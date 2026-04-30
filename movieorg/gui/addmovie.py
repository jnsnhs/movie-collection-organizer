from PySide6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QSpinBox,
    QFormLayout,
    QDialog,
    QDialogButtonBox,
    QMessageBox
)
import requests
from .apirequest import GetApiDataWindow
from ..defaults import BASE_URL


class AddWindow(QDialog):

    def __init__(self, parent) -> None:
        super().__init__()
        self.setWindowTitle("Add Movie")
        self.setMinimumWidth(320)
        self.main_window = parent

        self.button_search = QPushButton("Search title in OMDB...")
        self.button_search.clicked.connect(
            lambda: self.on_click_button_search())

        self.entry_title = QLineEdit()
        self.entry_director = QLineEdit()
        self.entry_writer = QLineEdit()
        self.entry_actors = QLineEdit()
        self.entry_year = QLineEdit(maxLength=4)
        self.entry_runtime = QLineEdit(maxLength=3)
        self.entry_language = QLineEdit()
        self.entry_genre = QLineEdit()
        self.entry_rating = QSpinBox(minimum=0, maximum=5)

        QBtns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel  # type: ignore
        self.buttonBox = QDialogButtonBox(QBtns)
        self.buttonBox.accepted.connect(lambda: self.on_click_button_add())
        self.buttonBox.rejected.connect(lambda: self.on_click_button_cancel())

        layout = QFormLayout()
        if self.is_apikey_valid(self.main_window.api_key):
            layout.addRow(self.button_search)
        layout.addRow("Title", self.entry_title)
        layout.addRow("Director:", self.entry_director)
        layout.addRow("Writer:", self.entry_writer)
        layout.addRow("Actors:", self.entry_actors)
        layout.addRow("Year:", self.entry_year)
        layout.addRow("Runtime:", self.entry_runtime)
        layout.addRow("Language:", self.entry_language)
        layout.addRow("Genre:", self.entry_genre)
        layout.addRow("Rating:", self.entry_rating)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.entry_title.setFocus()

    def on_click_button_search(self) -> None:
        api_key = self.main_window.api_key
        self.window_api_search = GetApiDataWindow(self, api_key)

    def is_apikey_valid(self, api_key: str) -> bool:
        request = f"{BASE_URL}{api_key}&i=tt0033467"
        response = requests.get(request)
        return True if response.status_code == 200 else False

    def on_click_button_add(self):
        if self.entry_title.text().strip() == "":
            no_title_msg = QMessageBox()
            no_title_msg.setWindowTitle("Unable to add new entry")
            no_title_msg.setText("Please enter a movie title to "
                                 "add a new entry.")
            no_title_msg.setStandardButtons(QMessageBox.Ok)  # type: ignore
            no_title_msg.setIcon(QMessageBox.Critical)  # type: ignore
            no_title_msg.exec()
        elif self.is_title_in_database():
            msg = QMessageBox()
            msg.setWindowTitle("Title already in database")
            msg.setText(
                f"A movie with the title '{self.entry_title.text()}' "
                "is already part of your database.\n\nDo you really want to "
                "add another entry with the same movie title?")
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
            "runtime": self.entry_runtime.text(),
            "language": self.entry_language.text(),
            "genre": self.entry_genre.text(),
            "rating": self.entry_rating.text()
        }
        self.main_window.current_database.append(new_movie)
        self.main_window.set_unsaved_changes(True)
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
        self.entry_runtime.setText(data["Runtime"].strip(" min"))
        self.entry_genre.setText(data["Genre"])
        self.entry_director.setText(data["Director"])
        self.entry_writer.setText(data["Writer"])
        self.entry_actors.setText(data["Actors"])
        self.entry_language.setText(data["Language"].split(", ")[0])

    def on_click_button_cancel(self) -> None:
        self.close()
