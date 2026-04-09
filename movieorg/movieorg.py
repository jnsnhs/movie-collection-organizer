from PySide6.QtWidgets import QApplication

from .gui.mainwindow import MainWindow


class Application(QApplication):
    def __init__(self) -> None:
        super().__init__()
        self.window = MainWindow()
        self.window.show()
