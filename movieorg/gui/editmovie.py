from PySide6.QtWidgets import (
    QLineEdit,
    QSpinBox,
    QFormLayout,
    QDialog,
    QDialogButtonBox,
)


class EditWindow(QDialog):

    def __init__(self, parent, database, selected_rows) -> None:
        super().__init__()
        self.main_window = parent
        self.current_database = database
        self.selected_movie_index = selected_rows[0].row()
        self.create_widgets()
        self.setLayout(self.create_layout())
        self.register_events()
        self.fill_entry_fields_with_movie_data()

    def configure_window(self) -> None:
        self.setMinimumWidth(320)
        movie_title = self.current_database[self.selected_movie_index]["title"]
        self.setWindowTitle(f"Edit „{movie_title}“")

    def create_widgets(self) -> None:
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
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # type: ignore

    def create_layout(self) -> QFormLayout:
        layout = QFormLayout()
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
        self.buttonBox.accepted.connect(lambda: self.on_click_button_ok())
        self.buttonBox.rejected.connect(lambda: self.on_click_button_cancel())

    def fill_entry_fields_with_movie_data(self) -> None:
        movie = self.current_database[self.selected_movie_index]
        self.entry_title.setText(movie["title"])
        self.entry_director.setText(movie["director"])
        self.entry_writer.setText(movie["writer"])
        self.entry_actors.setText(movie["actors"])
        self.entry_year.setText(movie["year"])
        self.entry_runtime.setText(movie["runtime"])
        self.entry_language.setText(movie["language"])
        self.entry_genre.setText(movie["genre"])
        self.entry_rating.setValue(int(movie["rating"]))

    def update_database_values(self, movie_index: int) -> None:
        movie = self.current_database[movie_index]
        movie["title"] = self.entry_title.text()
        movie["director"] = self.entry_director.text()
        movie["writer"] = self.entry_writer.text()
        movie["actors"] = self.entry_actors.text()
        movie["year"] = self.entry_year.text()
        movie["runtime"] = self.entry_runtime.text()
        movie["language"] = self.entry_language.text()
        movie["genre"] = self.entry_genre.text()
        movie["rating"] = self.entry_rating.text()

    def on_click_button_ok(self) -> None:
        self.update_database_values(self.selected_movie_index)
        self.main_window.set_unsaved_changes(True)
        self.close_window()

    def on_click_button_cancel(self) -> None:
        self.close_window()

    def close_window(self) -> None:
        self.close()
