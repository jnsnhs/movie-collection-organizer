from PySide6.QtWidgets import (
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFormLayout,
    QDialog,
    QDialogButtonBox,
    QMessageBox
)
from .apirequest import GetApiDataWindow


class AddWindow(QDialog):

    def __init__(self, main_window) -> None:
        super().__init__()
        self.setWindowTitle("Add Movie")
        self.main_window = main_window

        self.button_search = QPushButton("Search title in OMDB...")
        self.button_search.clicked.connect(
            lambda: self.on_click_button_search())

        self.entry_title = QLineEdit()
        self.entry_director = QLineEdit()
        self.entry_writer = QLineEdit()
        self.entry_actors = QLineEdit()
        self.entry_year = QLineEdit()
        self.entry_release = QLineEdit()
        self.entry_runtime = QLineEdit()
        self.entry_language = QLineEdit()
        self.entry_country = QLineEdit()
        self.entry_genre = QLineEdit()
        self.entry_plot = QTextEdit()

        QBtns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel  # type: ignore
        self.buttonBox = QDialogButtonBox(QBtns)
        self.buttonBox.accepted.connect(lambda: self.on_click_button_add())
        self.buttonBox.rejected.connect(lambda: self.on_click_button_cancel())

        layout = QFormLayout()
        layout.addRow(self.button_search)
        layout.addRow("Title", self.entry_title)
        layout.addRow("Director:", self.entry_director)
        layout.addRow("Writer:", self.entry_writer)
        layout.addRow("Actors:", self.entry_actors)
        layout.addRow("Year:", self.entry_year)
        layout.addRow("Release:", self.entry_release)
        layout.addRow("Runtime:", self.entry_runtime)
        layout.addRow("Language:", self.entry_language)
        layout.addRow("Country:", self.entry_country)
        layout.addRow("Genre:", self.entry_genre)
        layout.addRow("Plot:", self.entry_plot)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.entry_title.setFocus()

    def on_click_button_search(self) -> None:
        self.window_api_search = GetApiDataWindow(self)

    def on_click_button_add(self):
        if self.entry_title.text().strip() == "":
            no_title_msg = QMessageBox()
            no_title_msg.setWindowTitle("Unable to add new entry")
            no_title_msg.setText("Please enter a title to add a movie.")
            no_title_msg.setStandardButtons(QMessageBox.Ok)  # type: ignore
            no_title_msg.setIcon(QMessageBox.Critical)  # type: ignore
            no_title_msg.exec()
        elif self.is_title_in_database():
            msg = QMessageBox()
            msg.setWindowTitle("Title already in database")
            msg.setText(
                f"A movie with the title '{self.entry_title.text()}' "
                "is already part of your database.\nDo you really want to "
                "add another movie of the same title?")
            msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No)  # type: ignore
            msg.setIcon(QMessageBox.Question)  # type: ignore
            user_input = msg.exec()
            if user_input == QMessageBox.Yes:  # type: ignore
                self.add_movie_to_database()
                self.close()
        else:
            self.add_movie_to_database()
            self.close()

    def add_movie_to_database(self) -> None:
        new_movie = {
            "title": self.entry_title.text(),
            "director": self.entry_director.text(),
            "writer": self.entry_writer.text(),
            "actors": self.entry_actors.text(),
            "year": self.entry_year.text(),
            "release": self.entry_release.text(),
            "runtime": self.entry_runtime.text(),
            "language": self.entry_language.text(),
            "country": self.entry_country.text(),
            "genre": self.entry_genre.text()
        }
        self.main_window.current_database.append(new_movie)
        self.main_window.update_table_to_match_db()
        self.main_window.update_availability_of_menu_items()

    def is_title_in_database(self) -> bool:
        current_db = self.main_window.current_database
        for movie in current_db:
            if movie["title"] == self.entry_title.text().strip():
                return True
        return False

    def fill_entry_fields(self, data: dict) -> None:
        self.entry_title.setText(data["Title"])
        self.entry_year.setText(data["Year"])
        self.entry_release.setText(data["Released"])
        self.entry_runtime.setText(data["Runtime"])
        self.entry_genre.setText(data["Genre"])
        self.entry_director.setText(data["Director"])
        self.entry_writer.setText(data["Writer"])
        self.entry_actors.setText(data["Actors"])
        self.entry_plot.setText(data["Plot"])
        self.entry_language.setText(data["Language"])
        self.entry_country.setText(data["Country"])

    def on_click_button_cancel(self) -> None:
        self.close()
