from configparser import ConfigParser
from copy import deepcopy
import json
from os import path
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
    QAbstractItemView
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt

from ..defaults import CONFIG_FILE_NAME, MOVIE_ATTRIBUTES
from ..gui.addmovie import AddWindow
from ..gui.editmovie import EditWindow
from ..gui.settings import SettingsWindow
from ..gui.statistics import StatisticsWindow


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.app_title = "Movie Collection Organizer"
        self.setWindowTitle(f"Untitled - {self.app_title}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(480)

        self.api_key, self.db_path = self.load_config_data(CONFIG_FILE_NAME)
        self.name_of_file = ""
        self.unsaved_changes = False

        self.status_bar = self.statusBar()
        self.database_summary = QLabel()
        self.status_bar.addPermanentWidget(self.database_summary)

        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(True)
        self.initialize_submenus(menu_bar)
        menu_bar.hovered.connect(lambda: self.on_hover_menubar())

        self.table = self.initialize_table()
        self.reset_database()
        self.update_table_to_match_db()
        self.update_availability_of_menu_items()

        self.search_field = self.initialize_search_field()

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.search_field)
        layout.addWidget(self.table)
        container.setLayout(layout)
        self.setCentralWidget(container)

        if self.db_path:
            try:
                self.import_db_from_json_file(self.db_path)
            except Exception as exception:
                print("Unable to import default database.")
                print(exception)

    def on_hover_menubar(self):
        self.update_availability_of_menu_items()

    def initialize_search_field(self) -> QLineEdit:
        search_field = QLineEdit()
        search_field.setPlaceholderText("Search...")
        search_field.textChanged.connect(lambda x: self.filter_table(x))
        return search_field

    def initialize_submenus(self, menu_bar) -> None:
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        # new menu item
        new_action = QAction(QIcon('./assets/new.png'), '&New File', self)
        new_action.triggered.connect(lambda: self.on_click_new())
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # open menu item
        open_action = QAction('&Open File...', self)
        open_action.triggered.connect(lambda: self.on_click_open())
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # save menu item
        save_action = QAction('&Save', self)
        save_action.triggered.connect(lambda: self.on_click_save())
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)

        # save as menu item
        save_as_action = QAction('&Save As...', self)
        save_as_action.triggered.connect(lambda: self.on_click_save_as())
        save_as_action.setShortcut('Ctrl+Shift+S')
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # settings menu item
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(lambda: self.on_click_settings())
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(lambda: self.on_click_exit())
        file_menu.addAction(exit_action)

        # add menu item
        add_action = QAction('&Insert Movie...', self)
        add_action.triggered.connect(lambda: self.on_click_add_movie())
        add_action.setShortcut("Ctrl+I")
        edit_menu.addAction(add_action)

        self.edit_action = QAction('&Edit Movie...', self)
        self.edit_action.triggered.connect(lambda: self.on_click_edit_movie())
        edit_menu.addAction(self.edit_action)

        # remove item
        self.remove_action = QAction("Remove Movie(s)", self)
        self.remove_action.triggered.connect(
            lambda: self.on_click_remove_movie())
        edit_menu.addAction(self.remove_action)

        # statistics item
        self.stats_action = QAction('&Statistics...', self)
        self.stats_action.triggered.connect(lambda: self.on_click_statistics())
        view_menu.addAction(self.stats_action)

        # about menu item
        about_action = QAction(text='About', parent=self)
        about_action.triggered.connect(lambda: self.on_click_about())
        help_menu.addAction(about_action)

    def initialize_table(self) -> QTableWidget:
        table = QTableWidget()
        table.horizontalHeader().setStretchLastSection(False)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setShowGrid(True)
        table.setSortingEnabled(False)
        table.setColumnCount(len(MOVIE_ATTRIBUTES))
        table.setHorizontalHeaderLabels(
            [label.title() for label in MOVIE_ATTRIBUTES]
        )
        # self.table.setColumnWidth(1, 45)
        # self.table.horizontalHeader().resizeSection(1, 15)
        table.horizontalHeader().setSectionsMovable(True)
        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        table.cellDoubleClicked.connect(lambda: self.on_doubleclick_cell())
        return table

    def on_doubleclick_cell(self):
        self.open_edit_movie_dialog()

    def on_click_settings(self) -> None:
        settings_window = SettingsWindow(self)
        settings_window.exec()
        self.api_key, self.db_path = self.load_config_data(CONFIG_FILE_NAME)

    def update_availability_of_menu_items(self) -> None:
        if self.current_database:
            self.stats_action.setEnabled(True)
        else:
            self.stats_action.setEnabled(False)
        if self.table.selectionModel().selectedRows():
            self.remove_action.setEnabled(True)
        else:
            self.remove_action.setEnabled(False)
        if len(self.table.selectionModel().selectedRows()) == 1:
            self.edit_action.setEnabled(True)
        else:
            self.edit_action.setEnabled(False)

    def on_click_save(self) -> None:
        if self.path_of_current_db:
            with open(self.path_of_current_db, "wt") as file:
                json.dump(self.current_database, file, indent=4)
            self.last_save_of_current_db = deepcopy(self.current_database)
            self.status_bar.showMessage(
                "Database has been saved.", timeout=2000)
            self.name_of_file = path.split(self.path_of_current_db)[1]
            self.set_unsaved_changes(False)
            self.setWindowTitle(f"{self.name_of_file} - {self.app_title}")
        else:
            self.on_click_save_as()

    def on_click_save_as(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save Movie Database",
            dir="",
            filter="JSON Files (*.json)"
        )
        if filename:
            self.path_of_current_db = filename
            self.on_click_save()

    def are_changes_unsaved(self) -> bool:
        if self.current_database == self.last_save_of_current_db:
            return False
        else:
            return True

    def on_click_open(self) -> None:
        if self.are_changes_unsaved():
            msg = QMessageBox()
            msg.setWindowTitle("Unsaved Changes")
            msg.setText("Do you want to save the current database?")
            msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No)  # type: ignore
            msg.setIcon(QMessageBox.Question)  # type: ignore
            user_input = msg.exec()
            if user_input == QMessageBox.Yes:  # type: ignore
                if self.path_of_current_db:
                    self.on_click_save()
                    self.load_external_database()
                else:
                    self.on_click_save_as()
            elif user_input == QMessageBox.No:  # type: ignore
                self.load_external_database()
        else:
            self.load_external_database()

    def is_json_file_valid(self) -> bool:
        return True  # TODO: Check if JSON file has a valid format.

    def load_external_database(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open Movie Database",
            dir="",
            filter="JSON Files (*.json)"
        )
        if filename:
            self.import_db_from_json_file(filename)

    def import_db_from_json_file(self, filename: str) -> None:
        data = []
        with open(filename, "rt") as file_content:
            data = json.load(file_content)
        if self.is_json_file_valid():
            self.path_of_current_db = filename
            self.current_database = data
            self.last_save_of_current_db = deepcopy(self.current_database)
            self.name_of_file = path.split(self.path_of_current_db)[1]
            self.setWindowTitle(
                f"{self.name_of_file} - {self.app_title}")
            self.set_unsaved_changes(False)
            self.update_table_to_match_db()
        else:
            print(f"{filename} is not a valid json file. "
                  "Unable to load database.")

    def update_table_to_match_db(self):
        self.table.setRowCount(0)
        for movie_dict in self.current_database:
            self.add_new_bottom_row(movie_dict)
        self.update_status_bar_msg()

    def update_status_bar_msg(self) -> None:
        if (movies_count := len(self.current_database)) == 0:
            msg = "This database is still empty."
        elif movies_count == 1:
            msg = "There is only one movie in this database."
        else:
            msg = f"There are {movies_count} movies in this database"
            msg = f"{msg}{self.get_runtime_string()}."
        self.database_summary.setText(msg)

    def get_runtime_string(self) -> str:
        total_runtime = 0
        are_values_missing = False
        for movie in self.current_database:
            if movie["runtime"]:
                total_runtime += int(movie["runtime"])
            else:
                are_values_missing = True
        runtime_string = ""
        if total_runtime:
            if total_runtime >= 2 * 525_600:
                runtime_string = f"{round(total_runtime / 525_600, 1)} years"
            if total_runtime >= 2 * 43_920:
                runtime_string = f"{round(total_runtime / 43_920, 1)} months"
            elif total_runtime >= 2 * 10_080:
                runtime_string = f"{round(total_runtime / 10_080, 1)} weeks"
            elif total_runtime >= 2 * 1440:
                runtime_string = f"{round(total_runtime / 1440, 1)} days"
            else:
                runtime_string = f"{round(total_runtime / 60, 1)} hours"
            if are_values_missing:
                runtime_string = "> " + runtime_string
            runtime_string = f" with a total runtime of {runtime_string}"
        return runtime_string

    def on_click_add_movie(self) -> None:
        self.add_window = AddWindow(self)
        self.add_window.show()

    def on_click_edit_movie(self) -> None:
        self.open_edit_movie_dialog()

    def open_edit_movie_dialog(self) -> None:
        selected_row_index = self.table.selectionModel().selectedRows()
        EditWindow(self, self.current_database, selected_row_index).exec()
        self.update_status_bar_msg()
        self.update_table_to_match_db()

    def on_click_remove_movie(self) -> None:
        indexes = self.table.selectionModel().selectedRows()
        print(f"{len(indexes)} row(s) selected")
        indexes.reverse()
        for index in indexes:
            del self.current_database[index.row()]
        self.set_unsaved_changes(True)
        self.update_table_to_match_db()
        self.update_availability_of_menu_items()

    def on_click_statistics(self) -> None:
        StatisticsWindow(self.current_database).exec()

    def on_click_about(self) -> None:
        msg = QMessageBox()
        msg.setWindowTitle("Movie Collection Organizer")
        msg.setText("A simple way to organize your movie collection.\n"
                    "Made by Jens Neuhaus, 2026.")
        msg.setStandardButtons(QMessageBox.Ok)  # type: ignore
        msg.setIcon(QMessageBox.Information)  # type: ignore
        msg.exec()

    def on_click_new(self) -> None:
        if self.are_changes_unsaved():
            msg = QMessageBox()
            msg.setWindowTitle("Unsaved Changes")
            msg.setText("Do you want to save the current database?")
            msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No)  # type: ignore
            msg.setIcon(QMessageBox.Question)  # type: ignore
            user_input = msg.exec()
            if user_input == QMessageBox.Yes:  # type: ignore
                if self.path_of_current_db:
                    self.on_click_save()
                    self.reset_database()
                else:
                    self.on_click_save_as()
            elif user_input == QMessageBox.No:  # type: ignore
                self.reset_database()
        else:
            self.reset_database()

    def reset_database(self) -> None:
        self.table.setRowCount(0)
        self.current_database: list = []
        self.last_save_of_current_db: list = []
        self.path_of_current_db: str = ""
        self.update_availability_of_menu_items()
        self.update_status_bar_msg()
        self.setWindowTitle(
            f"Untitled - {self.app_title}")

    def add_new_bottom_row(self, new_movie_data: dict) -> None:
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        for col_index, item in enumerate(new_movie_data.items()):
            self.table.setItem(row_index, col_index, QTableWidgetItem(item[1]))
            if item[0] in ("rating", "year", "runtime", "language"):
                self.table.item(
                    row_index, col_index).setTextAlignment(  # type: ignore
                        Qt.AlignmentFlag.AlignCenter)

    def closeEvent(self, event) -> None:
        if self.are_changes_unsaved():
            confirmation = QMessageBox.question(
                self,
                "Save Changes?",
                "File has been modified, save changes?",
                QMessageBox.Yes |  # type: ignore
                QMessageBox.No |  # type: ignore
                QMessageBox.Cancel  # type: ignore
            )
            if confirmation == QMessageBox.Yes:  # type: ignore
                event.ignore()
                self.on_click_save()
            elif confirmation == QMessageBox.No:  # type: ignore
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def filter_table(self, raw_input: str) -> None:
        terms = [string for string in raw_input.split(" ") if string]
        positive_terms = [string for string in terms if string[0] != "-"]
        negative_terms = [string[1:] for string in terms if string[0] == "-"]
        for row in range(self.table.rowCount()):
            all_positive_terms_found = True
            for term in positive_terms:
                term_found = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and term.casefold() in item.text().casefold():
                        term_found = True
                        break
                if not term_found:
                    all_positive_terms_found = False
                    break
            no_negative_terms_found = True
            if all_positive_terms_found:
                for term in negative_terms:
                    term_found = False
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item and term.casefold() in item.text().casefold():
                            term_found = True
                            break
                    if term_found:
                        no_negative_terms_found = False
                        break
            conditions_satisfied = \
                all_positive_terms_found and no_negative_terms_found
            self.table.setRowHidden(row, not conditions_satisfied)

    def load_config_data(self, file_name: str) -> tuple[str, str]:
        config = ConfigParser()
        try:
            config.read(file_name)
        except Exception:
            api_key, db_path = ("", "")
            print("No config file found.")
        else:
            api_key = config.get("API", "key")
            db_path = config.get("Database", "default_db")
        finally:
            return (api_key, db_path)

    def set_unsaved_changes(self, state: bool) -> None:
        self.unsaved_changes = state
        if self.unsaved_changes:
            self.setWindowTitle(
                f"{self.name_of_file} [unsaved] - {self.app_title}")
        else:
            self.setWindowTitle(
                f"{self.name_of_file} - {self.app_title}")

    def on_click_exit(self) -> None:
        print("Exit Application")
        self.close()
