"""
gui/result_panel.py
===================
Panel TENGAH-ATAS: "Hasil Perhitungan"
(Akar x, f(x), nomor iterasi saat validasi terpenuhi, dan kesimpulan).
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from backend.iteration_solver import ResultSummary


class ResultPanel(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 16, 24, 18)
        outer.setSpacing(6)

        title = QLabel("Hasil Perhitungan")
        title.setObjectName("cardTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(2, 1)
        outer.addLayout(grid)

        self.values: dict[str, QLabel] = {}
        for row, (key, name) in enumerate([
            ("root", "Akar (x)"), ("f_root", "f(x)"),
            ("iteration", "Iterasi"), ("conclusion", "Kesimpulan"),
        ]):
            name_lbl = QLabel(name)
            name_lbl.setObjectName("resultName")
            colon = QLabel(":")
            colon.setObjectName("resultName")
            value = QLabel("")
            value.setObjectName("conclusion" if key == "conclusion" else "resultValue")
            if key == "conclusion":
                value.setWordWrap(True)
            grid.addWidget(name_lbl, row, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(colon, row, 1, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(value, row, 2, Qt.AlignmentFlag.AlignTop)
            self.values[key] = value

        self.setMinimumHeight(170)

    def show_result(self, summary: ResultSummary) -> None:
        self.values["root"].setText(summary.root_text)
        self.values["f_root"].setText(summary.f_root_text)
        self.values["iteration"].setText(summary.iteration_text)
        self.values["conclusion"].setText(summary.conclusion)

    def clear(self) -> None:
        for label in self.values.values():
            label.setText("")
