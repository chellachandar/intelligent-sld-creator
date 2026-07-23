"""
BUS CONFIGURATION TEMPLATES
====================================
Defines supported bus schemes and their properties.
Double Bus Bar with Coupler, Double Bus Bar with Sectionalizer, Single Bus
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class BusScheme(Enum):
    """Supported bus configurations"""
    SINGLE_BUS = "single_bus"
    DOUBLE_BUS_COUPLER = "double_bus_coupler"
    DOUBLE_BUS_SECTIONALIZER = "double_bus_sectionalizer"


@dataclass
class BusConfiguration:
    """Configuration template for bus arrangements"""
    scheme_type: BusScheme
    name: str
    description: str
    num_buses: int  # 1 or 2
    bus_names: List[str]
    has_coupler: bool
    coupler_type: str  # 'breaker', 'sectionalizer', 'none'
    bus_spacing: float  # Vertical distance between buses
    feeder_connection_mode: str  # 'single' or 'dual'
    supports_multi_voltage: bool
    layout_type: str  # 'horizontal' or 'vertical'


# ============================================================================
# PREDEFINED CONFIGURATIONS
# ============================================================================

class BusConfigurations:
    """Repository of all supported bus configurations"""

    # ---- SINGLE BUS ----
    SINGLE_BUS = BusConfiguration(
        scheme_type=BusScheme.SINGLE_BUS,
        name="Single Bus",
        description="Single main bus with all feeders connected to one bus",
        num_buses=1,
        bus_names=["MAIN BUS"],
        has_coupler=False,
        coupler_type='none',
        bus_spacing=0.0,
        feeder_connection_mode='single',
        supports_multi_voltage=False,
        layout_type='horizontal'
    )

    # ---- DOUBLE BUS WITH COUPLER ----
    DOUBLE_BUS_COUPLER = BusConfiguration(
        scheme_type=BusScheme.DOUBLE_BUS_COUPLER,
        name="Double Bus Bar with Coupler",
        description="""
        Two independent main buses with bus coupler breaker.
        Each feeder can be switched to either bus (redundancy).
        Coupler breaker can isolate buses when needed.
        Highly reliable for critical substations.
        """,
        num_buses=2,
        bus_names=["MAIN BUS-1", "MAIN BUS-2"],
        has_coupler=True,
        coupler_type='breaker',  # Motorized breaker
        bus_spacing=10.0,  # units (vertical distance)
        feeder_connection_mode='dual',  # Feeders can connect to either bus
        supports_multi_voltage=True,
        layout_type='horizontal'
    )

    # ---- DOUBLE BUS WITH SECTIONALIZER ----
    DOUBLE_BUS_SECTIONALIZER = BusConfiguration(
        scheme_type=BusScheme.DOUBLE_BUS_SECTIONALIZER,
        name="Double Bus Bar with Sectionalizer",
        description="""
        Two independent main buses with sectionalizer (isolator).
        Each feeder can be switched to either bus.
        Sectionalizer is manual or motor-driven (cheaper than breaker).
        Used when coupler breaker redundancy not needed.
        """,
        num_buses=2,
        bus_names=["MAIN BUS-1", "MAIN BUS-2"],
        has_coupler=True,
        coupler_type='sectionalizer',  # Manual or motorized isolator
        bus_spacing=10.0,
        feeder_connection_mode='dual',
        supports_multi_voltage=True,
        layout_type='horizontal'
    )


# ============================================================================
# CONFIGURATION REGISTRY (for easy lookup)
# ============================================================================

CONFIG_REGISTRY = {
    'single_bus': BusConfigurations.SINGLE_BUS,
    'double_bus_coupler': BusConfigurations.DOUBLE_BUS_COUPLER,
    'double_bus_sectionalizer': BusConfigurations.DOUBLE_BUS_SECTIONALIZER,
}


# ============================================================================
# CONFIGURATION PARAMETERS & CONSTRAINTS
# ============================================================================

@dataclass
class ConfigConstraints:
    """Hardware and design constraints for each configuration"""
    config_type: str
    max_feeders: int
    max_line_bays: int
    max_transformer_bays: int
    max_reactor_bays: int
    max_bus_couplers: int
    min_voltage: float  # kV
    max_voltage: float  # kV
    recommended_spacing: float  # Bay spacing
    breaker_redundancy: bool


CONSTRAINTS = {
    'single_bus': ConfigConstraints(
        config_type='single_bus',
        max_feeders=30,
        max_line_bays=20,
        max_transformer_bays=20,
        max_reactor_bays=5,
        max_bus_couplers=0,
        min_voltage=11,
        max_voltage=400,
        recommended_spacing=2.5,
        breaker_redundancy=False
    ),
    'double_bus_coupler': ConfigConstraints(
        config_type='double_bus_coupler',
        max_feeders=40,
        max_line_bays=20,
        max_transformer_bays=20,
        max_reactor_bays=5,
        max_bus_couplers=2,
        min_voltage=11,
        max_voltage=400,
        recommended_spacing=3.0,
        breaker_redundancy=True
    ),
    'double_bus_sectionalizer': ConfigConstraints(
        config_type='double_bus_sectionalizer',
        max_feeders=40,
        max_line_bays=20,
        max_transformer_bays=20,
        max_reactor_bays=5,
        max_bus_couplers=2,
        min_voltage=11,
        max_voltage=400,
        recommended_spacing=3.0,
        breaker_redundancy=False
    ),
}


# ============================================================================
# VOLTAGE & STYLING CONFIGURATION
# ============================================================================

@dataclass
class VoltageProfile:
    """Styling and layout rules per voltage level"""
    voltage: float  # kV
    region: str  # 'transmission', 'sub-transmission', 'distribution', 'LV'
    color_scheme: Dict[str, str]  # colors for this voltage
    font_size_adjustment: float  # multiplier
    symbol_size_adjustment: float
    line_width_adjustment: float
    typical_base_kv: float  # Reference base for calculations


VOLTAGE_PROFILES = {
    400: VoltageProfile(
        voltage=400,
        region='transmission',
        color_scheme={
            'bus': '#0066CC',
            'line': '#FF0000',
            'earth': '#00AA00',
            'secondary': '#0000FF',
            'text': '#000000'
        },
        font_size_adjustment=1.2,
        symbol_size_adjustment=1.2,
        line_width_adjustment=1.0,
        typical_base_kv=400
    ),
    220: VoltageProfile(
        voltage=220,
        region='sub-transmission',
        color_scheme={
            'bus': '#0099FF',
            'line': '#FF0000',
            'earth': '#00AA00',
            'secondary': '#0000FF',
            'text': '#000000'
        },
        font_size_adjustment=1.0,
        symbol_size_adjustment=1.0,
        line_width_adjustment=0.9,
        typical_base_kv=220
    ),
    132: VoltageProfile(
        voltage=132,
        region='sub-transmission',
        color_scheme={
            'bus': '#00CCFF',
            'line': '#FF3300',
            'earth': '#00AA00',
            'secondary': '#0000FF',
            'text': '#000000'
        },
        font_size_adjustment=0.9,
        symbol_size_adjustment=0.9,
        line_width_adjustment=0.8,
        typical_base_kv=132
    ),
    110: VoltageProfile(
        voltage=110,
        region='distribution',
        color_scheme={
            'bus': '#00CCFF',
            'line': '#FF3300',
            'earth': '#00AA00',
            'secondary': '#0000FF',
            'text': '#000000'
        },
        font_size_adjustment=0.85,
        symbol_size_adjustment=0.85,
        line_width_adjustment=0.75,
        typical_base_kv=110
    ),
    66: VoltageProfile(
        voltage=66,
        region='distribution',
        color_scheme={
            'bus': '#00FF99',
            'line': '#FF3300',
            'earth': '#00AA00',
            'secondary': '#0000FF',
            'text': '#000000'
        },
        font_size_adjustment=0.8,
        symbol_size_adjustment=0.8,
        line_width_adjustment=0.7,
        typical_base_kv=66
    ),
    33: VoltageProfile(
        voltage=33,
        region='distribution',
        color_scheme={
            'bus': '#99FF00',
            'line': '#FF3300',
            'earth': '#00AA00',
            'secondary': '#0000FF',
            'text': '#000000'
        },
        font_size_adjustment=0.75,
        symbol_size_adjustment=0.75,
        line_width_adjustment=0.65,
        typical_base_kv=33
    ),
    11: VoltageProfile(
        voltage=11,
        region='LV distribution',
        color_scheme={
            'bus': '#FFFF00',
            'line': '#FF3300',
            'earth': '#00AA00',
            'secondary': '#0000FF',
            'text': '#000000'
        },
        font_size_adjustment=0.7,
        symbol_size_adjustment=0.7,
        line_width_adjustment=0.6,
        typical_base_kv=11
    ),
}


def get_voltage_profile(voltage: float) -> VoltageProfile:
    """Get styling profile for a given voltage"""
    if voltage in VOLTAGE_PROFILES:
        return VOLTAGE_PROFILES[voltage]
    else:
        # Return closest voltage profile
        closest = min(VOLTAGE_PROFILES.keys(), key=lambda x: abs(x - voltage))
        return VOLTAGE_PROFILES[closest]


# ============================================================================
# BAY NUMBERING SCHEME
# ============================================================================

class BayNumberingScheme:
    """Global bay numbering rules"""

    @staticmethod
    def get_line_bay_numbers(count: int, start: int = 1) -> List[int]:
        """
        Line bay numbers: 401, 403, 405, 407, ..., 439 (odd numbers)
        Args:
            count: Number of line bays needed
            start: Starting bay ID (e.g., 4 for 400kV = 401, 403, ...)
        Returns:
            List of odd bay numbers
        """
        base = start * 100
        return [base + i for i in range(1, 2 * count, 2)]

    @staticmethod
    def get_transformer_bay_numbers(count: int, start: int = 1) -> List[int]:
        """
        Transformer bay numbers: 402, 404, 406, ..., 440 (even numbers)
        Args:
            count: Number of transformer bays
            start: Starting bay ID
        Returns:
            List of even bay numbers
        """
        base = start * 100
        return [base + i for i in range(2, 2 * count + 2, 2)]

    @staticmethod
    def get_reactor_bay_numbers(count: int, start: int = 4) -> List[int]:
        """
        Reactor bay numbers: 421, 422, 423, ... (sequential from 421)
        Args:
            count: Number of reactor bays
            start: Starting decade (default 4 for 400kV = 421, 422, ...)
        Returns:
            List of sequential bay numbers
        """
        base = start * 100 + 20
        return [base + i for i in range(1, count + 1)]

    @staticmethod
    def validate_bay_count(config_type: str, line_count: int,
                          transformer_count: int, reactor_count: int) -> bool:
        """Validate bay counts against configuration constraints"""
        if config_type not in CONSTRAINTS:
            return False

        constraints = CONSTRAINTS[config_type]
        return (line_count <= constraints.max_line_bays and
                transformer_count <= constraints.max_transformer_bays and
                reactor_count <= constraints.max_reactor_bays)


if __name__ == "__main__":
    print("Configuration Templates Loaded")
    print(f"Available configurations: {list(CONFIG_REGISTRY.keys())}")
    print(f"\nDouble Bus Bar with Coupler Details:")
    config = BusConfigurations.DOUBLE_BUS_COUPLER
    print(f"  - Buses: {config.bus_names}")
    print(f"  - Coupler Type: {config.coupler_type}")
    print(f"  - Multi-voltage Support: {config.supports_multi_voltage}")

    print(f"\nBay Numbering Examples:")
    print(f"  Line bays (400kV): {BayNumberingScheme.get_line_bay_numbers(5, 4)}")
    print(f"  Transformer bays (400kV): {BayNumberingScheme.get_transformer_bay_numbers(5, 4)}")
    print(f"  Reactor bays (400kV): {BayNumberingScheme.get_reactor_bay_numbers(3, 4)}")
