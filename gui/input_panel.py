"""
gui/input_panel.py
==================
Panel KIRI: form input Metode Iterasi, pilihan cara menentukan g(x),
tombol [Hitung Akar] & [Reset], serta petunjuk penggunaan.
"""

from __future__ import annotations

from typing import Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout,
)

from backend.iteration_solver import derive_g_methods, superscript_exponents

FIELDS = [
    ("f_function", "Fungsi F(X)", "Masukkan Fungsi F(X)", "Contoh: x**2 - 6x - 2"),
    ("g_function", "Fungsi g(x)", "Masukkan Fungsi g(x)", "Contoh: sqrt(6x + 2)"),
    ("x0", "Pendekatan Awal (x₀)", "Masukkan Nilai x₀", "Contoh: 4"),
    ("eps", "Toleransi Error (e)", "Masukkan Toleransi Error", "Contoh: 0,001"),
    ("n", "Iterasi Maksimum (N)", "Masukkan Iterasi Maksimum", "Contoh: 10 (Maks : 100)"),
    ("decimals", "Jumlah Angka Desimal", "Masukkan Jumlah Angka Desimal", "Contoh: 4 (Maks : 6)"),
]

GUIDE = [
    "· Gunakan x untuk variabel dan (*) sebagai perkalian",
    "· Gunakan / untuk pembagian dan (**) untuk pangkat",
    "· Pemisah desimal boleh koma (,) atau titik (.)",
    "· Ketik ** lalu angka, otomatis jadi pangkat (x**2 → x²)",
    "· Pilih Cara 1, 2, atau 3 untuk otomatis mengisi g(x)",
]


class InputPanel(QFrame):
    calculate_requested = pyqtSignal()
    reset_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedWidth(292)
        self._has_result = False
        self.edits: Dict[str, QLineEdit] = {}
        self._syncing_g = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(2)

        title = QLabel("PANEL INPUT")
        title.setObjectName("cardTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(6)

        # --- field input & dropdown cara g(x) ---
        for key, label, placeholder, example in FIELDS:
            lab = QLabel(label)
            lab.setObjectName("fieldLabel")
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            edit.textChanged.connect(self.update_buttons)
            edit.returnPressed.connect(self._on_enter)
            hint = QLabel(example)
            hint.setObjectName("hint")

            layout.addWidget(lab)
            layout.addWidget(edit)
            layout.addWidget(hint)
            self.edits[key] = edit

            if key == "f_function":
                edit.textChanged.connect(self._on_f_changed)
                edit.textChanged.connect(lambda text: self._auto_superscript("f_function", text))

                # Sisipkan pilihan cara g(x) tepat setelah Fungsi F(X)
                combo_lab = QLabel("Pilihan Cara g(x)")
                combo_lab.setObjectName("fieldLabel")
                self.combo_cara = QComboBox()
                self.combo_cara.addItem("Manual (Ketik Sendiri)", "manual")
                self.combo_cara.addItem("Cara 1 : Isolasi x²  [x = √(…)]", "cara1")
                self.combo_cara.addItem("Cara 2 : Isolasi x   [x = (…)/b]", "cara2")
                self.combo_cara.addItem("Cara 3 : Faktorisasi [x = c/(ax+b)]", "cara3")
                self.combo_cara.currentIndexChanged.connect(self._on_cara_changed)

                layout.addWidget(combo_lab)
                layout.addWidget(self.combo_cara)

            elif key == "g_function":
                edit.textChanged.connect(self._on_g_typed)
                edit.textChanged.connect(lambda text: self._auto_superscript("g_function", text))

        # --- tombol aksi ---
        layout.addSpacing(8)
        row = QHBoxLayout()
        row.setSpacing(10)
        self.btn_calc = QPushButton("Hitung Akar")
        self.btn_reset = QPushButton("Reset")
        for btn in (self.btn_calc, self.btn_reset):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            row.addWidget(btn)
        self.btn_calc.clicked.connect(self.calculate_requested.emit)
        self.btn_reset.clicked.connect(self.reset_requested.emit)
        layout.addLayout(row)

        # --- petunjuk penggunaan ---
        layout.addSpacing(10)
        guide_title = QLabel("Cara Penggunaan:")
        guide_title.setObjectName("guideTitle")
        layout.addWidget(guide_title)
        for line in GUIDE:
            g = QLabel(line)
            g.setObjectName("guide")
            g.setWordWrap(True)
            layout.addWidget(g)

        self.update_buttons()

    # ------------------------------------------------------------------ API
    def values(self) -> Dict[str, str]:
        return {key: edit.text() for key, edit in self.edits.items()}

    def is_complete(self) -> bool:
        required = ["g_function", "x0", "eps", "n", "decimals"]
        return all(self.edits[k].text().strip() for k in required)

    def has_text(self) -> bool:
        return any(edit.text().strip() for edit in self.edits.values())

    def set_has_result(self, value: bool) -> None:
        self._has_result = value
        self.update_buttons()

    def clear(self) -> None:
        self.combo_cara.blockSignals(True)
        self.combo_cara.setCurrentIndex(0)
        self.combo_cara.blockSignals(False)

        for edit in self.edits.values():
            edit.blockSignals(True)
            edit.clear()
            edit.blockSignals(False)
        self.update_buttons()
        self.edits["f_function"].setFocus()

    def update_buttons(self) -> None:
        self.btn_calc.setEnabled(self.is_complete())
        self.btn_reset.setEnabled(self.has_text() or self._has_result)

    def apply_theme(self, theme) -> None:
        for edit in self.edits.values():
            palette = edit.palette()
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(*theme.placeholder_rgba))
            edit.setPalette(palette)

    # ------------------------------------------------------------- internal
    def _apply_derived_g(self) -> None:
        idx = self.combo_cara.currentIndex()
        if idx <= 0:
            return
        f_text = self.edits["f_function"].text()
        methods = derive_g_methods(f_text)
        if not methods:
            return

        key = ["cara1", "cara2", "cara3"][idx - 1]
        val = methods.get(key, "")
        if val:
            self._syncing_g = True
            edit = self.edits["g_function"]
            edit.setText(superscript_exponents(val))
            self._syncing_g = False

    def _on_cara_changed(self, index: int) -> None:
        if index > 0:
            self._apply_derived_g()

    def _on_f_changed(self) -> None:
        if self.combo_cara.currentIndex() > 0:
            self._apply_derived_g()

    def _on_g_typed(self) -> None:
        if not self._syncing_g and self.combo_cara.currentIndex() > 0:
            # Bila pengguna mengedit g(x) manual, ubah status pilihan ke Manual
            self.combo_cara.blockSignals(True)
            self.combo_cara.setCurrentIndex(0)
            self.combo_cara.blockSignals(False)

    def _auto_superscript(self, key: str, text: str) -> None:
        new = superscript_exponents(text)
        if new == text:
            return
        edit = self.edits[key]
        pos = edit.cursorPosition() + len(new) - len(text)
        edit.blockSignals(True)
        edit.setText(new)
        edit.setCursorPosition(max(0, pos))
        edit.blockSignals(False)

    def _on_enter(self) -> None:
        if self.is_complete():
            self.calculate_requested.emit()
