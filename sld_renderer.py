"""
MAIN SLD RENDERING ENGINE (v2)
==============================
Parametric renderer built on the PROVEN geometry of the original engine.

Supported configurations:
  - single_bus
  - double_bus_coupler        (two buses + bus coupler bay)
  - double_bus_sectionalizer  (two buses split by bus sectionalizer isolators)

Bay numbering: Lines odd (401,403,...), Transformers even (402,404,...),
Reactors sequential from x21 (421,422,...). Lines/transformers interleave
by number, reactors at the end, coupler at the middle of the row.
"""

import io
import math
import datetime
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ezdxf
from ezdxf.enums import TextEntityAlignment

from config_components import ComponentDrawer as D, LW, BUS_LW

# AutoCAD .dwg-style lettering (monospace stroke font look)
plt.rcParams['font.family'] = 'monospace'
plt.rcParams['font.monospace'] = ['DejaVu Sans Mono', 'Courier New', 'monospace']


# ============================================================================
# DXF EXPORT (proven engine from original Final_DXF.py)
# ============================================================================

def export_ax_to_dxf(ax):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    for line in ax.lines:
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        color = line.get_color()
        dxf_color = 7
        if color == 'red':
            dxf_color = 1
        elif color == 'green':
            dxf_color = 3
        elif color == 'blue':
            dxf_color = 5
        elif color == 'black':
            dxf_color = 7
        for idx in range(len(xdata) - 1):
            msp.add_line((xdata[idx], ydata[idx]), (xdata[idx + 1], ydata[idx + 1]),
                         dxfattribs={'color': dxf_color})

    for patch in ax.patches:
        ec = patch.get_edgecolor()
        fc = patch.get_facecolor()

        def get_dxf_color(rgba):
            if rgba[0] > 0.5 and rgba[1] < 0.5 and rgba[2] < 0.5:
                return 1
            elif rgba[1] > 0.4 and rgba[0] < 0.5 and rgba[2] < 0.5:
                return 3
            elif rgba[2] > 0.5 and rgba[0] < 0.5 and rgba[1] < 0.5:
                return 5
            return 7

        edge_color = get_dxf_color(ec)
        face_color = get_dxf_color(fc)
        is_filled = patch.get_fill()

        if isinstance(patch, mpatches.Rectangle):
            x, y = patch.get_xy()
            w, h = patch.get_width(), patch.get_height()
            pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            if is_filled:
                hatch = msp.add_hatch(color=face_color)
                hatch.paths.add_polyline_path(pts, is_closed=True)
            msp.add_lwpolyline(pts, close=True, dxfattribs={'color': edge_color})

        elif isinstance(patch, mpatches.Polygon):
            pts = patch.get_xy()
            if len(pts) > 1 and (pts[0][0] == pts[-1][0] and pts[0][1] == pts[-1][1]):
                pts = pts[:-1]
            if is_filled:
                hatch = msp.add_hatch(color=face_color)
                hatch.paths.add_polyline_path(pts, is_closed=True)
            msp.add_lwpolyline(pts, close=True, dxfattribs={'color': edge_color})

        elif isinstance(patch, mpatches.Arc):
            w = patch.width
            h = patch.height

            def true_to_parametric(theta_deg, w, h):
                theta_rad = math.radians(theta_deg)
                t_rad = math.atan2(w * math.sin(theta_rad), h * math.cos(theta_rad))
                return math.degrees(t_rad) % 360.0

            t1 = true_to_parametric(patch.theta1, w, h)
            t2 = true_to_parametric(patch.theta2, w, h)
            if t2 <= t1 and not math.isclose(patch.theta1, patch.theta2):
                t2 += 360.0

            num_segments = 36
            angles = [math.radians(t1 + (t2 - t1) * i / num_segments)
                      for i in range(num_segments + 1)]
            cx, cy = patch.center
            rot = math.radians(patch.angle)
            cos_r, sin_r = math.cos(rot), math.sin(rot)
            pts = []
            for a in angles:
                ex = (w / 2.0) * math.cos(a)
                ey = (h / 2.0) * math.sin(a)
                px = ex * cos_r - ey * sin_r + cx
                py = ex * sin_r + ey * cos_r + cy
                pts.append((px, py))
            msp.add_lwpolyline(pts, dxfattribs={'color': edge_color})

    for txt in ax.texts:
        x, y = txt.get_position()
        text_str = txt.get_text()
        if not text_str.strip():
            continue
        fs = txt.get_fontsize()
        ha = txt.get_ha()
        va = txt.get_va()
        color = txt.get_color()
        dxf_color = 7
        if color == 'red':
            dxf_color = 1
        elif color == 'green':
            dxf_color = 3
        elif color == 'blue':
            dxf_color = 5

        h_scale = fs * 0.025
        line_gap = h_scale * 1.3
        lines = text_str.split('\n')
        num_lines = len(lines)
        block_height = (num_lines - 1) * line_gap + h_scale

        if va == 'top':
            start_center_y = y - (h_scale / 2.0)
        elif va in ['bottom', 'baseline']:
            start_center_y = y + block_height - (h_scale / 2.0)
        else:
            start_center_y = y + (block_height / 2.0) - (h_scale / 2.0)

        align = TextEntityAlignment.MIDDLE_CENTER
        if ha == 'left':
            align = TextEntityAlignment.MIDDLE_LEFT
        elif ha == 'right':
            align = TextEntityAlignment.MIDDLE_RIGHT

        current_y = start_center_y
        for l_str in lines:
            if l_str.strip():
                dtxt = msp.add_text(l_str, dxfattribs={'height': h_scale,
                                                       'color': dxf_color,
                                                       'width': 0.85})
                dtxt.set_placement((x, current_y), align=align)
            current_y -= line_gap

    return doc


# ============================================================================
# PARAMETERS
# ============================================================================

@dataclass
class SLDGenerationParams:
    substation_name: str
    hv_voltage: float
    lv_voltage: Optional[float] = None
    configuration: str = 'double_bus_coupler'
    line_bay_count: int = 0
    cable_bay_count: int = 0
    transformer_bay_count: int = 0
    reactor_bay_count: int = 0
    bus_coupler_count: int = 1
    line_names: List[str] = None
    cable_names: List[str] = None
    transformer_names: List[str] = None
    reactor_names: List[str] = None
    title_text: str = "Typical Substation Single Line Diagram"
    show_legend: bool = True
    dpi: int = 300
    # Ratings
    bus_fault_ka: float = 63
    bus_fault_sec: float = 1
    tx_mva: List[str] = None       # per-ICT MVA
    tx_z: List[str] = None         # per-ICT %Z
    tx_vg: List[str] = None        # per-ICT vector group
    reactor_mvar: List[str] = None  # per-reactor MVAr

    def __post_init__(self):
        self.line_names = self.line_names or []
        self.cable_names = self.cable_names or []
        self.transformer_names = self.transformer_names or []
        self.reactor_names = self.reactor_names or []
        self.tx_mva = self.tx_mva or []
        self.tx_z = self.tx_z or []
        self.tx_vg = self.tx_vg or []
        self.reactor_mvar = self.reactor_mvar or []


# ============================================================================
# RENDERER
# ============================================================================

class SLDRenderer:
    def __init__(self, params: SLDGenerationParams):
        self.params = params
        self.fig = None
        self.ax = None
        self.components_count = 0
        self.bays_drawn = []

        self.is_double = params.configuration in (
            'double_bus_coupler', 'double_bus_sectionalizer')
        self.is_dual_voltage = (params.lv_voltage is not None
                                and params.lv_voltage != params.hv_voltage)

        # Layout constants (proven original geometry)
        self.bus1_y = 10.0
        self.bus2_y = 9.0
        self.bay_y = 8.2      # bay top reference
        self.gap = 2.0
        self.x_start = 5.0
        self.fs = 6

    # ------------------------------------------------------------------
    def _num_prefix(self) -> int:
        v = int(self.params.hv_voltage)
        return (v // 100) if v >= 100 else (v // 10)

    def _name(self, names, i, default):
        if i < len(names) and str(names[i]).strip():
            return str(names[i]).strip()
        return default

    def _build_bays(self) -> List[Tuple[str, int, str]]:
        """Returns list of (type, number, name). Lines/ICTs interleaved by
        number, reactors after, coupler inserted at middle."""
        p = self.params
        base = self._num_prefix() * 100
        numbered = []
        odd = 1
        for i in range(p.line_bay_count):
            numbered.append(('line', base + odd,
                             self._name(p.line_names, i, f"LINE-{i + 1}")))
            odd += 2
        for i in range(p.cable_bay_count):
            numbered.append(('cable', base + odd,
                             self._name(p.cable_names, i, f"CABLE-{i + 1}")))
            odd += 2
        for i in range(p.transformer_bay_count):
            numbered.append(('ict', base + 2 * i + 2,
                             self._name(p.transformer_names, i, f"ICT-{i + 1}")))
        numbered.sort(key=lambda b: b[1])

        for i in range(p.reactor_bay_count):
            numbered.append(('reactor', base + 21 + i,
                             self._name(p.reactor_names, i, f"REACTOR-{i + 1}")))

        if self.is_double and p.configuration == 'double_bus_coupler':
            mid = len(numbered) // 2
            for i in range(max(p.bus_coupler_count, 0)):
                numbered.insert(mid + i, ('coupler', 0, "BUS COUPLER"))
        return numbered

    # ------------------------------------------------------------------
    # BAY BUILDERS
    # ------------------------------------------------------------------
    def _bay_top(self, ax, x, num):
        """Bus-selection top: risers + isolators to BUS1/BUS2, junction,
        breaker. Returns x of main stem (x+0.25)."""
        y = self.bay_y
        fs = self.fs
        if self.is_double:
            ax.plot([x, x], [y, self.bus1_y], color='black', linewidth=LW)
            ax.plot([x + .5, x + .5], [y, self.bus2_y], color='black', linewidth=LW)
            D.draw_isolator(ax, x, y, f"{num}89A", fs)
            D.draw_isolator(ax, x + .5, y, f"{num}89B", fs)
            D.earth_sh(ax, x, y, f"{num}89AE", fs)
            ax.plot([x, x + 0.5], [y - 1.2, y - 1.2], color='black', linewidth=LW)
            self.components_count += 3
        else:
            ax.plot([x + .25, x + .25], [y, self.bus1_y], color='black', linewidth=LW)
            D.draw_isolator(ax, x + .25, y, f"{num}89A", fs)
            D.earth_sh(ax, x + .25, y, f"{num}89AE", fs)
            ax.plot([x + .25, x + .25], [y - 1.2, y - 1.2], color='black', linewidth=LW)
            self.components_count += 2
        D.draw_breaker(ax, x + 0.25, y - 2.2, f"{num}52", fs)
        self.components_count += 1

    def _bay_label(self, ax, x, num, name):
        y = self.bay_y
        words = str(name).split()
        lines, cur = [], ""
        for w in words:
            if len(cur + " " + w) <= 24:
                cur = (cur + " " + w).strip()
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        head = f"{num}" if num else ""
        full = (head + "\n" + "\n".join(lines)).strip()
        ax.text(x + .25, y - 11.4, full, ha='center', va='top',
                fontsize=self.fs + 1)

    def _bay_line(self, ax, x, num, name):
        y, fs = self.bay_y, self.fs
        self._bay_top(ax, x, num)
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5], color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89L", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89LE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 10.4], color='black', linewidth=LW)
        D.draw_cvt(ax, x + 0.25, y - 7, f"{num}CVT", fs)
        D.draw_la(ax, x + 0.25, y - 8.5, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 8.7)
        D.draw_gantry(ax, x + 0.25, y - 10.5, "", fs)
        D.draw_symbol(ax, x + 0.25, y - 11.0, "", fs)
        self.components_count += 8
        self._bay_label(ax, x, num, name)

    def _bay_cable(self, ax, x, num, name):
        """Cable feeder: as line bay but no WT, ends in cable sealing end."""
        y, fs = self.bay_y, self.fs
        self._bay_top(ax, x, num)
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5], color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89L", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89LE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 10.3], color='black', linewidth=LW)
        D.draw_cvt(ax, x + 0.25, y - 7, f"{num}CVT", fs)
        D.draw_la(ax, x + 0.25, y - 8.5, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 8.7)
        D.draw_cable_termination(ax, x + 0.25, y - 10.3, "CABLE", fs)
        self.components_count += 7
        self._bay_label(ax, x, num, name)

    def _tx_rating(self, i):
        p = self.params

        def pick(lst, d):
            return str(lst[i]) if i < len(lst) and str(lst[i]).strip() else d

        return {'mva': pick(p.tx_mva, "500"), 'z': pick(p.tx_z, "12.5"),
                'vg': pick(p.tx_vg, "YNa0d11")}

    def _bay_ict(self, ax, x, num, name, idx=0):
        y, fs = self.bay_y, self.fs
        p = self.params
        self._bay_top(ax, x, num)
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5], color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89T", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89TE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 7.8], color='black', linewidth=LW)
        D.draw_la(ax, x + 0.25, y - 6.6, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 6.8)
        D.draw_ict3(ax, x + 0.25, y - 8.1, f"{num}ICT", fs)
        # Rating block (per-transformer inputs), right of symbol
        r = self._tx_rating(idx)
        ratio = (f"{int(p.hv_voltage)}/{int(p.lv_voltage)}kV"
                 if self.is_dual_voltage else f"{int(p.hv_voltage)}kV")
        block = (f"Tr.{idx + 1}\n{r['mva']}MVA\n{ratio}\n"
                 f"%Z={r['z']}\n{r['vg']}")
        ax.text(x + 0.65, y - 7.75, block, fontsize=fs, ha='left', va='top')
        ax.plot([x + 0.25, x + 0.25], [y - 8.8, y - 10.1], color='black', linewidth=LW)
        D.draw_symbol(ax, x + 0.25, y - 10.2, "", fs)
        if self.is_dual_voltage:
            ax.text(x + 0.25, y - 10.75, f"TO {int(p.lv_voltage)}kV",
                    fontsize=fs, ha='center')
        self.components_count += 5
        self._bay_label(ax, x, num, name)

    def _bay_reactor(self, ax, x, num, name, idx=0):
        y, fs = self.bay_y, self.fs
        p = self.params
        self._bay_top(ax, x, num)
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5], color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89R", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89RE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 7.85], color='black', linewidth=LW)
        D.draw_la(ax, x + 0.25, y - 6.6, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 6.8)
        D.draw_reacter(ax, x + 0.25, y - 8, f"{num}R", fs)
        # Rating block (per-reactor input), right of coil
        mvar = (str(p.reactor_mvar[idx])
                if idx < len(p.reactor_mvar) and str(p.reactor_mvar[idx]).strip()
                else "80")
        block = f"R-{idx + 1}\n{mvar}MVAr\n{int(p.hv_voltage)}kV"
        ax.text(x + 0.55, y - 7.75, block, fontsize=fs, ha='left', va='top')
        ax.plot([x + 0.25, x + 0.25], [y - 9, y - 9.55], color='black', linewidth=LW)
        D.draw_ngr(ax, x + 0.25, y - 9.6, fs)
        ax.plot([x + 0.25, x + 0.25], [y - 9.95, y - 10.15], color='black', linewidth=LW)
        D.draw_earth_symbol(ax, x + 0.25, y - 10.25, "", fs)
        self.components_count += 6
        self._bay_label(ax, x, num, name)

    def _bay_coupler(self, ax, x, name):
        y, fs = self.bay_y, self.fs
        pref = self._num_prefix()
        ax.plot([x - .2, x - .2], [y - .3, self.bus1_y], color='black', linewidth=LW)
        ax.plot([x + .7, x + .7], [y - .3, self.bus2_y], color='black', linewidth=LW)
        ax.plot([x - .2, x - .2], [y - 4, y - 1.5], color='black', linewidth=LW)
        ax.plot([x + .7, x + .7], [y - 4, y - 1.5], color='black', linewidth=LW)
        D.draw_isolator(ax, x - .2, y - .3, f"{pref}0089A", fs)
        D.draw_isolator(ax, x + .7, y - .3, f"{pref}0089B", fs)
        D.earth_sh(ax, x - .2, y - .5, f"{pref}0089AE", fs)
        D.earth_sh(ax, x + .7, y - .5, f"{pref}0089BE", fs)
        D.draw_ct(ax, x - .2, y - 2.5, f"{pref}00CT1", fs)
        D.draw_ct(ax, x + .7, y - 2.5, f"{pref}00CT2", fs)
        D.draw_breaker_coupler(ax, x + 0.25, y - 4, f"{pref}0052", fs)
        self.components_count += 7
        ax.text(x + .25, y - 11.4, name, ha='center', va='top', fontsize=fs + 1)

    # ------------------------------------------------------------------
    def _draw_bus_aux(self, ax):
        """Bus VT (isolator + WT) and bus earth switch on each bus,
        drawn in the left margin before the first bay."""
        fs = self.fs
        hv = int(self.params.hv_voltage)

        def one(xb, yb, tag):
            ax.plot([xb, xb], [yb, yb - 0.4], color='black', linewidth=LW)
            D.draw_isolator(ax, xb, yb - 0.4, f"{tag}-89V", fs)
            D.earth_sh(ax, xb, yb - 0.7, f"{tag}-89E", fs)
            D.draw_bus_vt(ax, xb, yb - 1.6, f"{tag} VT", fs)
            self.components_count += 3

        one(2.3, self.bus1_y, "B1")
        if self.is_double:
            one(3.7, self.bus2_y, "B2")

    # ------------------------------------------------------------------
    def _draw_buses(self, ax, n_bays):
        p = self.params
        x_end = self.x_start + n_bays * self.gap + 0.5
        hv = int(p.hv_voltage)
        fs = self.fs

        if self.is_double and p.configuration == 'double_bus_sectionalizer' and n_bays > 1:
            mid = n_bays // 2
            xm = self.x_start + mid * self.gap - self.gap / 2 + 0.25
            for yb, col, tag in ((self.bus1_y, 'blue', 'BUS-1'),
                                 (self.bus2_y, 'green', 'BUS-2')):
                ax.plot([1, xm - 0.6], [yb, yb], color=col, linewidth=BUS_LW)
                ax.plot([xm + 0.6, x_end], [yb, yb], color=col, linewidth=BUS_LW)
                ax.plot([xm - 0.6, xm - 0.3], [yb, yb], color='black', linewidth=LW)
                ax.plot([xm + 0.3, xm + 0.6], [yb, yb], color='black', linewidth=LW)
                D.draw_isolator_h(ax, xm, yb, f"89S {tag}", fs)
                self.components_count += 1
        else:
            ax.plot([1, x_end], [self.bus1_y, self.bus1_y],
                    color='black', linewidth=BUS_LW)
            if self.is_double:
                ax.plot([1, x_end], [self.bus2_y, self.bus2_y],
                        color='black', linewidth=BUS_LW)

        ka = self.params.bus_fault_ka
        sec = self.params.bus_fault_sec
        ka_s = f"{int(ka)}" if float(ka).is_integer() else f"{ka}"
        sec_s = f"{int(sec)}" if float(sec).is_integer() else f"{sec}"
        rating = f"{hv}kV, {ka_s}kA, {sec_s}Sec"
        ax.text(1.1, self.bus1_y + 0.3, f"BUS-1  {rating}",
                fontsize=fs + 3, color='black', fontweight='bold')
        if self.is_double:
            ax.text(1.1, self.bus2_y - 0.55, f"BUS-2  {rating}",
                    fontsize=fs + 3, color='black', fontweight='bold')
        return x_end

    # ------------------------------------------------------------------
    def render(self):
        p = self.params
        bays = self._build_bays()
        n = max(len(bays), 1)

        fig_w = max(13, n * 1.9 + 6)
        self.fig, self.ax = plt.subplots(figsize=(fig_w, 8))
        ax = self.ax

        x_end = self._draw_buses(ax, n)
        self._draw_bus_aux(ax)

        ict_i = 0
        re_i = 0
        for idx, (btype, num, name) in enumerate(bays):
            x = self.x_start + idx * self.gap
            if btype == 'line':
                self._bay_line(ax, x, num, name)
            elif btype == 'cable':
                self._bay_cable(ax, x, num, name)
            elif btype == 'ict':
                self._bay_ict(ax, x, num, name, ict_i)
                ict_i += 1
            elif btype == 'reactor':
                self._bay_reactor(ax, x, num, name, re_i)
                re_i += 1
            elif btype == 'coupler':
                self._bay_coupler(ax, x, name)
            self.bays_drawn.append((btype, num, name))

        center_x = (1 + x_end) / 2
        ax.text(center_x, 14.2, p.title_text, fontsize=self.fs + 14,
                va='center', ha='center', fontweight='bold')
        ax.text(center_x, 12.9, p.substation_name, fontsize=self.fs + 9,
                va='center', ha='center')
        cfg_label = {
            'single_bus': "SINGLE BUS BAR SCHEME",
            'double_bus_coupler': "DOUBLE BUS BAR WITH BUS COUPLER",
            'double_bus_sectionalizer': "DOUBLE BUS BAR WITH BUS SECTIONALIZER",
        }.get(p.configuration, "")
        date_str = datetime.date.today().isoformat()
        ax.text(center_x, 12.0, f"{cfg_label}   |   Generated: {date_str}",
                fontsize=self.fs + 2, va='center', ha='center', style='italic')

        ax.set_xlim(0.5, x_end + 2.5)
        ax.set_ylim(-6.0, 15.5)
        ax.axis('off')
        self.fig.tight_layout()
        return self.fig, self.ax

    # ------------------------------------------------------------------
    def export_pdf(self, target):
        if self.fig is None:
            self.render()
        self.fig.savefig(target, format='pdf', dpi=self.params.dpi,
                         bbox_inches='tight', facecolor='white')

    def export_dxf(self, target):
        """target: filepath (str) or text stream (StringIO)."""
        if self.ax is None:
            self.render()
        doc = export_ax_to_dxf(self.ax)
        if isinstance(target, str):
            doc.saveas(target)
        else:
            doc.write(target)

    def get_summary(self) -> Dict:
        p = self.params
        return {
            'substation': p.substation_name,
            'hv_voltage': p.hv_voltage,
            'lv_voltage': p.lv_voltage,
            'configuration': p.configuration,
            'total_bays': len(self.bays_drawn),
            'line_bays': p.line_bay_count,
            'transformer_bays': p.transformer_bay_count,
            'reactor_bays': p.reactor_bay_count,
            'components_drawn': self.components_count,
            'is_dual_voltage': self.is_dual_voltage,
            'is_dual_bus': self.is_double,
        }


def generate_sld(params: SLDGenerationParams):
    renderer = SLDRenderer(params)
    fig, ax = renderer.render()
    return fig, renderer


if __name__ == "__main__":
    params = SLDGenerationParams(
        substation_name="YELAHANKA SUBSTATION",
        hv_voltage=400, lv_voltage=220,
        configuration='double_bus_coupler',
        line_bay_count=4, transformer_bay_count=2,
        reactor_bay_count=1, bus_coupler_count=1,
        line_names=["TUMKUR-1 72km", "DEVANAHALLI", "TUMKUR-2", "LINE-4"],
        transformer_names=["500MVA ICT-1", "500MVA ICT-2"],
    )
    fig, r = generate_sld(params)
    r.export_pdf("test_v2.pdf")
    r.export_dxf("test_v2.dxf")
    print(r.get_summary())
