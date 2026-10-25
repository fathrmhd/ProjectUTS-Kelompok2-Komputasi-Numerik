"""
gui/table_panel.py
==================
Panel TENGAH-BAWAH: "Tabel Iterasi" + tombol [Tampilkan Semua] / [Sembunyikan].

Aturan tampilan:
  - Default : baris r = 1 sampai baris TRUE pertama (baris solusi, disorot).
  - Klik [Tampilkan Semua] : seluruh iterasi sampai N, tombol menjadi [Sembunyikan].
  - Bila TRUE tidak ditemukan dalam N iterasi : semua baris tampil,
    baris terakhir (N) disorot sebagai baris solusi.
  - Bila baris yang tampil <= 15, tabel dipotong menyesuaikan isi.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from backend.iteration_solver import IterationResult, IterationRow, format_number
from gui.theme import LIGHT

HEADERS = ["r", "x", "g(x)", "f(x)", "e_tol", "validasi"]
ROW_HEIGHT = 24

TRIM_MAX_ROWS = 15                  # batas jumlah baris agar tabel dipotong
CARD_MARGINS = (24, 16, 24, 22)     # kiri, atas, kanan, bawah
CARD_SPACING = 8
QWIDGETSIZE_MAX = 16777215


class TablePanel(QFrame):
    trim_changed = pyqtSignal(bool)     # True bila tabel sedang dipotong

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self._theme = LIGHT
        self._result: Optional[IterationResult] = None
        self._show_all = False
        self._filled_rows = 0
        self._trimmed = False

        # font monospace untuk isi tabel
        self._mono = QFont()
        self._mono.setFamilies(["Consolas", "Menlo", "DejaVu Sans Mono", "Courier New"])
        self._mono.setStyleHint(QFont.StyleHint.Monospace)
        self._mono.setPointSize(10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*CARD_MARGINS)
        layout.setSpacing(CARD_SPACING)

        # --- baris judul + tombol di kanan atas ---
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        self._title = QLabel("Tabel Iterasi")
        self._title.setObjectName("cardTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_toggle = QPushButton("Tampilkan Semua")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setMinimumWidth(130)
        self.btn_toggle.setEnabled(False)
        self.btn_toggle.clicked.connect(self._toggle_show_all)
        spacer = QLabel()
        spacer.setFixedWidth(130)
        top.addWidget(spacer)
        top.addWidget(self._title, 1)
        top.addWidget(self.btn_toggle)
        layout.addLayout(top)

        # --- tabel ---
        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 48)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.table, 1)

    # ------------------------------------------------------------------ API
    def set_result(self, result: IterationResult) -> None:
        """Tampilkan hasil baru (mulai dari mode ringkas)."""
        self._result = result
        self._show_all = False
        self._render()

    def clear(self) -> None:
        """Kosongkan tabel."""
        self._result = None
        self._show_all = False
        self._render()

    def apply_theme(self, theme) -> None:
        self._theme = theme
        self._render()

    # ------------------------------------------------------------- internal
    def _default_rows(self) -> List[IterationRow]:
        """Baris yang tampil pada mode ringkas."""
        if self._result is None:
            return []
        rows = self._result.rows
        if self._result.first_true is not None:
            return rows[: self._result.first_true + 1]
        return rows

    def _visible_rows(self) -> List[IterationRow]:
        if self._result is None:
            return []
        return self._result.rows if self._show_all else self._default_rows()

    def _toggle_show_all(self) -> None:
        self._show_all = not self._show_all
        self._render()

    def _header_height(self) -> int:
        h = self.table.horizontalHeader()
        return max(h.height(), h.sizeHint().height())

    def _top_row_height(self) -> int:
        return max(self._title.sizeHint().height(), self.btn_toggle.sizeHint().height())

    def _capacity(self) -> int:
        overhead = (CARD_MARGINS[1] + CARD_MARGINS[3] + CARD_SPACING
                    + self._top_row_height() + self._header_height() + 2)
        return max(8, (self.height() - overhead) // ROW_HEIGHT)

    def _render(self) -> None:
        t = self._theme
        rows = self._visible_rows()
        decimals = self._result.inputs.decimals if self._result else 4
        highlight = self._result.solution_index if self._result else -1

        # Potong tabel bila baris tampil <= 15
        trimmed = self._result is not None and len(rows) <= TRIM_MAX_ROWS
        if trimmed:
            total = len(rows)
            table_h = self._header_height() + total * ROW_HEIGHT + 2
            self.table.setFixedHeight(table_h)
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setMaximumHeight(CARD_MARGINS[1] + CARD_MARGINS[3] + CARD_SPACING
                                  + self._top_row_height() + table_h)
        else:
            self.table.setMinimumHeight(0)
            self.table.setMaximumHeight(QWIDGETSIZE_MAX)
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setMaximumHeight(QWIDGETSIZE_MAX)
            self._filled_rows = self._capacity()
            total = max(len(rows), self._filled_rows)

        self.table.setRowCount(total)

        for i in range(total):
            if i == highlight and i < len(rows):
                bg, fg = t.hl_bg, t.hl_text
            else:
                bg, fg = (t.row_a if i % 2 == 0 else t.row_b), t.text

            if i < len(rows):
                r = rows[i]
                cells = [
                    str(r.r),
                    format_number(r.x, decimals),
                    format_number(r.gx, decimals),
                    format_number(r.fx, decimals),
                    format_number(r.e_tol, decimals),
                    "TRUE" if r.valid else "FALSE",
                ]
            else:
                cells = [""] * len(HEADERS)

            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(self._mono)
                item.setBackground(QBrush(QColor(bg)))
                item.setForeground(QBrush(QColor(fg)))
                self.table.setItem(i, c, item)

        has_hidden = self._result is not None and len(self._result.rows) > len(self._default_rows())
        self.btn_toggle.setText("Sembunyikan" if self._show_all else "Tampilkan Semua")
        self.btn_toggle.setEnabled(has_hidden)

        if trimmed != self._trimmed:
            self._trimmed = trimmed
            self.trim_changed.emit(trimmed)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._trimmed and self._capacity() != self._filled_rows:
            self._render()
