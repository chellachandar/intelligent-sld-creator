"""
MAIN SLD RENDERING ENGINE (v3 — A3 TEMPLATE)
============================================
Two-panel A3 architecture:
  - PAGE axes: true-scale A3 sheet in cm (42 x 29.7). Border, legend table
    (bottom-left), title block (bottom-right), headings.
  - SLD axes:  the switchyard drawing in its own panel, stretched to the
    classic wide presentation (no compromise on symbol proportions).

DXF export maps BOTH panels into one drawing (page cm coordinates) so
AutoCAD shows exactly what is on screen / PDF. Fully editable entities.
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

PAGE_H = 29.7        # A3 height, cm (fixed)
PAGE_MIN_W = 42.0    # A3 width, cm (minimum page width — grows with bays)
SLD_SX = 2.0         # cm per data-unit horizontally (fixed bay size)
SLD_SY = 12.6 / 18.2  # cm per data-unit vertically (classic ratio)


# ============================================================================
# DXF EXPORT (transform-aware; proven arc/text math)
# ============================================================================

def _export_axes_to_msp(msp, ax, tf):
    """Export one Axes' entities into modelspace applying affine transform
    tf = (sx, ox, sy, oy):  x' = x*sx + ox ;  y' = y*sy + oy."""
    sx, ox, sy, oy = tf

    def T(x, y):
        return (x * sx + ox, y * sy + oy)

    def col_of(color):
        if color == 'red':
            return 1
        if color == 'green':
            return 3
        if color == 'blue':
            return 5
        return 7

    for line in ax.lines:
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        dxf_color = col_of(line.get_color())
        for idx in range(len(xdata) - 1):
            msp.add_line(T(xdata[idx], ydata[idx]),
                         T(xdata[idx + 1], ydata[idx + 1]),
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
            pts = [T(x, y), T(x + w, y), T(x + w, y + h), T(x, y + h)]
            if is_filled:
                hatch = msp.add_hatch(color=face_color)
                hatch.paths.add_polyline_path(pts, is_closed=True)
            msp.add_lwpolyline(pts, close=True,
                               dxfattribs={'color': edge_color})

        elif isinstance(patch, mpatches.Polygon):
            raw = patch.get_xy()
            if len(raw) > 1 and (raw[0][0] == raw[-1][0]
                                 and raw[0][1] == raw[-1][1]):
                raw = raw[:-1]
            pts = [T(px, py) for px, py in raw]
            if is_filled:
                hatch = msp.add_hatch(color=face_color)
                hatch.paths.add_polyline_path(pts, is_closed=True)
            msp.add_lwpolyline(pts, close=True,
                               dxfattribs={'color': edge_color})

        elif isinstance(patch, mpatches.Arc):
            w = patch.width
            h = patch.height

            def true_to_parametric(theta_deg, w_, h_):
                theta_rad = math.radians(theta_deg)
                t_rad = math.atan2(w_ * math.sin(theta_rad),
                                   h_ * math.cos(theta_rad))
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
                pts.append(T(px, py))
            msp.add_lwpolyline(pts, dxfattribs={'color': edge_color})

    for txt in ax.texts:
        x, y = txt.get_position()
        text_str = txt.get_text()
        if not text_str.strip():
            continue
        fs = txt.get_fontsize()
        ha = txt.get_ha()
        va = txt.get_va()
        dxf_color = col_of(txt.get_color())

        h_scale = fs * 0.0353          # pt -> cm on the A3 sheet
        line_gap = h_scale * 1.45
        lines = text_str.split('\n')
        num_lines = len(lines)
        block_height = (num_lines - 1) * line_gap + h_scale

        tx, ty = T(x, y)
        if va == 'top':
            start_center_y = ty - (h_scale / 2.0)
        elif va in ['bottom', 'baseline']:
            start_center_y = ty + block_height - (h_scale / 2.0)
        else:
            start_center_y = ty + (block_height / 2.0) - (h_scale / 2.0)

        align = TextEntityAlignment.MIDDLE_CENTER
        if ha == 'left':
            align = TextEntityAlignment.MIDDLE_LEFT
        elif ha == 'right':
            align = TextEntityAlignment.MIDDLE_RIGHT

        current_y = start_center_y
        for l_str in lines:
            if l_str.strip():
                dtxt = msp.add_text(l_str,
                                    dxfattribs={'height': h_scale,
                                                'color': dxf_color,
                                                'width': 0.85})
                dtxt.set_placement((tx, current_y), align=align)
            current_y -= line_gap

    return msp


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
    sectionalizer_count: int = 2   # 1 = BUS-1 only, 2 = both buses
    # Title block (drawing details)
    client: str = ""
    project: str = ""
    drawn_by: str = ""
    drg_no: str = ""
    rev: str = "1"
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
        self.ax = None          # SLD panel
        self.ax_page = None     # A3 page panel
        self.components_count = 0
        self.bays_drawn = []
        self._inset_tf = (1, 0, 1, 0)
        self._split_index = 0

        self.is_double = params.configuration in (
            'double_bus_coupler', 'double_bus_sectionalizer')
        self.is_dual_voltage = (params.lv_voltage is not None
                                and params.lv_voltage != params.hv_voltage)

        # Classic layout constants (proven geometry)
        self.bus1_y = 10.0
        self.bus2_y = 9.0
        self.bay_y = 8.2
        self.gap = 2.0
        self.x_start = 5.0
        self.bus_left = 3.0     # equal left/right bus margin (=2 each)
        self.fs = 5

    # ------------------------------------------------------------------
    def _num_prefix(self) -> int:
        v = int(self.params.hv_voltage)
        return (v // 100) if v >= 100 else (v // 10)

    def _name(self, names, i, default):
        if i < len(names) and str(names[i]).strip():
            return str(names[i]).strip()
        return default

    def _build_bays(self) -> List[Tuple[str, int, str]]:
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
                             self._name(p.transformer_names, i,
                                        f"ICT-{i + 1}")))
        numbered.sort(key=lambda b: b[1])

        for i in range(p.reactor_bay_count):
            numbered.append(('reactor', base + 21 + i,
                             self._name(p.reactor_names, i,
                                        f"REACTOR-{i + 1}")))

        cpl = max(int(p.bus_coupler_count), 0)
        mid = len(numbered) // 2
        self._split_index = mid

        if self.is_double and p.configuration == 'double_bus_coupler':
            if cpl >= 1:
                numbered.insert(mid, ('coupler', 0, "BUS COUPLER"))
        elif self.is_double and p.configuration == 'double_bus_sectionalizer':
            if cpl == 1:
                numbered.insert(mid, ('coupler', 0, "BUS COUPLER-1"))
                self._split_index = mid + 1
            elif cpl >= 2:
                numbered.insert(mid, ('coupler', 0, "BUS COUPLER-1"))
                numbered.insert(mid + 1, ('coupler', 0, "BUS COUPLER-2"))
                self._split_index = mid + 1
        return numbered

    # ------------------------------------------------------------------
    # BAY BUILDERS (classic geometry, unchanged presentation)
    # ------------------------------------------------------------------
    def _bay_top(self, ax, x, num):
        y = self.bay_y
        fs = self.fs
        if self.is_double:
            ax.plot([x, x], [y, self.bus1_y], color='black', linewidth=LW)
            ax.plot([x + .5, x + .5], [y, self.bus2_y],
                    color='black', linewidth=LW)
            D.draw_isolator(ax, x, y, f"{num}89A", fs)
            D.draw_isolator(ax, x + .5, y, f"{num}89B", fs)
            D.earth_sh(ax, x, y, f"{num}89AE", fs)
            ax.plot([x, x + 0.5], [y - 1.2, y - 1.2],
                    color='black', linewidth=LW)
            self.components_count += 3
        else:
            ax.plot([x + .25, x + .25], [y, self.bus1_y],
                    color='black', linewidth=LW)
            D.draw_isolator(ax, x + .25, y, f"{num}89A", fs)
            D.earth_sh(ax, x + .25, y, f"{num}89AE", fs)
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
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5],
                color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89L", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89LE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 10.4],
                color='black', linewidth=LW)
        D.draw_cvt(ax, x + 0.25, y - 7, f"{num}CVT", fs)
        D.draw_la(ax, x + 0.25, y - 8.5, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 8.7)
        D.draw_gantry(ax, x + 0.25, y - 10.5, "", fs)
        D.draw_symbol(ax, x + 0.25, y - 11.0, "", fs)
        self.components_count += 6
        self._bay_label(ax, x, num, name)

    def _bay_cable(self, ax, x, num, name):
        y, fs = self.bay_y, self.fs
        self._bay_top(ax, x, num)
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5],
                color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89L", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89LE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 10.3],
                color='black', linewidth=LW)
        D.draw_cvt(ax, x + 0.25, y - 7, f"{num}CVT", fs)
        D.draw_la(ax, x + 0.25, y - 8.5, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 8.7)
        D.draw_cable_termination(ax, x + 0.25, y - 10.3, "CABLE", fs)
        self.components_count += 6
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
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5],
                color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89T", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89TE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 7.8],
                color='black', linewidth=LW)
        D.draw_la(ax, x + 0.25, y - 6.6, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 6.8)
        D.draw_ict3(ax, x + 0.25, y - 8.1, f"{num}ICT", fs)
        r = self._tx_rating(idx)
        ratio = (f"{int(p.hv_voltage)}/{int(p.lv_voltage)}kV"
                 if self.is_dual_voltage else f"{int(p.hv_voltage)}kV")
        block = (f"Tr.{idx + 1}\n{r['mva']}MVA\n{ratio}\n"
                 f"%Z={r['z']}\n{r['vg']}")
        ax.text(x + 0.65, y - 7.75, block, fontsize=fs, ha='left', va='top')
        ax.plot([x + 0.25, x + 0.25], [y - 8.72, y - 10.1],
                color='black', linewidth=LW)
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
        ax.plot([x + .25, x + .25], [y - 2.7, y - 4.5],
                color='black', linewidth=LW)
        D.draw_ct(ax, x + 0.25, y - 3.4, f"{num}CT", fs)
        D.draw_isolator(ax, x + 0.25, y - 4.7, f"{num}89R", fs)
        D.earth_sh(ax, x + 0.25, y - 4.85, f"{num}89RE", fs)
        ax.plot([x + 0.25, x + 0.25], [y - 5.9, y - 7.85],
                color='black', linewidth=LW)
        D.draw_la(ax, x + 0.25, y - 6.6, f"{num}LA", fs)
        D.la_comp(ax, x - 0.25, y - 6.8)
        D.draw_reacter(ax, x + 0.25, y - 8, f"{num}R", fs)
        mvar = (str(p.reactor_mvar[idx])
                if idx < len(p.reactor_mvar)
                and str(p.reactor_mvar[idx]).strip() else "80")
        block = f"R-{idx + 1}\n{mvar}MVAr\n{int(p.hv_voltage)}kV"
        ax.text(x + 0.55, y - 7.75, block, fontsize=fs, ha='left', va='top')
        ax.plot([x + 0.25, x + 0.25], [y - 9, y - 9.55],
                color='black', linewidth=LW)
        D.draw_ngr(ax, x + 0.25, y - 9.6, fs)
        ax.plot([x + 0.25, x + 0.25], [y - 9.95, y - 10.15],
                color='black', linewidth=LW)
        D.draw_earth_symbol(ax, x + 0.25, y - 10.25, "", fs)
        self.components_count += 7
        self._bay_label(ax, x, num, name)

    def _bay_coupler(self, ax, x, name, cidx=1):
        y, fs = self.bay_y, self.fs
        ax.plot([x - .2, x - .2], [y - .3, self.bus1_y],
                color='black', linewidth=LW)
        ax.plot([x + .7, x + .7], [y - .3, self.bus2_y],
                color='black', linewidth=LW)
        ax.plot([x - .2, x - .2], [y - 4, y - 1.5],
                color='black', linewidth=LW)
        ax.plot([x + .7, x + .7], [y - 4, y - 1.5],
                color='black', linewidth=LW)
        D.draw_isolator(ax, x - .2, y - .3, f"C{cidx}-89A", fs)
        D.draw_isolator(ax, x + .7, y - .3, f"C{cidx}-89B", fs)
        D.earth_sh(ax, x - .2, y - .5, f"C{cidx}-89AE", fs)
        D.earth_sh(ax, x + .7, y - .5, f"C{cidx}-89BE", fs)
        D.draw_ct(ax, x - .2, y - 2.5, f"C{cidx}-CT1", fs)
        D.draw_ct(ax, x + .7, y - 2.5, f"C{cidx}-CT2", fs)
        D.draw_breaker_coupler(ax, x + 0.25, y - 4, f"C{cidx}-52", fs)
        self.components_count += 7
        ax.text(x + .25, y - 11.4, name, ha='center', va='top',
                fontsize=fs + 1)

    # ------------------------------------------------------------------
    def _draw_bus_aux(self, ax, x_end):
        """Bus VTs: B1 near the LEFT, B2 near the RIGHT (as before)."""
        fs = self.fs

        def one(xb, yb, tag):
            ax.plot([xb, xb], [yb, yb - 0.4], color='black', linewidth=LW)
            D.draw_isolator(ax, xb, yb - 0.4, f"{tag}-89V", fs)
            D.earth_sh(ax, xb, yb - 0.7, f"{tag}-89E", fs)
            D.draw_bus_vt(ax, xb, yb - 1.6, f"{tag} VT", fs)
            self.components_count += 3

        one(self.bus_left + 1.0, self.bus1_y, "B1")
        if self.is_double:
            one(x_end - 0.7, self.bus2_y, "B2")

    # ------------------------------------------------------------------
    def _draw_buses(self, ax, n_bays):
        p = self.params
        bl = self.bus_left
        # symmetric margins: right end mirrors the left margin (=2)
        x_end = self.x_start + (n_bays - 1) * self.gap + (self.x_start - bl)
        if self.is_double:
            x_end += 0.5
        hv = int(p.hv_voltage)
        fs = self.fs

        ka = p.bus_fault_ka
        sec = p.bus_fault_sec
        ka_s = f"{int(ka)}" if float(ka).is_integer() else f"{ka}"
        sec_s = f"{int(sec)}" if float(sec).is_integer() else f"{sec}"
        rating = f"{hv}kV, {ka_s}kA, {sec_s}Sec"

        is_sec = (self.is_double
                  and p.configuration == 'double_bus_sectionalizer'
                  and n_bays > 1)

        # Single combined rating label (both buses identical) top-left
        ax.text(bl, self.bus1_y + 0.6, f"Bus Rating: {rating}",
                fontsize=fs + 2, color='black', fontweight='bold',
                ha='left', va='center')

        def bus_id(txt, y_above):
            yy = (self.bus1_y + 0.28) if y_above else (self.bus2_y - 0.32)
            ax.text(bl, yy, txt, fontsize=fs + 1, color='black',
                    fontweight='bold', ha='left', va='center')

        def split_bus(yb, s_label):
            xm = self.x_start + self._split_index * self.gap - 0.75
            ax.plot([bl, xm - 0.45], [yb, yb], color='black', linewidth=BUS_LW)
            ax.plot([xm + 0.45, x_end], [yb, yb], color='black',
                    linewidth=BUS_LW)
            ax.plot([xm - 0.45, xm - 0.28], [yb, yb], color='black',
                    linewidth=LW)
            ax.plot([xm + 0.28, xm + 0.45], [yb, yb], color='black',
                    linewidth=LW)
            D.draw_isolator_h(ax, xm, yb, s_label, fs)
            self.components_count += 1
            return xm

        if is_sec:
            sec2 = int(getattr(p, 'sectionalizer_count', 2)) >= 2
            xm1 = split_bus(self.bus1_y, "89S-1")
            bus_id("BUS-1A", True)
            ax.text(xm1 + 0.6, self.bus1_y + 0.28, "BUS-1B",
                    fontsize=fs + 1, color='black', fontweight='bold',
                    ha='left', va='center')
            if sec2:
                xm2 = split_bus(self.bus2_y, "89S-2")
                bus_id("BUS-2A", False)
                ax.text(xm2 + 0.6, self.bus2_y - 0.32, "BUS-2B",
                        fontsize=fs + 1, color='black', fontweight='bold',
                        ha='left', va='center')
            else:
                ax.plot([bl, x_end], [self.bus2_y, self.bus2_y],
                        color='black', linewidth=BUS_LW)
                bus_id("BUS-2", False)
        else:
            ax.plot([bl, x_end], [self.bus1_y, self.bus1_y],
                    color='black', linewidth=BUS_LW)
            bus_id("BUS-1", True)
            if self.is_double:
                ax.plot([bl, x_end], [self.bus2_y, self.bus2_y],
                        color='black', linewidth=BUS_LW)
                bus_id("BUS-2", False)
        return x_end

    # ------------------------------------------------------------------
    # PAGE FURNITURE (cm coordinates, true scale)
    # ------------------------------------------------------------------
    def _mini(self, pg, key, cx, cy):
        """Compact HORIZONTAL legend glyphs (~1.6 cm wide) — rotated so the
        conductor runs left-to-right, giving a neat low-height row."""
        LWm = 0.9

        def ln(x1, y1, x2, y2):
            pg.plot([x1, x2], [y1, y2], color='black', linewidth=LWm)

        if key == 'isolator':
            ln(cx - 0.8, cy, cx - 0.28, cy)
            pg.add_patch(mpatches.Arc((cx - 0.22, cy), 0.12, 0.12,
                                      angle=0, theta1=0, theta2=360,
                                      color='black', linewidth=LWm))
            pg.add_patch(mpatches.Arc((cx + 0.22, cy), 0.12, 0.12,
                                      angle=0, theta1=0, theta2=360,
                                      color='black', linewidth=LWm))
            ln(cx - 0.18, cy - 0.16, cx + 0.2, cy + 0.16)  # open blade
            ln(cx + 0.28, cy, cx + 0.8, cy)
        elif key == 'earth':
            ln(cx - 0.8, cy, cx - 0.05, cy)
            ln(cx - 0.2, cy + 0.16, cx + 0.15, cy - 0.16)  # blade
            ln(cx + 0.25, cy + 0.28, cx + 0.25, cy - 0.28)
            ln(cx + 0.4, cy + 0.18, cx + 0.4, cy - 0.18)
            ln(cx + 0.55, cy + 0.09, cx + 0.55, cy - 0.09)
        elif key == 'breaker':
            pg.add_patch(mpatches.Rectangle((cx - 0.3, cy - 0.2), 0.6, 0.4,
                                            fill=False, edgecolor='black',
                                            linewidth=LWm))
            ln(cx - 0.8, cy, cx - 0.3, cy)
            ln(cx + 0.3, cy, cx + 0.8, cy)
        elif key == 'ct':
            ln(cx - 0.8, cy, cx + 0.8, cy)
            pg.add_patch(mpatches.Arc((cx - 0.16, cy + 0.02), 0.5, 0.32,
                                      angle=90, theta1=80, theta2=280,
                                      color='black', linewidth=LWm))
            pg.add_patch(mpatches.Arc((cx + 0.16, cy + 0.02), 0.5, 0.32,
                                      angle=90, theta1=80, theta2=280,
                                      color='black', linewidth=LWm))
        elif key == 'cvt':
            # CVT = capacitor divider (stacked plate pairs) + winding coil
            ln(cx - 0.8, cy, cx - 0.55, cy)
            for j in range(3):  # three capacitor plate pairs
                xp = cx - 0.55 + j * 0.22
                ln(xp, cy + 0.26, xp, cy - 0.26)
                ln(xp + 0.08, cy + 0.26, xp + 0.08, cy - 0.26)
                if j < 2:
                    ln(xp + 0.08, cy, xp + 0.22, cy)
            ln(cx + 0.19, cy, cx + 0.34, cy)
            for k in range(3):   # winding coil
                pg.add_patch(mpatches.Arc((cx + 0.34 + k * 0.15, cy),
                                          0.2, 0.15, angle=90,
                                          theta1=80, theta2=280,
                                          color='black', linewidth=LWm))
        elif key == 'vt':
            # VT = CVT without capacitance → winding coil only (matches
            # the bus-VT drawing: bushing arc pair + coil, NO cap plates)
            ln(cx - 0.8, cy, cx - 0.5, cy)
            pg.add_patch(mpatches.Arc((cx - 0.38, cy), 0.24, 0.34,
                                      angle=0, theta1=270, theta2=90,
                                      color='black', linewidth=LWm))
            pg.add_patch(mpatches.Arc((cx - 0.14, cy), 0.24, 0.34,
                                      angle=0, theta1=270, theta2=90,
                                      color='black', linewidth=LWm))
            ln(cx, cy, cx + 0.12, cy)
            for k in range(4):
                pg.add_patch(mpatches.Arc((cx + 0.12 + k * 0.16, cy),
                                          0.22, 0.16, angle=90,
                                          theta1=80, theta2=280,
                                          color='black', linewidth=LWm))
        elif key == 'la':
            ln(cx - 0.8, cy, cx - 0.35, cy)
            pg.add_patch(mpatches.Rectangle((cx - 0.35, cy - 0.22), 0.6, 0.44,
                                            fill=False, edgecolor='black',
                                            linewidth=LWm))
            pg.add_patch(mpatches.Polygon(
                [[cx + 0.12, cy + 0.13], [cx - 0.18, cy],
                 [cx + 0.12, cy - 0.13]],
                closed=True, fill=True, color='black', linewidth=LWm))
            ln(cx + 0.25, cy, cx + 0.5, cy)
            ln(cx + 0.5, cy + 0.22, cx + 0.5, cy - 0.22)
            ln(cx + 0.6, cy + 0.14, cx + 0.6, cy - 0.14)
            ln(cx + 0.7, cy + 0.07, cx + 0.7, cy - 0.07)
        elif key == 'ict':
            # two overlapping windings side-by-side (horizontal)
            ln(cx - 0.8, cy, cx - 0.5, cy)
            pg.add_patch(mpatches.Arc((cx - 0.22, cy), 0.56, 0.56,
                                      angle=0, theta1=0, theta2=360,
                                      color='black', linewidth=LWm))
            pg.add_patch(mpatches.Arc((cx + 0.16, cy), 0.44, 0.44,
                                      angle=0, theta1=0, theta2=360,
                                      color='black', linewidth=LWm))
            ln(cx + 0.38, cy, cx + 0.8, cy)
        elif key == 'reactor':
            # mirrored coil (bumps face opposite the CT/VT windings)
            ln(cx - 0.8, cy, cx - 0.5, cy)
            for k in range(3):
                pg.add_patch(mpatches.Arc((cx - 0.3 + k * 0.25, cy),
                                          0.5, 0.35, angle=270,
                                          theta1=60, theta2=300,
                                          color='black', linewidth=LWm))
            ln(cx + 0.45, cy, cx + 0.8, cy)

    def _draw_legend(self, pg):
        """Legend as bordered tables, bottom-left (SYMBOL | DESCRIPTION)."""
        pg.text(1.3, 10.1, "LEGEND:", fontsize=8, fontweight='bold',
                va='bottom')
        t1 = [('isolator', "ISOLATOR (89)"),
              ('earth', "EARTH SWITCH"),
              ('breaker', "CIRCUIT BREAKER (52)"),
              ('ct', "CURRENT TRANSFORMER"),
              ('cvt', "CAPACITIVE VOLTAGE TRANSFORMER (CVT)")]
        t2 = [('vt', "POTENTIAL / BUS VT"),
              ('la', "LIGHTNING ARRESTOR"),
              ('ict', "POWER TRANSFORMER (ICT)"),
              ('reactor', "SHUNT REACTOR")]
        row_h = 1.15
        top = 9.6

        def table(x0, x1, items):
            n = len(items)
            y0 = top - n * row_h
            pg.add_patch(mpatches.Rectangle((x0, y0), x1 - x0, n * row_h,
                                            fill=False, edgecolor='black',
                                            linewidth=1.0))
            pg.plot([x0 + 2.6, x0 + 2.6], [y0, top],
                    color='black', linewidth=0.6)
            for r in range(1, n):
                pg.plot([x0, x1], [top - r * row_h] * 2,
                        color='black', linewidth=0.6)
            for r, (key, desc) in enumerate(items):
                cy = top - r * row_h - row_h / 2
                self._mini(pg, key, x0 + 1.3, cy)
                pg.text(x0 + 2.85, cy, desc, fontsize=6,
                        va='center', ha='left')

        table(1.2, 12.8, t1)
        table(13.2, 24.8, t2)

    def _draw_frame_and_title(self, pg):
        """A3 border + reference-style title block, bottom-right (cm)."""
        p = self.params
        pw = getattr(self, 'page_w', PAGE_MIN_W)
        pg.add_patch(mpatches.Rectangle((0.7, 0.7), pw - 1.4,
                                        PAGE_H - 1.4, fill=False,
                                        edgecolor='black', linewidth=1.6))
        pg.add_patch(mpatches.Rectangle((1.0, 1.0), pw - 2.0,
                                        PAGE_H - 2.0, fill=False,
                                        edgecolor='black', linewidth=0.7))

        tb_x1 = pw - 1.0
        tb_x0 = tb_x1 - 15.4
        rows, rh = 5, 1.2
        tb_y0 = 1.2
        tb_y1 = tb_y0 + rows * rh
        pg.add_patch(mpatches.Rectangle((tb_x0, tb_y0), tb_x1 - tb_x0,
                                        rows * rh, fill=False,
                                        edgecolor='black', linewidth=1.0))
        for r in range(1, rows):
            pg.plot([tb_x0, tb_x1], [tb_y0 + r * rh] * 2,
                    color='black', linewidth=0.6)
        pg.plot([tb_x0 + 3.0, tb_x0 + 3.0], [tb_y0, tb_y1],
                color='black', linewidth=0.6)
        # vertical divider segregating the DATE / SCALE columns (rows 4-5)
        pg.plot([tb_x0 + 8.6, tb_x0 + 8.6], [tb_y0, tb_y0 + 2 * rh],
                color='black', linewidth=0.6)

        date_s = datetime.date.today().strftime("%d.%m.%Y")
        lab_x, val_x = tb_x0 + 0.2, tb_x0 + 3.3
        mid_x = tb_x0 + 8.8

        def cell(cx, cy, t, bold=False, size=6):
            pg.text(cx, cy, t, fontsize=size, va='center', ha='left',
                    fontweight='bold' if bold else 'normal')

        def yr(i):
            return tb_y1 - (i - 0.5) * rh

        cell(lab_x, yr(1), "CLIENT", True)
        cell(val_x, yr(1), p.client or "-")
        cell(lab_x, yr(2), "PROJECT", True)
        cell(val_x, yr(2), p.project or "-")
        cell(lab_x, yr(3), "TITLE", True)
        cell(val_x, yr(3), p.title_text or "SINGLE LINE DIAGRAM")
        cell(lab_x, yr(4), "DRAWN", True)
        cell(val_x, yr(4), p.drawn_by or "-")
        cell(mid_x, yr(4), f"DATE {date_s}")
        cell(lab_x, yr(5), "DRG.No", True)
        cell(val_x, yr(5), p.drg_no or "-")
        cell(mid_x, yr(5),
             f"SCALE N.T.S SHEET 01 OF 01 REV {p.rev or '1'}", size=5.5)

    # ------------------------------------------------------------------
    def render(self):
        p = self.params
        if (p.configuration == 'double_bus_coupler'
                and int(p.bus_coupler_count) != 1):
            raise ValueError(
                "No such configuration: 'Double Bus Bar with Coupler' "
                "supports exactly ONE bus coupler.")
        if (p.configuration == 'double_bus_sectionalizer'
                and int(p.bus_coupler_count) > 2):
            raise ValueError(
                "No such configuration: 'Double Bus Bar with Sectionalizer' "
                "supports at most TWO bus couplers.")

        bays = self._build_bays()
        n = max(len(bays), 1)
        self.fs = 5  # constant — bay size is now fixed on paper

        # True right end (mirrors left margin) — same formula as _draw_buses
        x_end_calc = (self.x_start + (n - 1) * self.gap
                      + (self.x_start - self.bus_left)
                      + (0.5 if self.is_double else 0.0))
        # Symmetric drawing window → SLD centered in its panel
        margin = 1.2
        self._dx0 = self.bus_left - margin
        self._dx1 = x_end_calc + margin

        # -- ADAPTIVE PAGE: fixed bay dimensions, width grows with bays --
        panel_w = (self._dx1 - self._dx0) * SLD_SX
        panel_h = 18.2 * SLD_SY
        page_w = max(PAGE_MIN_W, panel_w + 2.4)
        self.page_w = page_w
        self.fig = plt.figure(figsize=(page_w / 2.54, PAGE_H / 2.54))

        pg = self.fig.add_axes([0, 0, 1, 1])
        pg.set_xlim(0, page_w)
        pg.set_ylim(0, PAGE_H)
        pg.axis('off')
        self.ax_page = pg

        # -- SLD PANEL (classic presentation, fixed physical scale) --
        box = ((page_w - panel_w) / 2, 12.0, panel_w, panel_h)
        self.ax = self.fig.add_axes([box[0] / page_w, box[1] / PAGE_H,
                                     box[2] / page_w, box[3] / PAGE_H])
        ax = self.ax
        ax.set_facecolor('none')

        x_end = self._draw_buses(ax, n)
        self._draw_bus_aux(ax, x_end)

        ict_i = 0
        re_i = 0
        cpl_i = 0
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
                cpl_i += 1
                self._bay_coupler(ax, x, name, cpl_i)
            self.bays_drawn.append((btype, num, name))

        dx0, dx1 = self._dx0, self._dx1
        dy0, dy1 = -5.6, 12.6
        ax.set_xlim(dx0, dx1)
        ax.set_ylim(dy0, dy1)
        ax.axis('off')

        # SLD-panel -> page transform (used by DXF export)
        sx = box[2] / (dx1 - dx0)
        sy = box[3] / (dy1 - dy0)
        self._inset_tf = (sx, box[0] - dx0 * sx, sy, box[1] - dy0 * sy)

        # -- Headings on the page --
        cfg_label = {
            'single_bus': "SINGLE BUS BAR SCHEME",
            'double_bus_coupler': "DOUBLE BUS BAR WITH BUS COUPLER",
            'double_bus_sectionalizer':
                "DOUBLE BUS BAR WITH BUS SECTIONALIZER",
        }.get(p.configuration, "")
        date_str = datetime.date.today().isoformat()
        if p.title_text and str(p.title_text).strip():
            pg.text(page_w / 2, 27.7, p.title_text, fontsize=15,
                    va='center', ha='center', fontweight='bold')
        if p.substation_name and str(p.substation_name).strip():
            pg.text(page_w / 2, 26.5, p.substation_name, fontsize=11,
                    va='center', ha='center')
        pg.text(page_w / 2, 25.5,
                f"{cfg_label}   |   Generated: {date_str}",
                fontsize=7, va='center', ha='center', style='italic')

        self._draw_legend(pg)
        self._draw_frame_and_title(pg)
        return self.fig, self.ax

    # ------------------------------------------------------------------
    def export_pdf(self, target):
        if self.fig is None:
            self.render()
        # No bbox trim — preserve exact A3 sheet
        self.fig.savefig(target, format='pdf', dpi=self.params.dpi,
                         facecolor='white')

    def export_dxf(self, target):
        """target: filepath (str) or text stream. Exports BOTH panels in
        page (cm) coordinates so AutoCAD matches the sheet exactly."""
        if self.ax is None:
            self.render()
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        _export_axes_to_msp(msp, self.ax_page, (1.0, 0.0, 1.0, 0.0))
        _export_axes_to_msp(msp, self.ax, self._inset_tf)
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
        substation_name="400/220kV Standard Substation",
        hv_voltage=400, lv_voltage=220,
        configuration='double_bus_coupler',
        line_bay_count=4, transformer_bay_count=2,
        reactor_bay_count=1, bus_coupler_count=1,
        client="TEST CLIENT", project="TEST PROJECT",
        drawn_by="CC", drg_no="SLD-001",
    )
    fig, r = generate_sld(params)
    r.export_pdf("test_v3_a3.pdf")
    r.export_dxf("test_v3_a3.dxf")
    print(r.get_summary())
