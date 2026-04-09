from PySide6.QtWidgets import QApplication

from .gui.mainwindow import MainWindow

MOVIE_ATTRIBUTES = (
    "title",
    "director",
    "writer",
    "actors",
    "year",
    "release",
    "runtime",
    "language",
    "country",
    "genre"
)


class Application(QApplication):
    def __init__(self) -> None:
        super().__init__()
        self.window = MainWindow()
        self.window.show()
