"""
gui/main_window.py
==================
Jendela utama desktop: header (toggle tema, judul, kredit), tata letak 3 kolom,
dan penghubung (controller) antara panel-panel GUI dengan backend.

Tata letak:
  [Panel Input] | [Hasil Perhitungan ] | [Grafik Fungsi]
                | [Tabel Iterasi      ] |
"""

from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QPushButton, QVBoxLayout, QWidget,
)

from backend.iteration_solver import InputError, parse_inputs, solve, summarize
from gui.graph_panel import GraphPanel
from gui.input_panel import InputPanel
from gui.result_panel import ResultPanel
from gui.table_panel import TablePanel
from gui.theme import DARK, LIGHT, build_stylesheet


class ThemeToggleButton(QPushButton):
    """Tombol ikon: bulan (saat Mode Terang) / matahari (saat Mode Gelap)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("themeToggle")
        self.setFixedSize(QSize(44, 44))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Ganti mode terang / gelap")
        self._dark = False
        self._color = QColor("#000000")

    def set_mode(self, dark: bool, icon_color: str) -> None:
        self._dark = dark
        self._color = QColor(icon_color)
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(44, 44)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QPointF(self.width() / 2, self.height() / 2)
        r = 13.0
        if not self._dark:
            outer = QPainterPath()
            outer.addEllipse(c, r, r)
            cut = QPainterPath()
            cut.addEllipse(QPointF(c.x() + r * 0.55, c.y() - r * 0.35), r * 0.85, r * 0.85)
            p.fillPath(outer.subtracted(cut), self._color)
        else:
            pen = QPen(self._color, 2.2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(c, r * 0.5, r * 0.5)
            for i in range(8):
                ang = i * math.pi / 4
                p1 = QPointF(c.x() + math.cos(ang) * r * 0.78, c.y() + math.sin(ang) * r * 0.78)
                p2 = QPointF(c.x() + math.cos(ang) * r * 1.05, c.y() + math.sin(ang) * r * 1.05)
                p.drawLine(p1, p2)
        p.end()


def _add_shadow(widget: QWidget) -> None:
    """Bayangan lembut di bawah kartu."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(26)
    effect.setOffset(0, 6)
    effect.setColor(QColor(0, 0, 0, 60))
    widget.setGraphicsEffect(effect)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Metode Iterasi")
        self.resize(1440, 900)
        self.setMinimumSize(1150, 720)
        self._theme = LIGHT

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 8, 14, 18)
        root.setSpacing(10)

        root.addLayout(self._build_header())

        # --- 3 kolom ---
        self.input_panel = InputPanel()
        self.result_panel = ResultPanel()
        self.table_panel = TablePanel()
        self.graph_panel = GraphPanel()

        body = QHBoxLayout()
        body.setSpacing(16)
        body.addWidget(self.input_panel, 0, Qt.AlignmentFlag.AlignTop)

        self.middle = QVBoxLayout()
        self.middle.setSpacing(16)
        self.middle.addWidget(self.result_panel, 0)
        self.middle.addWidget(self.table_panel, 1)
        self.middle.addStretch(0)
        body.addLayout(self.middle, 5)

        body.addWidget(self.graph_panel, 3)
        root.addLayout(body, 1)

        for card in (self.input_panel, self.result_panel, self.table_panel, self.graph_panel):
            _add_shadow(card)

        # --- sambungkan sinyal ---
        self.input_panel.calculate_requested.connect(self._on_calculate)
        self.input_panel.reset_requested.connect(self._on_reset)
        self.toggle_btn.clicked.connect(self._toggle_theme)
        self.table_panel.trim_changed.connect(self._on_table_trim_changed)

        self._apply_theme(LIGHT)

    # ------------------------------------------------------------ header
    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)

        self.toggle_btn = ThemeToggleButton()

        left = QWidget()
        left.setFixedWidth(190)
        left_lay = QHBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(self.toggle_btn, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        title = QLabel("Metode Iterasi")
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        credit = QLabel("Created By : Kelompok 2")
        credit.setObjectName("credit")
        credit.setFixedWidth(190)
        credit.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        header.addWidget(left)
        header.addWidget(title, 1)
        header.addWidget(credit)
        return header

    # ------------------------------------------------------------- tema
    def _toggle_theme(self) -> None:
        self._apply_theme(DARK if self._theme is LIGHT else LIGHT)

    def _apply_theme(self, theme) -> None:
        self._theme = theme
        self.setStyleSheet(build_stylesheet(theme))
        self.toggle_btn.set_mode(theme is DARK, theme.toggle_icon)
        self.input_panel.apply_theme(theme)
        self.table_panel.apply_theme(theme)
        self.graph_panel.apply_theme(theme)

    # ------------------------------------------------------------- tata letak tabel
    def _on_table_trim_changed(self, trimmed: bool) -> None:
        self.middle.setStretch(1, 0 if trimmed else 1)
        self.middle.setStretch(2, 1 if trimmed else 0)

    # ------------------------------------------------------------ aksi
    def _on_calculate(self) -> None:
        """Validasi input -> jalankan metode iterasi -> perbarui semua panel."""
        v = self.input_panel.values()
        try:
            inputs = parse_inputs(
                v["f_function"],
                v["g_function"],
                v["x0"],
                v["eps"],
                v["n"],
                v["decimals"],
            )
            result = solve(inputs)
        except InputError as err:
            QMessageBox.warning(self, "Input Tidak Valid", str(err))
            return

        self.result_panel.show_result(summarize(result))
        self.table_panel.set_result(result)
        self.graph_panel.show_result(result)
        self.input_panel.set_has_result(True)

    def _on_reset(self) -> None:
        """Kosongkan input, hasil, tabel, dan kembalikan grafik ke grid kosong."""
        self.input_panel.clear()
        self.result_panel.clear()
        self.table_panel.clear()
        self.graph_panel.clear()
        self.input_panel.set_has_result(False)
