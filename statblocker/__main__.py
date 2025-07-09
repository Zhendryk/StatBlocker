import sys
from PyQt5.QtWidgets import QApplication
from statblocker.controller.main_controller import MainController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainController(app)
    main_window.run()
