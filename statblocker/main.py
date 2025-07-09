import sys
from PyQt5.QtWidgets import QApplication
from statblocker.controller.main_controller import MainController


def main():
    app = QApplication(sys.argv)
    main_window = MainController(app)
    main_window.run()
