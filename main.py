# Файл запуска

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from db.db import SessionLocal
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Модуль работы с партнёрами")

    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow(SessionLocal)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()