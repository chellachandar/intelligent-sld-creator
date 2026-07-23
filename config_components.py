"""
GLOBAL COMPONENT LIBRARY (v2)
=============================
All electrical symbols defined ONCE, reused by every bay type, every
configuration, every voltage. Geometry ported from the proven original
Final_DXF.py engine (YELAHANKA reference output).

Colors use NAMED values (red/green/blue/black) so the DXF exporter maps
them to exact AutoCAD colors.
"""

from dataclasses import dataclass
from matplotlib.patches import Rectangle, Polygon, Arc

# Global stroke weights
LW = 0.9        # symbol line width
BUS_LW = 2.2    # bus bar line width


@dataclass
class ComponentProperties:
    """Metadata for a component (for docs/UI listings)."""
    name: str
    symbol_type: str
    description: str = ""


COMPONENT_CATALOG = [
    ComponentProperties("Isolator", "isolator", "Disconnector 89A/89B/89L/89T/89R"),
    ComponentProperties("Horizontal Isolator", "isolator_h", "Bus sectionalizer isolator"),
    ComponentProperties("Circuit Breaker", "breaker", "52"),
    ComponentProperties("Bus Coupler Breaker", "breaker_coupler", "52BC"),
    ComponentProperties("Earth Switch", "earth_switch", "89AE/89BE/89LE"),
    ComponentProperties("Current Transformer", "ct", "CT"),
    ComponentProperties("Voltage Transformer", "wt", "WT"),
    ComponentProperties("Capacitive VT", "cvt", "CVT"),
    ComponentProperties("Lightning Arrester", "la", "LA"),
    ComponentProperties("Interconnecting Transformer", "ict", "ICT"),
    ComponentProperties("Shunt Reactor", "reactor", "Reactor"),
    ComponentProperties("Earth Symbol", "earth", "Grounding"),
    ComponentProperties("Line Arrow", "symbol", "Feeder termination"),
]


class ComponentDrawer:
    """All symbol drawing functions (global, reusable, proven geometry)."""

    # ---------------- BREAKERS ----------------
    @staticmethod
    def draw_breaker(ax, x, y, label, fs):
        ax.add_patch(Rectangle((x - 0.1, y - 0.2), 0.2, 0.4, fill=False,
                               edgecolor='black', linewidth=LW))
        ax.plot([x, x], [y + .2, y + 1], color='red', linewidth=LW)
        ax.plot([x, x], [y - .2, y - 1], color='red', linewidth=LW)
        ax.text(x + .25, y, label, fontsize=fs, ha='left', va='center')

    @staticmethod
    def draw_breaker_coupler(ax, x, y, label, fs):
        ax.add_patch(Rectangle((x - 0.1, y - 0.2), 0.2, 0.4, fill=False,
                               edgecolor='black', linewidth=LW))
        ax.plot([x - .45, x - .1], [y, y], color='red', linewidth=LW)
        ax.plot([x + .1, x + .45], [y, y], color='red', linewidth=LW)
        ax.text(x, y + .45, label, fontsize=fs, ha='center')

    # ---------------- ISOLATORS ----------------
    @staticmethod
    def draw_isolator(ax, x, y, label, fs):
        """Vertical isolator: stub, two contact circles, open blade, stub."""
        ax.plot([x, x], [y - .12, y + .4], color='red', linewidth=LW)
        ax.text(x + .12, y - .32, label, fontsize=fs, ha='left')
        ax.add_patch(Arc((x, y - 0.15), width=0.05, height=0.1,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.add_patch(Arc((x, y - 0.65), width=0.05, height=0.1,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.plot([x - .06, x + .06], [y - .58, y - .22], color='red', linewidth=LW)
        ax.plot([x, x], [y - .7, y - 1.2], color='red', linewidth=LW)

    @staticmethod
    def draw_isolator_h(ax, x, y, label, fs):
        """Horizontal isolator (bus sectionalizer)."""
        ax.add_patch(Arc((x - 0.25, y), width=0.1, height=0.05,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.add_patch(Arc((x + 0.25, y), width=0.1, height=0.05,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.plot([x - .2, x + .15], [y, y + .25], color='red', linewidth=LW)
        ax.text(x, y + .35, label, fontsize=fs, ha='center')

    # ---------------- EARTH SWITCH ----------------
    @staticmethod
    def earth_sh(ax, x, y, label, fs):
        """Earth switch hanging left of a point on the stem."""
        y = y - .2
        ax.plot([x, x - .2], [y - .6, y - .6], color='red', linewidth=LW)
        ax.add_patch(Arc((x - .2, y - .45 - 0.15), width=0.05, height=0.1,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.add_patch(Arc((x - .35, y - .45 - 0.15), width=0.05, height=0.1,
                         angle=0, theta1=0, theta2=360, color='green', linewidth=LW))
        ax.plot([x - .2, x - .35], [y - .35, y - .6], color='green', linewidth=LW)
        ax.plot([x - .35, x - .5], [y - .6, y - .6], color='green', linewidth=LW)
        ax.plot([x - .5, x - .5], [y - .45, y - .75], color='green', linewidth=LW)
        ax.plot([x - .55, x - .55], [y - .5, y - .7], color='green', linewidth=LW)
        ax.plot([x - .6, x - .6], [y - .55, y - .65], color='green', linewidth=LW)
        ax.text(x - .42, y - .3, label, fontsize=fs, ha='center')

    # ---------------- INSTRUMENT TRANSFORMERS ----------------
    @staticmethod
    def draw_ct(ax, x, y, label, fs):
        spacing = 0.75
        ax.add_patch(Arc((x + .03, y - spacing / 4), width=0.2, height=0.4,
                         angle=0, theta1=80, theta2=280, color='blue', linewidth=LW))
        ax.add_patch(Arc((x + .03, y + spacing / 4), width=0.2, height=0.4,
                         angle=0, theta1=80, theta2=280, color='blue', linewidth=LW))
        ax.text(x - .15, y, label, fontsize=fs, ha='right', va='center')

    @staticmethod
    def draw_wt(ax, x, y, label, fs):
        ax.add_patch(Arc((x, y - 0.15), width=0.2, height=0.4,
                         angle=0, theta1=90, theta2=360, color='red', linewidth=LW))
        ax.plot([x, x + .1], [y - .15, y - .15], color='red', linewidth=LW)
        ax.text(x - .15, y, label, fontsize=fs, ha='right', va='center')

    @staticmethod
    def draw_cvt(ax, x, y, label, fs):
        """Capacitive voltage transformer (proven multi-stage symbol)."""
        y = y - .2
        ax.plot([x, x + .15], [y - .6, y - .6], color='red', linewidth=LW)
        ax.plot([x + .15, x + .15], [y - .45, y - .75], color='red', linewidth=LW)
        ax.plot([x + .2, x + .2], [y - .45, y - .75], color='red', linewidth=LW)
        ax.plot([x + .2, x + .55], [y - .6, y - .6], color='red', linewidth=LW)
        ax.plot([x + .55, x + .55], [y - .45, y - .75], color='red', linewidth=LW)
        ax.plot([x + .6, x + .6], [y - .45, y - .75], color='red', linewidth=LW)
        ax.plot([x + .6, x + .7], [y - .6, y - .6], color='red', linewidth=LW)
        ax.plot([x + .7, x + .7], [y - .45, y - .75], color='green', linewidth=LW)
        ax.plot([x + .75, x + .75], [y - .5, y - .7], color='green', linewidth=LW)
        ax.plot([x + .8, x + .8], [y - .55, y - .65], color='green', linewidth=LW)
        ax.plot([x + .375, x + .375], [y - .6, y - 1.4], color='red', linewidth=LW)
        ax.plot([x + .375, x + .45], [y - 1.4, y - 1.4], color='red', linewidth=LW)
        ax.add_patch(Arc((x + .45, y - 1.4 - 0.1125), width=0.1, height=0.2,
                         angle=0, theta1=270, theta2=90, color='red', linewidth=LW))
        ax.add_patch(Arc((x + .45, y - 1.4 + 0.1125), width=0.1, height=0.2,
                         angle=0, theta1=270, theta2=90, color='red', linewidth=LW))
        ax.plot([x + .575, x + .575], [y - 1, y - 1.7], color='red', linewidth=LW)
        ax.plot([x + .55, x + .55], [y - 1, y - 1.7], color='red', linewidth=LW)
        spacing = 0.25
        for cy in (y - 1.1 - spacing / 4, y - 1.025 + spacing / 4,
                   y - 1.6 + spacing / 4, y - 1.8 + spacing / 4):
            ax.add_patch(Arc((x + .675, cy), width=0.1, height=0.2,
                             angle=0, theta1=80, theta2=280, color='red', linewidth=LW))
        ax.text(x + .4, y - .35, label, fontsize=fs, ha='center')

    # ---------------- LIGHTNING ARRESTER ----------------
    @staticmethod
    def draw_la(ax, x, y, label, fs):
        y = y - .2
        ax.plot([x - .9, x], [y, y], color='red', linewidth=LW)
        ax.plot([x - .9, x - .9], [y + .2, y - .2], color='green', linewidth=LW)
        ax.plot([x - .95, x - .95], [y + .15, y - .15], color='green', linewidth=LW)
        ax.plot([x - 1, x - 1], [y + .1, y - .1], color='green', linewidth=LW)
        ax.text(x - .5, y - .45, label, fontsize=fs, ha='center')

    @staticmethod
    def la_comp(ax, x, y):
        """Arrester body: arrow inside a box."""
        ax.add_patch(Polygon([[x + 0.1, y + 0.1], [x - 0.1, y], [x + 0.1, y - 0.1]],
                             closed=True, fill=True, color='red', linewidth=LW))
        ax.add_patch(Rectangle((x - 0.2, y - 0.2), 0.4, 0.4, fill=False,
                               edgecolor='red', linewidth=LW))

    # ---------------- POWER EQUIPMENT ----------------
    @staticmethod
    def draw_ict(ax, x, y, label, fs):
        """Interconnecting / power transformer (two interlaced windings)."""
        ax.add_patch(Arc((x, y - 0.15), width=0.3, height=0.6,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.add_patch(Arc((x - .15, y - 0.15), width=0.2, height=0.4,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.add_patch(Arc((x, y - .255 - 0.15), width=0.4, height=1.2,
                         angle=0, theta1=270, theta2=90, color='red', linewidth=LW))
        ax.text(x - .3, y - .7, label, fontsize=fs, ha='center')

    @staticmethod
    def draw_reacter(ax, x, y, label, fs):
        ax.add_patch(Arc((x - .025, y - .05), width=0.2, height=0.4,
                         angle=0, theta1=80, theta2=300, color='red', linewidth=LW))
        ax.add_patch(Arc((x - .025, y - .3), width=0.2, height=0.4,
                         angle=0, theta1=60, theta2=300, color='red', linewidth=LW))
        ax.add_patch(Arc((x - .025, y - .55), width=0.2, height=0.4,
                         angle=0, theta1=60, theta2=300, color='red', linewidth=LW))
        ax.add_patch(Arc((x - .025, y - .8), width=0.2, height=0.4,
                         angle=0, theta1=60, theta2=280, color='red', linewidth=LW))
        ax.text(x - .45, y - .8, label, fontsize=fs, ha='center')

    @staticmethod
    def draw_ict3(ax, x, y, label, fs):
        """3-winding autotransformer (HV+LV overlapping, tertiary, earthed
        neutral) — matches reference ICT symbol."""
        ax.add_patch(Arc((x, y), width=0.5, height=0.5,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.add_patch(Arc((x, y - 0.3), width=0.5, height=0.5,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        ax.add_patch(Arc((x + 0.4, y - 0.15), width=0.26, height=0.26,
                         angle=0, theta1=0, theta2=360, color='red', linewidth=LW))
        # earthed neutral (left)
        ax.plot([x - 0.25, x - 0.55], [y - 0.15, y - 0.15], color='green', linewidth=LW)
        ax.plot([x - 0.55, x - 0.55], [y - 0.15, y - 0.3], color='green', linewidth=LW)
        ComponentDrawer.draw_earth_symbol(ax, x - 0.55, y - 0.42, "", fs)
        ax.text(x - 0.35, y + 0.32, label, fontsize=fs, ha='right')

    @staticmethod
    def draw_ngr(ax, x, y, fs):
        """Neutral grounding reactor (small 2-turn coil)."""
        ax.add_patch(Arc((x, y - .05), width=0.14, height=0.24,
                         angle=0, theta1=60, theta2=300, color='red', linewidth=LW))
        ax.add_patch(Arc((x, y - .25), width=0.14, height=0.24,
                         angle=0, theta1=60, theta2=280, color='red', linewidth=LW))
        ax.text(x + .18, y - .15, "NGR", fontsize=fs, ha='left')

    @staticmethod
    def draw_gantry(ax, x, y, label, fs):
        """OHL termination gantry (beam + legs + X-brace)."""
        ax.plot([x, x], [y + .12, y], color='red', linewidth=LW)
        ax.plot([x - .3, x + .3], [y, y], color='red', linewidth=LW)
        ax.plot([x - .25, x - .25], [y, y - .35], color='red', linewidth=LW)
        ax.plot([x + .25, x + .25], [y, y - .35], color='red', linewidth=LW)
        ax.plot([x - .25, x + .25], [y, y - .35], color='red', linewidth=LW)
        ax.plot([x + .25, x - .25], [y, y - .35], color='red', linewidth=LW)
        if label:
            ax.text(x + .4, y - .15, label, fontsize=fs, ha='left')

    @staticmethod
    def draw_cable_termination(ax, x, y, label, fs):
        """Cable sealing end: cone + cable tail with hook."""
        ax.add_patch(Polygon([[x - 0.1, y], [x + 0.1, y], [x, y - 0.4]],
                             closed=True, fill=False, edgecolor='red', linewidth=LW))
        ax.plot([x, x], [y - .4, y - .7], color='red', linewidth=LW)
        ax.add_patch(Arc((x + 0.08, y - 0.7), width=0.16, height=0.16,
                         angle=0, theta1=180, theta2=270, color='red', linewidth=LW))
        if label:
            ax.text(x + .2, y - .3, label, fontsize=fs, ha='left')

    # ---------------- TERMINATIONS ----------------
    @staticmethod
    def draw_symbol(ax, x, y, label, fs):
        """Down arrow — outgoing feeder."""
        ax.add_patch(Polygon([[x, y - 0.1], [x + 0.1, y + 0.1], [x - 0.1, y + 0.1]],
                             closed=True, fill=False, edgecolor='red', linewidth=LW))

    @staticmethod
    def draw_symbol_upp(ax, x, y, label, fs):
        """Up arrow — incoming feeder."""
        ax.add_patch(Polygon([[x, y + 0.1], [x + 0.1, y - 0.1], [x - 0.1, y - 0.1]],
                             closed=True, fill=False, edgecolor='red', linewidth=LW))

    @staticmethod
    def draw_earth_symbol(ax, x, y, label, fs):
        ax.plot([x - .125, x + .125], [y + .1, y + .1], color='green', linewidth=LW)
        ax.plot([x - .1, x + .1], [y, y], color='green', linewidth=LW)
        ax.plot([x - .075, x + .075], [y - .1, y - .1], color='green', linewidth=LW)
        ax.plot([x - .05, x + .05], [y - .2, y - .2], color='green', linewidth=LW)
        ax.plot([x - .025, x + .025], [y - .3, y - .3], color='green', linewidth=LW)

    @staticmethod
    def draw_name(ax, x, y, label, fs):
        ax.text(x, y + .5, label, fontsize=fs + 2, ha='center')


if __name__ == "__main__":
    print("Component library v2 loaded:")
    for c in COMPONENT_CATALOG:
        print(f"  {c.symbol_type:16s} {c.name} ({c.description})")
