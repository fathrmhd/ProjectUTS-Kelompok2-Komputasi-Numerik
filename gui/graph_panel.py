"""
gui/graph_panel.py
==================
Panel KANAN: "Grafik Fungsi" - menanamkan canvas Matplotlib ke dalam Qt.
Menggambar grafik kurva f(x) dan titik akar.
"""

from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout

from backend.iteration_solver import IterationResult
from gui.plotter import IterationPlotter
from gui.theme import LIGHT


class GraphPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 16, 22, 26)
        layout.setSpacing(8)

        title = QLabel("Grafik Fungsi")
        title.setObjectName("cardTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.figure = Figure(figsize=(4.4, 5.2), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas, 1)

        self.plotter = IterationPlotter(self.figure, LIGHT)

    def show_result(self, result: IterationResult) -> None:
        """Gambar kurva f(x), titik awal x0, dan titik akar."""
        inp = result.inputs
        self.plotter.plot(
            f_func=inp.f_func,
            x0=inp.x0,
            root=result.root,
            f_root=result.f_root,
            decimals=inp.decimals,
        )

    def clear(self) -> None:
        """Reset canvas ke grid kosong awal."""
        self.plotter.clear()

    def apply_theme(self, theme) -> None:
        self.plotter.set_theme(theme)
