import json
from configparser import ConfigParser
from copy import deepcopy
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QVBoxLayout,
    QFileDialog,
    QMessageBox
)
from PySide6.QtGui import QIcon, QAction

from ..defaults import CONFIG_FILE_NAME
from ..gui.addmovie import AddWindow
from ..gui.settings import SettingsWindow
from ..gui.statistics import StatisticsWindow


MOVIE_ATTRIBUTES = (
    "title",
    "director",
    "writer",
    "actors",
    "year",
    "runtime",
    "language",
    "genre",
    "rating"
    )


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.app_title = "Movie Collection Organizer"
        self.setWindowTitle(f"Untitled - {self.app_title}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(480)

        self.api_key, self.db_path = self.load_config_data(CONFIG_FILE_NAME)

        self.status_bar = self.statusBar()
        self.database_summary = QLabel()
        self.status_bar.addPermanentWidget(self.database_summary)

        menu_bar = self.menuBar()
        self.initialize_submenus(menu_bar)
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
            except Exception:
                print("Unable to import default database.")

    def initialize_search_field(self) -> QLineEdit:
        search_field = QLineEdit()
        search_field.setPlaceholderText("Search...")
        search_field.textChanged.connect(lambda x: self.filter_table_simple(x))
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
        about_action = QAction('&Insert Movie...', self)
        about_action.triggered.connect(lambda: self.on_click_add_movie())
        about_action.setShortcut("Ctrl+I")
        edit_menu.addAction(about_action)

        # remove item
        remove_action = QAction("Delete Movie...", self)
        remove_action.triggered.connect(lambda: self.on_click_remove_movie())
        remove_action.setShortcut("Ctrl+D")
        edit_menu.addAction(remove_action)

        # statistics item
        self.stats_action = QAction('&Statistics...', self)
        self.stats_action.triggered.connect(lambda: self.on_click_statistics())
        view_menu.addAction(self.stats_action)

        # about menu item
        add_action = QAction(text='About', parent=self)
        add_action.triggered.connect(lambda: self.on_click_about())
        help_menu.addAction(add_action)

    def initialize_table(self) -> QTableWidget:
        table = QTableWidget()
        table.horizontalHeader().setStretchLastSection(False)
        table.verticalHeader().setVisible(False)
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
        print("double clicked!")

    def on_click_settings(self) -> None:
        settings_window = SettingsWindow(self)
        settings_window.exec()
        self.api_key, self.db_path = self.load_config_data(CONFIG_FILE_NAME)

    def update_availability_of_menu_items(self):
        if len(self.current_database) == 0:
            self.stats_action.setEnabled(False)
        else:
            self.stats_action.setEnabled(True)

    def on_click_save(self) -> None:
        if self.path_of_current_db:
            with open(self.path_of_current_db, "wt") as file:
                json.dump(self.current_database, file, indent=4)
            self.last_save_of_current_db = deepcopy(self.current_database)
            self.status_bar.showMessage(
                "Database has been saved.", timeout=2000)
            self.setWindowTitle(
                f"{self.path_of_current_db} - {self.app_title}")
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
            self.setWindowTitle(
                f"{self.path_of_current_db} - {self.app_title}")
            self.update_table_to_match_db()
            self.update_availability_of_menu_items()
        else:
            print(f"{filename} is not a valid json file. "
                  "Unable to load database.")

    def update_table_to_match_db(self):
        self.table.setRowCount(0)
        for movie_dict in self.current_database:
            self.add_new_bottom_row(movie_dict)
        self.update_status_bar_msg()

    def update_status_bar_msg(self):
        if (movies_count := len(self.current_database)) == 0:
            msg = "Current database is empty."
        elif movies_count == 1:
            msg = f"{movies_count} movies in database."
        else:
            msg = f"{movies_count} movies in database."
        self.database_summary.setText(msg)

    def on_click_add_movie(self) -> None:
        self.add_window = AddWindow(self)
        self.add_window.show()

    def on_click_remove_movie(self) -> None:
        indexes = self.table.selectionModel().selectedRows()
        print(f"{len(indexes)} row(s) selected")
        indexes.reverse()
        for index in indexes:
            del self.current_database[index.row()]
        self.update_table_to_match_db()
        self.update_availability_of_menu_items()

    def on_click_statistics(self) -> None:
        self.stats_window = StatisticsWindow(self.current_database)
        self.stats_window.show()

    def on_click_about(self) -> None:
        msg = QMessageBox()
        msg.setWindowTitle("Movie Collection Organizer")
        msg.setText("Some information about this little application...")
        msg.setStandardButtons(QMessageBox.Ok)  # type: ignore
        msg.setIcon(QMessageBox.Information)  # type: ignore
        msg.exec()

    def on_click_new(self):
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

    def reset_database(self):
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

    def closeEvent(self, event):
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

    def filter_table_simple(self, raw_input: str) -> None:
        search_terms = [i for i in raw_input.split(" ") if i]
        for row in range(self.table.rowCount()):
            all_terms_found = True
            for term in search_terms:
                term_found = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and term.casefold() in item.text().casefold():
                        term_found = True
                        break
                if not term_found:
                    all_terms_found = False
                    break

            self.table.setRowHidden(row, not all_terms_found)

# year, runtime, rating

    def filter_table_advanced(self, raw_input: str) -> None:
        search_terms = [i for i in raw_input.split(" ") if i]
        for row in range(self.table.rowCount()):
            all_conditions_met = True
            for term in search_terms:
                filter_positive = False
                if set(term).intersection({"=", "<", ">"}):
                    row_meets_condition = self.meets_filter_condition(
                        row, term
                    )
                    filter_positive = row_meets_condition
                if not filter_positive:
                    all_conditions_met = False
                    break
            self.table.setRowHidden(row, not all_conditions_met)

    def meets_filter_condition(self, row: int, condition: str) -> bool:
        count_operators = sum([condition.count(i) for i in ("<", ">", "=")])
        if count_operators > 1:
            print("term invalid")
            return False
        for o in ("<", ">", "="):
            if len(res := [i for i in input.partition(o) if i]) == 3:
                left_side = res[0]
                operator = res[1]
                right_side = res[2]
        return False

        # for col in range(self.table.columnCount()):
        #     item = self.table.item(row, col)
        #     if item and term.casefold() in item.text().casefold():
        #         term_found = True
        #         break

    def load_config_data(self, file_name: str) -> tuple[str, str]:
        config = ConfigParser()
        try:
            config.read(file_name)
        except Exception:
            api_key, db_path = ("", "")
        else:
            api_key = config.get("API", "key")
            db_path = config.get("Database", "default_db")
        finally:
            return (api_key, db_path)

    def on_click_exit(self):
        print("Exit Application")
        self.close()
