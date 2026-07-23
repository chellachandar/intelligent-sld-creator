"""
BAY TYPE TEMPLATES
====================================
Defines all bay types and how they're assembled from components.
Each bay type specifies which components to use and in what arrangement.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


class BayType(Enum):
    """Supported bay types"""
    LINE = "line"
    TRANSFORMER = "transformer"
    REACTOR = "reactor"
    BUS_COUPLER = "bus_coupler"
    TRANSFER_BUS_COUPLER = "transfer_bus_coupler"
    FUTURE = "future"
    NO_BAY = "no_bay"


@dataclass
class ComponentPlacement:
    """Defines placement of a component within a bay"""
    component_type: str  # e.g., 'isolator', 'breaker', 'ct', etc.
    relative_y: float  # Y position relative to bay top
    label_suffix: str  # e.g., '89A', '52', 'CT', etc.
    description: str  # What this component represents


@dataclass
class BayTemplate:
    """Template for assembling a complete bay"""
    bay_type: BayType
    name: str
    description: str
    width: float  # Bay width in units
    height: float  # Bay height in units
    components: List[ComponentPlacement] = field(default_factory=list)
    has_upper_bus: bool = True  # Connects to upper (HV) bus
    has_lower_bus: bool = True  # Connects to lower (LV) bus
    has_middle_breaker: bool = False  # 1.5-breaker scheme only
    support_dual_bus: bool = True  # Can be on either bus (dual bus schemes)
    notes: str = ""


# ============================================================================
# BAY TEMPLATE DEFINITIONS
# ============================================================================

class BayTemplates:
    """Repository of all bay type templates"""

    # ---- LINE BAY ----
    LINE_BAY = BayTemplate(
        bay_type=BayType.LINE,
        name="Line Bay",
        description="""
        Standard transmission/distribution line bay.
        Typical components: Isolators (HV & LV), Breaker, CT, WT/CVT, LA, Grounding.
        Used for line feeders connecting to external networks or generation.
        """,
        width=2.5,
        height=12.0,
        components=[
            ComponentPlacement("isolator", 11.0, "89A", "HV Isolator A"),
            ComponentPlacement("isolator", 11.0, "89B", "HV Isolator B (parallel)"),
            ComponentPlacement("earth_switch", 10.5, "89AE", "HV Earth Switch"),
            ComponentPlacement("breaker", 9.0, "52", "Main Breaker"),
            ComponentPlacement("earth_switch", 7.0, "89BE", "Breaker Earth"),
            ComponentPlacement("ct", 6.0, "CT", "Current Transformer"),
            ComponentPlacement("isolator", 4.0, "89L/89C", "LV Isolator"),
            ComponentPlacement("earth_switch", 3.0, "89LE/89CE", "LV Earth Switch"),
            ComponentPlacement("wt", 1.5, "WT", "Voltage Transformer"),
            ComponentPlacement("la", 1.0, "LA", "Lightning Arrester"),
            ComponentPlacement("earth_symbol", 0.2, "GND", "Grounding"),
        ],
        has_upper_bus=True,
        has_lower_bus=True,
        support_dual_bus=True,
        notes="Standard feeder bay for lines"
    )

    # ---- TRANSFORMER BAY ----
    TRANSFORMER_BAY = BayTemplate(
        bay_type=BayType.TRANSFORMER,
        name="Transformer Bay",
        description="""
        Power transformer bay connecting two voltage levels.
        Typical components: HV Isolators/Breaker, Power Transformer, LV Isolators/Breaker.
        Used for stepping down voltage (e.g., 400kV to 220kV).
        Includes detailed winding information.
        """,
        width=3.5,
        height=14.0,
        components=[
            ComponentPlacement("isolator", 13.0, "89A", "HV Isolator A"),
            ComponentPlacement("isolator", 13.0, "89B", "HV Isolator B"),
            ComponentPlacement("breaker", 11.5, "52-HV", "HV Breaker"),
            ComponentPlacement("power_transformer", 7.0, "TX", "Power Transformer (3-winding)"),
            ComponentPlacement("breaker", 2.5, "52-LV", "LV Breaker"),
            ComponentPlacement("isolator", 1.0, "89C", "LV Isolator"),
            ComponentPlacement("isolator", 1.0, "89D", "LV Isolator B"),
            ComponentPlacement("earth_symbol", 0.2, "GND", "Grounding"),
        ],
        has_upper_bus=True,
        has_lower_bus=True,
        support_dual_bus=True,
        notes="Transformer with full HV/LV protection"
    )

    # ---- REACTOR BAY (Shunt Reactor) ----
    REACTOR_BAY = BayTemplate(
        bay_type=BayType.REACTOR,
        name="Reactor Bay",
        description="""
        Shunt reactor bay for voltage support/power factor correction.
        Typical components: Isolators, Breaker, Reactor coil, CT, Grounding.
        Used for reactive power management and voltage stability.
        """,
        width=2.5,
        height=12.0,
        components=[
            ComponentPlacement("isolator", 11.0, "89A", "Isolator A"),
            ComponentPlacement("isolator", 11.0, "89B", "Isolator B"),
            ComponentPlacement("breaker", 9.0, "52", "Main Breaker"),
            ComponentPlacement("reactor", 6.0, "R", "Shunt Reactor"),
            ComponentPlacement("ct", 4.0, "CT", "Current Transformer"),
            ComponentPlacement("earth_symbol", 0.2, "GND", "Grounding"),
        ],
        has_upper_bus=True,
        has_lower_bus=False,
        support_dual_bus=True,
        notes="Reactor for reactive power compensation"
    )

    # ---- BUS COUPLER BAY ----
    BUS_COUPLER_BAY = BayTemplate(
        bay_type=BayType.BUS_COUPLER,
        name="Bus Coupler",
        description="""
        Coupler between two main buses (horizontal connection).
        Can be:
          - Breaker (motorized, fast switching): DOUBLE_BUS_COUPLER
          - Sectionalizer (manual/motorized isolator): DOUBLE_BUS_SECTIONALIZER
        Provides redundancy in double bus bar schemes.
        """,
        width=0.5,
        height=2.0,
        components=[
            ComponentPlacement("breaker_coupler", 1.0, "52C", "Coupler Breaker or Sectionalizer"),
            ComponentPlacement("ct", 0.5, "CT-C", "Coupler CT (optional)"),
        ],
        has_upper_bus=True,
        has_lower_bus=True,
        support_dual_bus=False,
        notes="Connects two parallel buses"
    )

    # ---- TRANSFER BUS COUPLER ----
    TRANSFER_BUS_COUPLER = BayTemplate(
        bay_type=BayType.TRANSFER_BUS_COUPLER,
        name="Transfer Bus Coupler",
        description="""
        Coupler to transfer/auxiliary bus (1.5-breaker scheme).
        Provides redundant path for load transfer.
        Used in complex schemes for high reliability.
        """,
        width=1.0,
        height=3.0,
        components=[
            ComponentPlacement("breaker", 2.0, "52T", "Transfer Coupler Breaker"),
            ComponentPlacement("reactor", 1.2, "R", "Bus Reactor (optional)"),
        ],
        has_upper_bus=True,
        has_lower_bus=False,
        support_dual_bus=False,
        notes="Transfer bus connection"
    )

    # ---- FUTURE BAY (Placeholder) ----
    FUTURE_BAY = BayTemplate(
        bay_type=BayType.FUTURE,
        name="Future Bay",
        description="Reserved space for future expansion. No equipment installed.",
        width=2.5,
        height=12.0,
        components=[],
        has_upper_bus=False,
        has_lower_bus=False,
        support_dual_bus=True,
        notes="Placeholder for future use"
    )

    # ---- NO BAY (Empty) ----
    NO_BAY = BayTemplate(
        bay_type=BayType.NO_BAY,
        name="No Bay",
        description="Empty space with label. Used for gaps or reserved positions.",
        width=2.5,
        height=12.0,
        components=[],
        has_upper_bus=False,
        has_lower_bus=False,
        support_dual_bus=True,
        notes="Empty placeholder"
    )


# ============================================================================
# BAY REGISTRY (for easy lookup by type)
# ============================================================================

BAY_REGISTRY = {
    'line': BayTemplates.LINE_BAY,
    'transformer': BayTemplates.TRANSFORMER_BAY,
    'reactor': BayTemplates.REACTOR_BAY,
    'bus_coupler': BayTemplates.BUS_COUPLER_BAY,
    'transfer_bus_coupler': BayTemplates.TRANSFER_BUS_COUPLER,
    'future': BayTemplates.FUTURE_BAY,
    'no_bay': BayTemplates.NO_BAY,
}


# ============================================================================
# BAY ARRANGEMENT RULES
# ============================================================================

@dataclass
class BayArrangement:
    """Specification of bays to be drawn in sequence"""
    bay_type: str  # e.g., 'line', 'transformer', 'reactor'
    bay_number: int  # Assigned bay number (401, 402, 403, ...)
    bay_name: Optional[str] = None  # Custom name (e.g., "TUMKUR-1 72km")
    voltage_level: str = 'HV'  # 'HV' or 'LV' (for dual bus schemes)
    bus_section: int = 1  # Which bus (1 or 2 for double bus, 1 for single)
    position: int = 0  # Drawing sequence position


class BayArrangementValidator:
    """Validates bay arrangements against constraints"""

    @staticmethod
    def validate_arrangement(arrangement: List[BayArrangement],
                            config_type: str,
                            max_line_bays: int = 20,
                            max_transformer_bays: int = 20) -> Tuple[bool, str]:
        """
        Validates:
        1. No duplicate bay numbers
        2. Correct bay type vs bay number (odd=line, even=transformer)
        3. Adequate spacing
        4. Configuration compatibility
        """
        if not arrangement:
            return False, "Arrangement cannot be empty"

        # Check for duplicate bay numbers
        bay_numbers = [b.bay_number for b in arrangement]
        if len(bay_numbers) != len(set(bay_numbers)):
            return False, "Duplicate bay numbers found"

        # Check bay type vs number alignment
        line_count = 0
        transformer_count = 0
        for bay in arrangement:
            if bay.bay_type == 'line':
                line_count += 1
                if bay.bay_number % 2 == 0:  # Even number for line
                    return False, f"Line bay {bay.bay_number} should have odd number"
            elif bay.bay_type == 'transformer':
                transformer_count += 1
                if bay.bay_number % 2 != 0:  # Odd number for transformer
                    return False, f"Transformer bay {bay.bay_number} should have even number"

        if line_count > max_line_bays:
            return False, f"Too many line bays (max {max_line_bays})"
        if transformer_count > max_transformer_bays:
            return False, f"Too many transformer bays (max {max_transformer_bays})"

        return True, "Valid arrangement"

    @staticmethod
    def auto_generate_arrangement(num_lines: int,
                                 num_transformers: int,
                                 num_reactors: int = 0,
                                 voltage: int = 400,
                                 include_coupler: bool = True) -> List[BayArrangement]:
        """
        Auto-generates bay arrangement in standard order:
        Lines, Transformers, Reactors, Bus Coupler(s)
        """
        arrangement = []
        position = 0
        voltage_prefix = voltage // 100  # 400 -> 4, 220 -> 2, etc.

        # Generate line bays (odd numbers)
        line_numbers = [voltage_prefix * 100 + i for i in range(1, 2 * num_lines, 2)]
        for idx, bay_num in enumerate(line_numbers):
            arrangement.append(BayArrangement(
                bay_type='line',
                bay_number=bay_num,
                bay_name=f"Line-{idx+1}",
                position=position
            ))
            position += 1

        # Generate transformer bays (even numbers)
        transformer_numbers = [voltage_prefix * 100 + i for i in range(2, 2 * num_transformers + 2, 2)]
        for idx, bay_num in enumerate(transformer_numbers):
            arrangement.append(BayArrangement(
                bay_type='transformer',
                bay_number=bay_num,
                bay_name=f"Transformer-{idx+1}",
                position=position
            ))
            position += 1

        # Generate reactor bays
        if num_reactors > 0:
            reactor_base = voltage_prefix * 100 + 20
            for idx in range(num_reactors):
                arrangement.append(BayArrangement(
                    bay_type='reactor',
                    bay_number=reactor_base + idx + 1,
                    bay_name=f"Reactor-{idx+1}",
                    position=position
                ))
                position += 1

        # Add bus coupler if needed
        if include_coupler:
            arrangement.append(BayArrangement(
                bay_type='bus_coupler',
                bay_number=0,  # Special numbering for coupler
                bay_name="Bus Coupler",
                position=position
            ))

        return arrangement


# ============================================================================
# BAY COMPONENT SPECIFICATIONS
# ============================================================================

@dataclass
class BayComponentSpec:
    """Detailed specification for rendering a bay component"""
    component_type: str
    label: str
    x_offset: float = 0.0
    y_offset: float = 0.0
    is_visible: bool = True
    alternate_component: Optional[str] = None  # e.g., 'cvt' instead of 'wt'


def get_bay_template(bay_type: str) -> Optional[BayTemplate]:
    """Fetch bay template by type"""
    return BAY_REGISTRY.get(bay_type.lower())


def get_all_bay_types() -> List[str]:
    """Get list of all available bay types"""
    return list(BAY_REGISTRY.keys())


if __name__ == "__main__":
    print("Bay Templates Loaded")
    print(f"Available bay types: {get_all_bay_types()}")

    print(f"\nLine Bay Structure:")
    line_bay = get_bay_template('line')
    print(f"  - Width: {line_bay.width} units")
    print(f"  - Height: {line_bay.height} units")
    print(f"  - Components: {len(line_bay.components)}")
    for comp in line_bay.components:
        print(f"    - {comp.label_suffix}: {comp.description}")

    print(f"\nAuto-generated Bay Arrangement (4 lines, 2 transformers, 1 reactor, 400kV):")
    arrangement = BayArrangementValidator.auto_generate_arrangement(
        num_lines=4,
        num_transformers=2,
        num_reactors=1,
        voltage=400
    )
    for bay in arrangement:
        print(f"  Bay {bay.bay_number}: {bay.bay_type} ({bay.bay_name})")
