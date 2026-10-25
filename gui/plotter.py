"""
gui/plotter.py
==============
Logika penggambaran grafik fungsi f(x) dengan Matplotlib.

Fitur visual:
  1. Kurva utama y = f(x).
  2. Titik akar (root, f(root)) dengan marker merah & anotasi koordinat.
  3. Titik pendekatan awal x0 pada kurva f(x).
  4. Sumbu X (y = 0) dan sumbu Y (x = 0).
  5. Navigasi interaktif: zoom (scroll), geser (drag), reset tampilan (klik ganda).
  6. Kurva otomatis dihitung ulang saat zoom/geser agar selalu tersambung rapi.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from backend.iteration_solver import ParsedFunction, format_number

EMPTY_XLIM = (-15.0, 15.0)
EMPTY_YLIM = (-20.0, 20.0)
CURVE_SAMPLES = 1500


def _comma_tick(value: float, _pos) -> str:
    """Label sumbu dengan koma sebagai pemisah desimal."""
    text = f"{value:.6g}"
    if text in ("-0", "0"):
        text = "0"
    return text.replace(".", ",")


class IterationPlotter:
    def __init__(self, figure: Figure, theme) -> None:
        self.fig = figure
        self.theme = theme
        self.ax = self.fig.add_subplot(111)
        self._home: Tuple[Tuple[float, float], Tuple[float, float]] = (EMPTY_XLIM, EMPTY_YLIM)
        self._drag: Optional[dict] = None
        self._state: Optional[dict] = None

        self._fn = None
        self._line: Optional[Line2D] = None

        self.fig.subplots_adjust(left=0.085, right=0.985, top=0.985, bottom=0.14)
        canvas = self.fig.canvas
        canvas.mpl_connect("scroll_event", self._on_scroll)
        canvas.mpl_connect("button_press_event", self._on_press)
        canvas.mpl_connect("motion_notify_event", self._on_motion)
        canvas.mpl_connect("button_release_event", self._on_release)
        self.clear()

    # ------------------------------------------------------------------ API
    def set_theme(self, theme) -> None:
        self.theme = theme
        if self._state is None:
            self.clear()
            return
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        self.plot(**self._state)
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)
        self._finish()

    def clear(self) -> None:
        self._state = None
        self._fn = None
        self._line = None
        self._reset_axes()
        self.ax.set_xlim(*EMPTY_XLIM)
        self.ax.set_ylim(*EMPTY_YLIM)
        self._home = (EMPTY_XLIM, EMPTY_YLIM)
        self._finish()

    def plot(
        self,
        f_func: ParsedFunction,
        x0: float,
        root: float,
        f_root: float,
        decimals: int,
    ) -> None:
        """Gambar kurva f(x), titik awal x0, dan titik akar."""
        t = self.theme
        self._state = dict(
            f_func=f_func,
            x0=x0,
            root=root,
            f_root=f_root,
            decimals=decimals,
        )
        self._reset_axes()

        # ---- Tentukan rentang sumbu x & y awal ----
        span = abs(root - x0) or 4.0
        x_lo = min(x0, root) - 0.5 * span
        x_hi = max(x0, root) + 0.5 * span

        # Usahakan memuat x = 0 jika dekat
        if 0 < x_lo < 2 * span:
            x_lo = -0.15 * span
        if x_hi < 0 and -x_hi < 2 * span:
            x_hi = 0.15 * span

        # Evaluasi rentang y di sekitar [x_lo, x_hi]
        xs = np.linspace(x_lo, x_hi, 900)
        ys = f_func.vector(xs)
        finite = ys[np.isfinite(ys)]
        if finite.size:
            lo, hi = np.percentile(finite, [2, 98])
        else:
            lo, hi = -2.0, 2.0

        lo = min(lo, 0.0, f_root)
        hi = max(hi, 0.0, f_root)
        pad_y = 0.35 * ((hi - lo) or 1.0)
        y_lo, y_hi = lo - pad_y, hi + pad_y

        # ---- Kurva f(x) ----
        self._fn = f_func.vector
        (self._line,) = self.ax.plot(
            [], [],
            color=t.plot_curve,
            linewidth=2.4,
            zorder=3,
        )

        # ---- Titik pendekatan awal (x0) ----
        try:
            fx0 = f_func.scalar(x0)
        except Exception:
            fx0 = 0.0
        if math.isfinite(fx0):
            self.ax.plot([x0], [fx0], "o", color="#F59E0B" if t.name == "light" else "#FBBF24",
                         markersize=7, zorder=5)
            self.ax.annotate(
                f"x₀ = {format_number(x0, decimals)}",
                xy=(x0, fx0),
                xytext=(8, -14),
                textcoords="offset points",
                color=t.plot_label,
                fontsize=8.5,
                zorder=6,
            )

        # ---- Titik akar (root, f_root) ----
        self.ax.plot([root], [f_root], "o", color=t.plot_root, markersize=9, zorder=6)
        self.ax.annotate(
            f"Akar ({format_number(root, decimals)}; {format_number(f_root, decimals)})",
            xy=(root, f_root),
            xytext=(10, 12),
            textcoords="offset points",
            color=t.plot_label,
            fontsize=9,
            fontweight="bold",
            zorder=7,
        )

        self.ax.set_xlim(x_lo, x_hi)
        self.ax.set_ylim(y_lo, y_hi)
        self._home = ((x_lo, x_hi), (y_lo, y_hi))

        # ---- Legend di bawah plot ----
        handles = [
            Line2D([0], [0], color=t.plot_curve, linewidth=2.4),
            Line2D([0], [0], marker="o", color="none",
                   markerfacecolor="#F59E0B" if t.name == "light" else "#FBBF24",
                   markeredgecolor="#F59E0B" if t.name == "light" else "#FBBF24", markersize=7),
            Line2D([0], [0], marker="o", color="none",
                   markerfacecolor=t.plot_root, markeredgecolor=t.plot_root, markersize=9),
        ]
        labels = [
            f"f(x) = {f_func.display}",
            f"x₀ = {format_number(x0, decimals)}",
            f"Akar = {format_number(root, decimals)}",
        ]
        legend = self.fig.legend(
            handles, labels, loc="lower left", bbox_to_anchor=(0.02, 0.0),
            frameon=False, fontsize=9, labelcolor=t.plot_label, ncol=3,
        )
        for txt in legend.get_texts():
            txt.set_fontweight("bold")

        self._finish()

    # ------------------------------------------------------------- internal
    def _reset_axes(self) -> None:
        t = self.theme
        for leg in list(self.fig.legends):
            leg.remove()
        self.ax.clear()
        self.fig.patch.set_facecolor(t.plot_bg)
        self.ax.set_facecolor(t.plot_bg)

        self.ax.minorticks_on()
        self.ax.set_axisbelow(True)
        self.ax.xaxis.set_major_formatter(FuncFormatter(_comma_tick))
        self.ax.yaxis.set_major_formatter(FuncFormatter(_comma_tick))
        self.ax.grid(which="major", color=t.plot_axis, alpha=0.55, linewidth=0.8)
        self.ax.grid(which="minor", color=t.plot_axis, alpha=0.25, linewidth=0.4, linestyle=":")

        self.ax.axhline(0, color=t.plot_axis, linewidth=1.1, alpha=0.85)
        self.ax.axvline(0, color=t.plot_axis, linewidth=1.1, alpha=0.85)

        for spine in self.ax.spines.values():
            spine.set_color(t.plot_axis)
            spine.set_linewidth(1.0)

        self.ax.tick_params(colors=t.plot_label, labelsize=9)

    def _update_curve(self) -> None:
        """Hitung ulang kurva f(x) untuk rentang x yang sedang terlihat."""
        if self._line is None or self._fn is None:
            return
        x_lo, x_hi = self.ax.get_xlim()
        if not (math.isfinite(x_lo) and math.isfinite(x_hi)) or x_lo >= x_hi:
            return
        xs = np.linspace(x_lo, x_hi, CURVE_SAMPLES)
        ys = self._fn(xs)
        self._line.set_data(xs, ys)

    def _finish(self) -> None:
        self._update_curve()
        self.fig.canvas.draw_idle()

    # ----------------------------------------------------------- interaksi
    def _on_scroll(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        scale = 0.82 if event.button == "up" else (1.0 / 0.82)
        cur_x = self.ax.get_xlim()
        cur_y = self.ax.get_ylim()
        x, y = event.xdata, event.ydata

        new_x = (x - (x - cur_x[0]) * scale, x + (cur_x[1] - x) * scale)
        new_y = (y - (y - cur_y[0]) * scale, y + (cur_y[1] - y) * scale)
        self.ax.set_xlim(new_x)
        self.ax.set_ylim(new_y)
        self._finish()

    def _on_press(self, event) -> None:
        if event.inaxes != self.ax:
            return
        if event.dblclick:
            self.ax.set_xlim(*self._home[0])
            self.ax.set_ylim(*self._home[1])
            self._finish()
            return
        if event.button == 1:
            self._drag = {
                "x": event.xdata, "y": event.ydata,
                "xlim": self.ax.get_xlim(), "ylim": self.ax.get_ylim(),
            }

    def _on_motion(self, event) -> None:
        if not self._drag or event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None:
            return
        dx = event.xdata - self._drag["x"]
        dy = event.ydata - self._drag["y"]
        x0, x1 = self._drag["xlim"]
        y0, y1 = self._drag["ylim"]
        self.ax.set_xlim(x0 - dx, x1 - dx)
        self.ax.set_ylim(y0 - dy, y1 - dy)
        self._finish()

    def _on_release(self, _event) -> None:
        self._drag = None
