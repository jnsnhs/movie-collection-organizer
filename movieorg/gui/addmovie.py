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
        self.main_window = parent
        self.configure_window()
        self.create_widgets()
        self.setLayout(self.create_layout())
        self.register_events()

    def configure_window(self) -> None:
        self.setMinimumWidth(320)
        self.setWindowTitle("Add Movie")

    def create_widgets(self) -> None:
        self.button_search = self.create_omdb_search_button()
        self.entry_title = QLineEdit()
        self.entry_title.setFocus()
        self.entry_director = QLineEdit()
        self.entry_writer = QLineEdit()
        self.entry_actors = QLineEdit()
        self.entry_year = QLineEdit(maxLength=4)
        self.entry_runtime = QLineEdit(maxLength=3)
        self.entry_language = QLineEdit()
        self.entry_genre = QLineEdit()
        self.entry_rating = QSpinBox(minimum=0, maximum=5)
        self.buttonBox = self.create_dialog_buttons()

    def create_layout(self) -> QFormLayout:
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
        return layout

    def register_events(self) -> None:
        self.buttonBox.accepted.connect(lambda: self.add_movie_to_database())
        self.buttonBox.rejected.connect(lambda: self.close_window())
        self.search_button.clicked.connect(
            lambda: GetApiDataWindow(self, self.main_window.api_key))

    def create_dialog_buttons(self) -> QDialogButtonBox:
        QBtns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel  # type: ignore
        self.buttonBox = QDialogButtonBox(QBtns)
        return self.buttonBox

    def create_omdb_search_button(self) -> QPushButton:
        self.search_button = QPushButton("Search for title in OMDB...")
        return self.search_button

    def is_apikey_valid(self, api_key: str) -> bool:
        request = f"{BASE_URL}{api_key}&i=tt0033467"
        response = requests.get(request)
        return True if response.status_code == 200 else False

    def create_messagebox_title_exists(self) -> QMessageBox:
        message = QMessageBox()
        message.setWindowTitle("Title already in database")
        message.setText(
            f"A movie with the title '{self.entry_title.text()}' "
            "is already part of your database.\n\nDo you really want to "
            "add another entry with the same movie title?")
        message.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No)  # type: ignore
        message.setIcon(QMessageBox.Question)  # type: ignore
        return message

    def create_messagebox_title_is_empty(self) -> QMessageBox:
        message = QMessageBox()
        message.setWindowTitle("Unable to add new entry")
        message.setText(
            "Please enter a movie title to add a new entry.")
        message.setStandardButtons(QMessageBox.Ok)  # type: ignore
        message.setIcon(QMessageBox.Critical)  # type: ignore
        return message

    def add_movie_to_database(self) -> None:
        confirmation = True
        if self.entry_title.text().strip() == "":
            messagebox = self.create_messagebox_title_is_empty()
            messagebox.exec()
            confirmation = False
        elif self.is_title_in_database():
            message = self.create_messagebox_title_exists()
            if message.exec() != QMessageBox.Yes:  # type: ignore
                confirmation = False
        if confirmation:
            new_movie = self.get_movie_data_from_entries()
            self.main_window.current_database.append(new_movie)
            self.main_window.set_unsaved_changes(True)
            self.main_window.update_table_to_match_db()
            self.main_window.update_availability_of_menu_items()
            self.close_window()

    def get_movie_data_from_entries(self) -> dict:
        return {
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

    def is_title_in_database(self) -> bool:
        current_db = self.main_window.current_database
        for movie in current_db:
            if movie["title"] == self.entry_title.text().strip():
                return True
        return False

    def fill_entry_fields_with_movie_data(self, data: dict) -> None:
        self.entry_title.setText(data["Title"])
        self.entry_year.setText(data["Year"])
        self.entry_runtime.setText(data["Runtime"].strip(" min"))
        self.entry_genre.setText(data["Genre"])
        self.entry_director.setText(data["Director"])
        self.entry_writer.setText(data["Writer"])
        self.entry_actors.setText(data["Actors"])
        self.entry_language.setText(data["Language"].split(", ")[0])

    def close_window(self) -> None:
        self.close()
