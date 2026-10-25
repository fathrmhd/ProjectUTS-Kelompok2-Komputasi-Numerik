"""
gui/theme.py
============
Design system aplikasi: palet warna Mode Terang & Mode Gelap, serta
penyusun stylesheet Qt (QSS). Semua warna mengikuti spesifikasi.

Catatan: "Opacity 25%" / "75%" pada spesifikasi diwujudkan dengan warna rgba().
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Theme:
    name: str
    # --- umum ---
    bg: str                 # latar belakang aplikasi
    panel: str              # latar kartu/panel
    text: str               # judul & label
    hint: str               # teks petunjuk (opacity 75%)
    # --- form ---
    field_bg: str
    field_border: str
    placeholder_rgba: Tuple[int, int, int, int]   # placeholder (opacity 25%)
    # --- tombol ---
    btn: str
    btn_text: str
    btn_hover: str
    btn_disabled: str       # latar tombol non-aktif (opacity 25%)
    # --- hasil & tabel ---
    root_value: str         # warna angka hasil akar
    header_bg: str
    header_text: str
    cell_border: str
    row_a: str
    row_b: str
    hl_bg: str              # sorotan baris solusi (TRUE pertama)
    hl_text: str
    toggle_icon: str        # warna ikon toggle mode
    # --- grafik matplotlib ---
    plot_bg: str
    plot_axis: str
    plot_curve: str
    plot_root: str
    plot_label: str


LIGHT = Theme(
    name="light",
    bg="#F8FAFC", panel="#FFFFFF", text="#0F172A", hint="rgba(15, 23, 42, 191)",
    field_bg="#FFFFFF", field_border="#CBD5E1", placeholder_rgba=(0, 0, 0, 64),
    btn="#2563EB", btn_text="#FFFFFF", btn_hover="#1D4ED8", btn_disabled="rgba(37, 99, 235, 64)",
    root_value="#16A34A", header_bg="#F1F5F9", header_text="#0F172A", cell_border="#E2E8F0",
    row_a="#FFFFFF", row_b="#F8FAFC", hl_bg="#DBEAFE", hl_text="#1E40AF",
    toggle_icon="#000000",
    plot_bg="#FFFFFF", plot_axis="#94A3B8", plot_curve="#2563EB",
    plot_root="#DC2626", plot_label="#0F172A",
)

DARK = Theme(
    name="dark",
    bg="#0F172A", panel="#1E293B", text="#F8FAFC", hint="rgba(226, 232, 240, 191)",
    field_bg="#334155", field_border="#475569", placeholder_rgba=(255, 255, 255, 64),
    btn="#2563EB", btn_text="#FFFFFF", btn_hover="#3B82F6", btn_disabled="rgba(37, 99, 235, 64)",
    root_value="#4ADE80", header_bg="#334155", header_text="#F8FAFC", cell_border="#475569",
    row_a="#1E293B", row_b="#0F172A", hl_bg="#1E3A8A", hl_text="#93C5FD",
    toggle_icon="#FFFFFF",
    plot_bg="#1E293B", plot_axis="#475569", plot_curve="#38BDF8",
    plot_root="#EF4444", plot_label="#F8FAFC",
)


def build_stylesheet(t: Theme) -> str:
    """Bangun stylesheet global dari sebuah tema."""
    return f"""
    * {{
        font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
        font-size: 13px;
    }}
    QMainWindow, QWidget#central {{ background: {t.bg}; }}

    /* ---------- kartu / panel ---------- */
    QFrame#card {{ background: {t.panel}; border: none; border-radius: 28px; }}
    QLabel {{ background: transparent; color: {t.text}; }}
    QLabel#appTitle {{ font-size: 46px; font-weight: 800; }}
    QLabel#credit {{ font-size: 12px; }}
    QLabel#cardTitle {{ font-size: 21px; font-weight: 700; }}
    QLabel#fieldLabel {{ font-size: 12px; font-weight: 700; margin-top: 6px; }}
    QLabel#hint {{ font-size: 9px; color: {t.hint}; }}
    QLabel#guideTitle {{ font-size: 11px; font-weight: 600; color: {t.text}; }}
    QLabel#guide {{ font-size: 9px; color: {t.hint}; }}
    QLabel#resultName {{ font-size: 12px; font-weight: 700; }}
    QLabel#resultValue {{ font-size: 12px; font-weight: 700; color: {t.root_value}; }}
    QLabel#conclusion {{ font-size: 12px; font-weight: 600; }}

    /* ---------- textfield ---------- */
    QLineEdit {{
        background: {t.field_bg}; color: {t.text};
        border: 1px solid {t.field_border}; border-radius: 8px;
        padding: 7px 10px; font-size: 13px;
        selection-background-color: {t.btn}; selection-color: #FFFFFF;
    }}
    QLineEdit:focus {{ border: 1px solid {t.btn}; }}

    /* ---------- combobox ---------- */
    QComboBox {{
        background: {t.field_bg}; color: {t.text};
        border: 1px solid {t.field_border}; border-radius: 8px;
        padding: 6px 10px; font-size: 12px; font-weight: 600;
    }}
    QComboBox:focus {{ border: 1px solid {t.btn}; }}
    QComboBox::drop-down {{
        border: none; width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background: {t.panel}; color: {t.text};
        selection-background-color: {t.btn}; selection-color: #FFFFFF;
        border: 1px solid {t.field_border}; border-radius: 6px;
        padding: 4px;
    }}

    /* ---------- tombol ---------- */
    QPushButton {{
        background: {t.btn}; color: {t.btn_text}; border: none;
        border-radius: 10px; padding: 9px 14px; font-weight: 700;
    }}
    QPushButton:hover {{ background: {t.btn_hover}; }}
    QPushButton:disabled {{ background: {t.btn_disabled}; color: {t.btn_text}; }}
    QPushButton#themeToggle {{ background: transparent; border: none; padding: 0; }}
    QPushButton#themeToggle:hover {{ background: transparent; }}

    /* ---------- tabel ---------- */
    QTableWidget {{
        background: {t.panel}; border: 1px solid {t.cell_border};
        gridline-color: {t.cell_border}; outline: 0;
    }}
    QHeaderView {{ background: {t.header_bg}; }}
    QHeaderView::section {{
        background: {t.header_bg}; color: {t.header_text};
        border: none; border-right: 1px solid {t.cell_border};
        border-bottom: 1px solid {t.cell_border};
        padding: 4px; font-family: "Consolas", "Menlo", "DejaVu Sans Mono", monospace;
        font-size: 14px;
    }}

    /* ---------- scrollbar ---------- */
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
    QScrollBar::handle:vertical {{
        background: {t.cell_border}; border-radius: 5px; min-height: 28px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
    QScrollBar::handle:horizontal {{
        background: {t.cell_border}; border-radius: 5px; min-width: 28px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

    /* ---------- kotak pesan ---------- */
    QMessageBox {{ background: {t.panel}; }}
    QMessageBox QLabel {{ color: {t.text}; }}
    """
