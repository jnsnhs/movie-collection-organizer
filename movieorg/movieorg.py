from PySide6.QtWidgets import QApplication

from .gui.mainwindow import MainWindow


class Application(QApplication):

    def __init__(self) -> None:
        super().__init__()
        self.main_window = MainWindow()
        self.main_window.show()
