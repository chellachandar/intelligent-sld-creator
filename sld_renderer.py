"""
MAIN SLD RENDERING ENGINE
====================================
Intelligent orchestrator that takes configuration + bay arrangement
and generates complete SLD diagrams (PDF/DXF).
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import ezdxf
from ezdxf.enums import TextEntityAlignment
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import io
import math

from config_components import ComponentDrawer, DRAWER_REGISTRY
from config_configurations import (
    BusConfiguration, BusConfigurations, BayNumberingScheme,
    get_voltage_profile, VOLTAGE_PROFILES
)
from config_bays import BayTemplate, BayArrangement, BayArrangementValidator, get_bay_template


# ============================================================================
# SLD GENERATION PARAMETERS
# ============================================================================

@dataclass
class SLDGenerationParams:
    """Parameters for SLD generation"""
    # Essential
    substation_name: str
    hv_voltage: float  # e.g., 400
    lv_voltage: Optional[float] = None  # e.g., 220 (None for single voltage)
    configuration: str = 'double_bus_coupler'  # Bus configuration type

    # Bay arrangement
    line_bay_count: int = 0
    transformer_bay_count: int = 0
    reactor_bay_count: int = 0
    bus_coupler_count: int = 1

    # Custom naming
    line_names: List[str] = None
    transformer_names: List[str] = None
    reactor_names: List[str] = None

    # Styling
    title_text: str = "POWERGRID CORPORATION OF INDIA LTD"
    show_legend: bool = True
    dpi: int = 300

    def __post_init__(self):
        if self.line_names is None:
            self.line_names = []
        if self.transformer_names is None:
            self.transformer_names = []
        if self.reactor_names is None:
            self.reactor_names = []


# ============================================================================
# SLD RENDERER
# ============================================================================

class SLDRenderer:
    """Intelligent SLD generation engine"""

    def __init__(self, params: SLDGenerationParams):
        self.params = params
        self.fig = None
        self.ax = None
        self.hv_profile = get_voltage_profile(params.hv_voltage)
        self.lv_profile = get_voltage_profile(params.lv_voltage) if params.lv_voltage else self.hv_profile

        # Configuration
        self.config = self._get_configuration()
        self.is_dual_voltage = params.lv_voltage is not None and params.lv_voltage != params.hv_voltage
        self.is_dual_bus = self.config.num_buses == 2

        # Layout parameters
        self.bus_y_hv = 15.0  # HV bus Y position
        self.bus_y_lv = 5.0 if self.is_dual_voltage else 15.0  # LV bus Y position
        self.bay_start_x = 3.0
        self.bay_spacing = 3.5
        self.page_margin = 2.0

        # Drawing state
        self.bays_drawn = []
        self.components_count = 0

    def _get_configuration(self) -> BusConfiguration:
        """Get bus configuration from type string"""
        if self.params.configuration == 'double_bus_coupler':
            return BusConfigurations.DOUBLE_BUS_COUPLER
        elif self.params.configuration == 'double_bus_sectionalizer':
            return BusConfigurations.DOUBLE_BUS_SECTIONALIZER
        else:
            return BusConfigurations.SINGLE_BUS

    def _calculate_page_size(self) -> Tuple[float, float]:
        """Calculate figure size based on bay count"""
        total_bays = (self.params.line_bay_count +
                     self.params.transformer_bay_count +
                     self.params.reactor_bay_count +
                     self.params.bus_coupler_count)

        width = max(12, total_bays * self.bay_spacing)
        height = 18.0 if self.is_dual_voltage else 12.0

        return width, height

    def _generate_bay_arrangement(self) -> List[BayArrangement]:
        """Generate bay arrangement based on parameters"""
        arrangement = BayArrangementValidator.auto_generate_arrangement(
            num_lines=self.params.line_bay_count,
            num_transformers=self.params.transformer_bay_count,
            num_reactors=self.params.reactor_bay_count,
            voltage=int(self.params.hv_voltage),
            include_coupler=self.params.bus_coupler_count > 0
        )
        return arrangement

    def _draw_bus_section(self):
        """Draw bus bars (main and optional second bus)"""
        width, _ = self._calculate_page_size()
        bus_end_x = self.bay_start_x + width - self.page_margin

        # HV Bus
        color = self.hv_profile.color_scheme['bus']
        self.ax.plot([self.bay_start_x, bus_end_x], [self.bus_y_hv, self.bus_y_hv],
                    color=color, linewidth=2.0, label='HV Bus (400kV)')

        # Label HV Bus
        label_x = self.page_margin
        self.ax.text(label_x, self.bus_y_hv + 0.5, f"{int(self.params.hv_voltage)} kV - BUS 1",
                    fontsize=12, fontweight='bold', color=color)

        # LV Bus (if dual voltage)
        if self.is_dual_voltage:
            color_lv = self.lv_profile.color_scheme['bus']
            self.ax.plot([self.bay_start_x, bus_end_x], [self.bus_y_lv, self.bus_y_lv],
                        color=color_lv, linewidth=2.0, label=f'LV Bus ({int(self.params.lv_voltage)}kV)')

            label_y = self.bus_y_lv - 0.8
            self.ax.text(label_x, label_y, f"{int(self.params.lv_voltage)} kV - BUS 2",
                        fontsize=12, fontweight='bold', color=color_lv)

        # Second bus (for double bus bar)
        if self.is_dual_bus and not self.is_dual_voltage:
            # Two buses at different heights, same voltage
            bus_y_2 = self.bus_y_hv - 8.0
            color = self.hv_profile.color_scheme['bus']
            self.ax.plot([self.bay_start_x, bus_end_x], [bus_y_2, bus_y_2],
                        color=color, linewidth=2.0)

            label_y = bus_y_2 - 0.8
            self.ax.text(label_x, label_y, f"{int(self.params.hv_voltage)} kV - BUS 2",
                        fontsize=12, fontweight='bold', color=color)

            self.bus_y_lv = bus_y_2

    def _draw_bay(self, arrangement: BayArrangement, x_pos: float):
        """Draw a complete bay based on template"""
        bay_template = get_bay_template(arrangement.bay_type)
        if not bay_template:
            return

        # Get component drawer
        drawer = ComponentDrawer()

        # Draw vertical connections to HV bus
        if bay_template.has_upper_bus:
            color = self.hv_profile.color_scheme['line']
            self.ax.plot([x_pos, x_pos], [self.bus_y_hv, self.bus_y_hv - 1],
                        color=color, linewidth=0.8)

        # Draw components based on template
        for comp in bay_template.components:
            y_pos = self.bus_y_hv - comp.relative_y

            if comp.component_type in DRAWER_REGISTRY:
                draw_func = DRAWER_REGISTRY[comp.component_type]
                draw_func(self.ax, x_pos, y_pos, label=comp.label_suffix)
                self.components_count += 1

        # Draw connection to LV bus if applicable
        if bay_template.has_lower_bus and self.is_dual_voltage:
            color = self.lv_profile.color_scheme['line']
            self.ax.plot([x_pos, x_pos], [bay_template.height - self.bus_y_hv, self.bus_y_lv],
                        color=color, linewidth=0.8)

        # Draw bay label
        label_y = self.bus_y_hv + 1.5
        bay_label = f"{arrangement.bay_number}\n({arrangement.bay_type})"
        if arrangement.bay_name:
            bay_label += f"\n{arrangement.bay_name}"

        self.ax.text(x_pos, label_y, bay_label,
                    fontsize=10, ha='center', va='bottom',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        self.bays_drawn.append(arrangement)

    def _draw_all_bays(self):
        """Draw all bays based on arrangement"""
        arrangement = self._generate_bay_arrangement()

        for idx, bay in enumerate(arrangement):
            x_pos = self.bay_start_x + idx * self.bay_spacing
            self._draw_bay(bay, x_pos)

    def _add_title_and_info(self):
        """Add title, substation name, and other information"""
        width, _ = self._calculate_page_size()
        center_x = self.bay_start_x + width / 2.5

        # Company/Grid title
        self.ax.text(center_x, 20, self.params.title_text,
                    fontsize=18, fontweight='bold', ha='center',
                    color=self.hv_profile.color_scheme['text'])

        # Substation name
        self.ax.text(center_x, 18.5, self.params.substation_name,
                    fontsize=16, fontweight='bold', ha='center',
                    color=self.hv_profile.color_scheme['text'])

        # Date and info
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        info_text = f"Generated: {date_str}"
        self.ax.text(center_x, 17.5, info_text,
                    fontsize=10, ha='center', style='italic',
                    color=self.hv_profile.color_scheme['text'])

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Generate complete SLD diagram"""
        # Create figure
        width, height = self._calculate_page_size()
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=100)

        # Draw components in order
        self._draw_bus_section()
        self._draw_all_bays()
        self._add_title_and_info()

        # Formatting
        self.ax.set_xlim(0, width + 2)
        self.ax.set_ylim(-2, height)
        self.ax.axis('off')
        self.fig.tight_layout()

        return self.fig, self.ax

    def export_pdf(self, filepath: str):
        """Export SLD to PDF"""
        if self.fig is None:
            self.render()

        self.fig.savefig(filepath, format='pdf', dpi=self.params.dpi,
                        bbox_inches='tight', facecolor='white')
        print(f"PDF exported: {filepath}")

    def export_dxf(self, filepath: str):
        """Export SLD to DXF (AutoCAD format)"""
        if self.fig is None:
            self.render()

        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        # Extract data from matplotlib axes and convert to DXF
        # This is a simplified version - full implementation would map all patches/lines

        # Draw bus lines
        width, _ = self._calculate_page_size()
        bus_end_x = self.bay_start_x + width

        # HV Bus line
        msp.add_line((self.bay_start_x, self.bus_y_hv),
                    (bus_end_x, self.bus_y_hv),
                    dxfattribs={'color': 1, 'lineweight': 0.5})  # Red

        if self.is_dual_voltage:
            # LV Bus line
            msp.add_line((self.bay_start_x, self.bus_y_lv),
                        (bus_end_x, self.bus_y_lv),
                        dxfattribs={'color': 3, 'lineweight': 0.5})  # Green

        # Add title
        title = msp.add_text(self.params.title_text, dxfattribs={'height': 2.5})
        title.set_placement((self.bay_start_x + width / 2, self.bus_y_hv + 5))

        # Add substation name
        subname = msp.add_text(self.params.substation_name, dxfattribs={'height': 2.0})
        subname.set_placement((self.bay_start_x + width / 2, self.bus_y_hv + 3.5))

        # Save DXF
        doc.saveas(filepath)
        print(f"DXF exported: {filepath}")

    def get_summary(self) -> Dict:
        """Get summary of generated SLD"""
        return {
            'substation': self.params.substation_name,
            'hv_voltage': self.params.hv_voltage,
            'lv_voltage': self.params.lv_voltage,
            'configuration': self.params.configuration,
            'total_bays': len(self.bays_drawn),
            'line_bays': self.params.line_bay_count,
            'transformer_bays': self.params.transformer_bay_count,
            'reactor_bays': self.params.reactor_bay_count,
            'components_drawn': self.components_count,
            'is_dual_voltage': self.is_dual_voltage,
            'is_dual_bus': self.is_dual_bus,
        }


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def generate_sld(params: SLDGenerationParams) -> Tuple[plt.Figure, SLDRenderer]:
    """
    Convenience function to generate SLD.

    Usage:
        params = SLDGenerationParams(
            substation_name="YELAHANKA SS",
            hv_voltage=400,
            lv_voltage=220,
            line_bay_count=4,
            transformer_bay_count=2,
            reactor_bay_count=1
        )
        fig, renderer = generate_sld(params)
        renderer.export_pdf("output.pdf")
        renderer.export_dxf("output.dxf")
    """
    renderer = SLDRenderer(params)
    fig, ax = renderer.render()
    return fig, renderer


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("SLD RENDERER - Example Generation")
    print("=" * 60)

    params = SLDGenerationParams(
        substation_name="YELAHANKA SUBSTATION",
        hv_voltage=400,
        lv_voltage=220,
        configuration='double_bus_coupler',
        line_bay_count=4,
        transformer_bay_count=2,
        reactor_bay_count=1,
        bus_coupler_count=1,
        line_names=["TUMKUR-1 72km", "DEVANAHALLI", "Local-1", "Local-2"],
        transformer_names=["TX-1 (500MVA)", "TX-2 (315MVA)"],
        reactor_names=["Reactor-1"]
    )

    print(f"\nGenerating SLD with parameters:")
    print(f"  Substation: {params.substation_name}")
    print(f"  Voltage: {params.hv_voltage}kV / {params.lv_voltage}kV")
    print(f"  Configuration: {params.configuration}")
    print(f"  Bays: {params.line_bay_count} lines, {params.transformer_bay_count} transformers, {params.reactor_bay_count} reactors")

    try:
        fig, renderer = generate_sld(params)
        summary = renderer.get_summary()

        print(f"\nGeneration Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

        print(f"\n✓ SLD rendered successfully!")
        print(f"  Components drawn: {renderer.components_count}")
        print(f"  Bays created: {len(renderer.bays_drawn)}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
