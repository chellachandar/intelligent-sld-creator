"""
GLOBAL COMPONENT LIBRARY
====================================
Defines all electrical components used in SLD generation.
Each component is defined once, used everywhere.
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Arc
import math

# ============================================================================
# COMPONENT BASE CLASS
# ============================================================================

@dataclass
class ComponentProperties:
    """Properties for any electrical component"""
    name: str
    symbol_type: str  # 'isolator', 'breaker', 'ct', 'vt', 'la', 'reactor', etc.
    height: float = 0.8  # units
    width: float = 0.3
    label_offset_x: float = 0.3
    label_offset_y: float = 0.2
    line_color: str = 'red'
    fill_color: str = 'none'
    line_width: float = 0.5
    description: str = ""


# ============================================================================
# COMPONENT DEFINITIONS (GLOBAL)
# ============================================================================

class ComponentLibrary:
    """Global repository of all electrical components"""

    # ---- ISOLATOR (Disconnector) ----
    ISOLATOR = ComponentProperties(
        name="Isolator",
        symbol_type="isolator",
        height=0.8,
        width=0.2,
        label_offset_x=0.25,
        label_offset_y=-0.3,
        line_color='red',
        line_width=0.5,
        description="Isolator/Disconnector (89A, 89B, 89C, 89D)"
    )

    # ---- CIRCUIT BREAKER ----
    BREAKER = ComponentProperties(
        name="Breaker",
        symbol_type="breaker",
        height=0.4,
        width=0.2,
        label_offset_x=0.3,
        label_offset_y=0.0,
        line_color='black',
        line_width=0.5,
        description="Circuit Breaker (52)"
    )

    # ---- BREAKER (Horizontal for Coupler) ----
    BREAKER_COUPLER = ComponentProperties(
        name="Breaker Coupler",
        symbol_type="breaker_coupler",
        height=0.2,
        width=0.4,
        label_offset_x=0.0,
        label_offset_y=0.4,
        line_color='red',
        line_width=0.5,
        description="Bus Coupler Breaker"
    )

    # ---- CURRENT TRANSFORMER (CT) ----
    CT = ComponentProperties(
        name="CT",
        symbol_type="ct",
        height=0.6,
        width=0.2,
        label_offset_x=-0.3,
        label_offset_y=0.0,
        line_color='blue',
        line_width=0.5,
        description="Current Transformer (CT, ACT, BCT)"
    )

    # ---- VOLTAGE TRANSFORMER (WT) ----
    WT = ComponentProperties(
        name="WT",
        symbol_type="wt",
        height=0.4,
        width=0.1,
        label_offset_x=-0.3,
        label_offset_y=0.0,
        line_color='red',
        line_width=0.5,
        description="Voltage Transformer (WT)"
    )

    # ---- CAPACITIVE VOLTAGE TRANSFORMER (CVT) ----
    CVT = ComponentProperties(
        name="CVT",
        symbol_type="cvt",
        height=1.5,  # Complex symbol, taller
        width=0.4,
        label_offset_x=0.4,
        label_offset_y=-0.3,
        line_color='red',
        line_width=0.5,
        description="Capacitive Voltage Transformer (CVT)"
    )

    # ---- LIGHTNING ARRESTER (LA) ----
    LA = ComponentProperties(
        name="LA",
        symbol_type="la",
        height=0.3,
        width=0.3,
        label_offset_x=-0.5,
        label_offset_y=-0.4,
        line_color='green',
        line_width=0.5,
        description="Lightning Arrester (LA)"
    )

    # ---- REACTOR (Shunt Reactor) ----
    REACTOR = ComponentProperties(
        name="Reactor",
        symbol_type="reactor",
        height=0.6,
        width=0.2,
        label_offset_x=-0.45,
        label_offset_y=-0.8,
        line_color='red',
        line_width=0.5,
        description="Shunt Reactor"
    )

    # ---- POWER TRANSFORMER (for transformer bays) ----
    POWER_TRANSFORMER = ComponentProperties(
        name="Power Transformer",
        symbol_type="power_transformer",
        height=1.2,
        width=0.8,
        label_offset_x=-0.5,
        label_offset_y=-0.8,
        line_color='red',
        line_width=0.5,
        description="Power Transformer (3-winding shown)"
    )

    # ---- EARTH/GROUNDING SWITCH ----
    EARTH_SWITCH = ComponentProperties(
        name="Earth Switch",
        symbol_type="earth_switch",
        height=0.5,
        width=0.2,
        label_offset_x=0.25,
        label_offset_y=-0.3,
        line_color='red',
        line_width=0.5,
        description="Earth/Grounding Switch (89E, 89AE)"
    )

    # ---- EARTH/GROUNDING SYMBOL ----
    EARTH_SYMBOL = ComponentProperties(
        name="Earth Symbol",
        symbol_type="earth_symbol",
        height=0.3,
        width=0.25,
        label_offset_x=0.0,
        label_offset_y=-0.5,
        line_color='green',
        line_width=0.5,
        description="Ground/Earth (GND)"
    )


# ============================================================================
# COMPONENT DRAWING FUNCTIONS
# ============================================================================

class ComponentDrawer:
    """Draws individual components on matplotlib axes"""

    @staticmethod
    def draw_isolator(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw isolator symbol (two circles + diagonal break line)"""
        if props is None:
            props = ComponentLibrary.ISOLATOR

        # Two circles
        circle1_y = y + 0.2
        circle2_y = y - 0.2
        ax.plot([x, x], [circle1_y - 0.1, circle1_y + 0.1],
                color=props.line_color, linewidth=props.line_width)
        ax.plot([x, x], [circle2_y - 0.1, circle2_y + 0.1],
                color=props.line_color, linewidth=props.line_width)

        # Diagonal break line
        ax.plot([x - 0.05, x + 0.05], [circle1_y - 0.15, circle2_y + 0.15],
                color=props.line_color, linewidth=props.line_width)

        # Vertical connections
        ax.plot([x, x], [y + 0.4, circle1_y + 0.1],
                color=props.line_color, linewidth=props.line_width)
        ax.plot([x, x], [circle2_y - 0.1, y - 1.2],
                color=props.line_color, linewidth=props.line_width)

        if label:
            ax.text(x + props.label_offset_x, y + props.label_offset_y, label,
                   fontsize=9, ha='center', color=props.line_color)

    @staticmethod
    def draw_breaker(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw circuit breaker symbol (rectangle with connections)"""
        if props is None:
            props = ComponentLibrary.BREAKER

        # Rectangle
        rect = Rectangle((x - props.width/2, y - props.height/2),
                        props.width, props.height,
                        fill=False, edgecolor=props.line_color,
                        linewidth=props.line_width)
        ax.add_patch(rect)

        # Vertical connections
        ax.plot([x, x], [y + props.height/2, y + 1],
                color=props.line_color, linewidth=props.line_width)
        ax.plot([x, x], [y - props.height/2, y - 1],
                color=props.line_color, linewidth=props.line_width)

        if label:
            ax.text(x + props.label_offset_x, y + props.label_offset_y, label,
                   fontsize=9, ha='center', color=props.line_color)

    @staticmethod
    def draw_breaker_coupler(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw horizontal bus coupler breaker"""
        if props is None:
            props = ComponentLibrary.BREAKER_COUPLER

        # Horizontal rectangle
        rect = Rectangle((x - props.width/2, y - props.height/2),
                        props.width, props.height,
                        fill=False, edgecolor=props.line_color,
                        linewidth=props.line_width)
        ax.add_patch(rect)

        # Horizontal connections
        ax.plot([x - props.width/2 - 0.4, x - props.width/2], [y, y],
                color=props.line_color, linewidth=props.line_width)
        ax.plot([x + props.width/2, x + props.width/2 + 0.4], [y, y],
                color=props.line_color, linewidth=props.line_width)

        if label:
            ax.text(x, y + props.label_offset_y, label,
                   fontsize=9, ha='center', color=props.line_color)

    @staticmethod
    def draw_ct(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw Current Transformer (two semicircles)"""
        if props is None:
            props = ComponentLibrary.CT

        spacing = 0.75

        # Upper semicircle
        arc1 = Arc((x + 0.03, y - spacing/4), width=0.2, height=0.4,
                  angle=0, theta1=80, theta2=280,
                  color=props.line_color, linewidth=props.line_width)
        ax.add_patch(arc1)

        # Lower semicircle
        arc2 = Arc((x + 0.03, y + spacing/4), width=0.2, height=0.4,
                  angle=0, theta1=80, theta2=280,
                  color=props.line_color, linewidth=props.line_width)
        ax.add_patch(arc2)

        # Vertical connections
        ax.plot([x, x], [y + 0.5, y - 0.5],
                color=props.line_color, linewidth=props.line_width)

        if label:
            ax.text(x + props.label_offset_x, y + props.label_offset_y, label,
                   fontsize=9, ha='center', color=props.line_color)

    @staticmethod
    def draw_wt(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw Voltage Transformer (arc + line)"""
        if props is None:
            props = ComponentLibrary.WT

        # Arc
        arc = Arc((x, y - 0.15), width=0.2, height=0.4,
                 angle=0, theta1=90, theta2=360,
                 color=props.line_color, linewidth=props.line_width)
        ax.add_patch(arc)

        # Horizontal line
        ax.plot([x, x + 0.1], [y - 0.15, y - 0.15],
                color=props.line_color, linewidth=props.line_width)

        # Vertical connections
        ax.plot([x, x], [y + 0.3, y - 0.5],
                color=props.line_color, linewidth=props.line_width)

        if label:
            ax.text(x + props.label_offset_x, y + props.label_offset_y, label,
                   fontsize=9, ha='center', color=props.line_color)

    @staticmethod
    def draw_reactor(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw Reactor (multiple arc segments)"""
        if props is None:
            props = ComponentLibrary.REACTOR

        # Four arc segments
        for i in range(4):
            arc = Arc((x - 0.025, y - (i * 0.25)), width=0.2, height=0.4,
                     angle=0, theta1=60, theta2=300,
                     color=props.line_color, linewidth=props.line_width)
            ax.add_patch(arc)

        # Vertical connections
        ax.plot([x, x], [y + 0.3, y - 1.3],
                color=props.line_color, linewidth=props.line_width)

        if label:
            ax.text(x + props.label_offset_x, y + props.label_offset_y, label,
                   fontsize=9, ha='center', color=props.line_color)

    @staticmethod
    def draw_la(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw Lightning Arrester (line with parallel earth)"""
        if props is None:
            props = ComponentLibrary.LA

        # Horizontal line connection
        ax.plot([x - 0.9, x], [y, y],
                color=props.line_color, linewidth=props.line_width)

        # Earth parallel lines (green)
        ax.plot([x - 0.9, x - 0.9], [y + 0.2, y - 0.2],
                color='green', linewidth=props.line_width)
        ax.plot([x - 0.95, x - 0.95], [y + 0.15, y - 0.15],
                color='green', linewidth=props.line_width)
        ax.plot([x - 1.0, x - 1.0], [y + 0.1, y - 0.1],
                color='green', linewidth=props.line_width)

        if label:
            ax.text(x - 0.5, y - 0.5, label,
                   fontsize=9, ha='center', color=props.line_color)

    @staticmethod
    def draw_earth_symbol(ax, x: float, y: float, label: str = "", props: ComponentProperties = None):
        """Draw earth/grounding symbol (three horizontal lines)"""
        if props is None:
            props = ComponentLibrary.EARTH_SYMBOL

        # Three decreasing length horizontal lines
        ax.plot([x - 0.125, x + 0.125], [y + 0.1, y + 0.1],
                color='green', linewidth=props.line_width)
        ax.plot([x - 0.1, x + 0.1], [y, y],
                color='green', linewidth=props.line_width)
        ax.plot([x - 0.075, x + 0.075], [y - 0.1, y - 0.1],
                color='green', linewidth=props.line_width)

        # Vertical connection
        ax.plot([x, x], [y + 0.2, y + 0.1],
                color='green', linewidth=props.line_width)

    @staticmethod
    def draw_power_transformer(ax, x: float, y: float, label: str = "",
                              hv_label: str = "HV", lv_label: str = "LV",
                              props: ComponentProperties = None):
        """Draw Power Transformer (primary & secondary windings)"""
        if props is None:
            props = ComponentLibrary.POWER_TRANSFORMER

        # Primary winding (HV, red)
        arc1_hv = Arc((x - 0.2, y + 0.3), width=0.2, height=0.4,
                      angle=0, theta1=0, theta2=360,
                      color=props.line_color, linewidth=props.line_width)
        ax.add_patch(arc1_hv)

        # Secondary winding (LV, blue)
        arc1_lv = Arc((x + 0.2, y + 0.3), width=0.2, height=0.4,
                      angle=0, theta1=0, theta2=360,
                      color='blue', linewidth=props.line_width)
        ax.add_patch(arc1_lv)

        # Tertiary winding (if needed, green)
        arc1_tert = Arc((x, y - 0.3), width=0.2, height=0.4,
                       angle=0, theta1=0, theta2=360,
                       color='green', linewidth=props.line_width)
        ax.add_patch(arc1_tert)

        # Connections
        ax.plot([x - 0.2, x - 0.2], [y + 0.7, y + 1.0],
                color=props.line_color, linewidth=props.line_width)
        ax.plot([x + 0.2, x + 0.2], [y + 0.7, y - 1.0],
                color='blue', linewidth=props.line_width)
        ax.plot([x, x], [y - 0.7, y - 1.0],
                color='green', linewidth=props.line_width)

        if label:
            ax.text(x - 0.5, y - 0.8, label, fontsize=9, ha='center')
        if hv_label:
            ax.text(x - 0.2, y + 1.2, hv_label, fontsize=8, ha='center', color=props.line_color)
        if lv_label:
            ax.text(x + 0.2, y - 1.2, lv_label, fontsize=8, ha='center', color='blue')


# ============================================================================
# COMPONENT REGISTRY (for easy access by name)
# ============================================================================

COMPONENT_REGISTRY = {
    'isolator': ComponentLibrary.ISOLATOR,
    'breaker': ComponentLibrary.BREAKER,
    'breaker_coupler': ComponentLibrary.BREAKER_COUPLER,
    'ct': ComponentLibrary.CT,
    'wt': ComponentLibrary.WT,
    'cvt': ComponentLibrary.CVT,
    'la': ComponentLibrary.LA,
    'reactor': ComponentLibrary.REACTOR,
    'power_transformer': ComponentLibrary.POWER_TRANSFORMER,
    'earth_switch': ComponentLibrary.EARTH_SWITCH,
    'earth_symbol': ComponentLibrary.EARTH_SYMBOL,
}


DRAWER_REGISTRY = {
    'isolator': ComponentDrawer.draw_isolator,
    'breaker': ComponentDrawer.draw_breaker,
    'breaker_coupler': ComponentDrawer.draw_breaker_coupler,
    'ct': ComponentDrawer.draw_ct,
    'wt': ComponentDrawer.draw_wt,
    'reactor': ComponentDrawer.draw_reactor,
    'la': ComponentDrawer.draw_la,
    'earth_symbol': ComponentDrawer.draw_earth_symbol,
    'power_transformer': ComponentDrawer.draw_power_transformer,
}


if __name__ == "__main__":
    print("Component Library Loaded")
    print(f"Available components: {list(COMPONENT_REGISTRY.keys())}")
