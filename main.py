"""
main.py
=======
Titik masuk aplikasi "Metode Iterasi" (Iterasi Titik Tetap).

Cara menjalankan:
   pip install -r requirements.txt
   python main.py
""

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> None:
    app QApplication(sys.argv)
    app.setStyle("Fusion")           # gaya dasar yang konsisten di semua OS
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()