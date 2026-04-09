import json
from copy import deepcopy
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QFileDialog,
    QMessageBox
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QLineEdit

from .addmovie import AddWindow
from ..defaults import MOVIE_ATTRIBUTES


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Movie Collection Organizer")
        # self.setWindowIcon(QIcon('./assets/editor.png'))
        # self.setGeometry()
        self.setMinimumWidth(640)
        self.setMinimumHeight(480)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
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

        # exit menu item
        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(lambda: self.on_click_exit())
        file_menu.addAction(exit_action)

        # add menu item
        about_action = QAction('&Add Movie...', self)
        about_action.triggered.connect(lambda: self.on_click_add_movie())
        about_action.setShortcut("Ctrl+A")
        edit_menu.addAction(about_action)

        # about menu item
        add_action = QAction(text='About', parent=self)
        add_action.triggered.connect(lambda: self.on_click_about())
        help_menu.addAction(add_action)

        self.initialize_table()
        self.reset_database()

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search...")
        self.search_field.textChanged.connect(self.filter_table)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.search_field)
        layout.addWidget(self.table)
        container.setLayout(layout)

        self.setCentralWidget(container)

    def initialize_table(self) -> None:
        self.table = QTableWidget()
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSortingEnabled(False)
        # self.table.cellClicked.connect(self.cell_clicked)
        # self.table.cellDoubleClicked.connect(self.cell_double_clicked)
        # self.table.cellChanged.connect(self.cell_changed)
        self.table.setColumnCount(len(MOVIE_ATTRIBUTES))
        self.table.setHorizontalHeaderLabels(MOVIE_ATTRIBUTES)
        # self.table.setColumnWidth(1, 45)
        # self.table.horizontalHeader().resizeSection(1, 15)
        self.table.horizontalHeader().setSectionsMovable(True)

    def on_click_save(self) -> None:
        if self.path_of_current_db:
            with open(self.path_of_current_db, "wt") as file:
                json.dump(self.current_database, file, indent=4)
            self.last_save_of_current_db = deepcopy(self.current_database)
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
            data = []
            with open(filename, "rt") as file_content:
                data = json.load(file_content)
            if self.is_json_file_valid():
                self.path_of_current_db = filename
                self.current_database = data
                self.last_save_of_current_db = deepcopy(self.current_database)
                self.update_table_to_match_db()
            else:
                print("Invalid JSON file. Unable to load database.")

    def update_table_to_match_db(self):
        self.table.setRowCount(0)
        for movie_dict in self.current_database:
            self.add_new_bottom_row(movie_dict)

    def on_click_add_movie(self) -> None:
        self.add_window = AddWindow(self)
        self.add_window.show()

    def on_click_exit(self) -> None:
        if self.are_changes_unsaved() is True:
            msg = QMessageBox()
            msg.setWindowTitle("Unsaved Changes")
            msg.setText("Do you really want to quit?")
            msg.setStandardButtons(QMessageBox.Ok)  # type: ignore
            msg.setIcon(QMessageBox.Critical)  # type: ignore
            msg.exec()
        else:
            self.close()

    def on_click_about(self) -> None:
        msg = QMessageBox()
        msg.setWindowTitle("Movie Collection Organizer")
        msg.setText("Some information about this little application...")
        msg.setStandardButtons(QMessageBox.Ok)  # type: ignore
        msg.setIcon(QMessageBox.Information)  # type: ignore
        # msg.accepted.connect(lambda: print("Click OK in About Dialog."))
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

    def add_new_bottom_row(self, new_movie_data: dict) -> None:
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        for col_index, item in enumerate(new_movie_data.items()):
            self.table.setItem(row_index, col_index, QTableWidgetItem(item[1]))

    def cell_clicked(self, row, column) -> None:
        print(f"Cell clicked: row {row}, column {column}")
        item = self.table.item(row, column)
        if item:
            print(f"Content: {item.text()}")

    def cell_double_clicked(self, row, column) -> None:
        print(f"Editing cell at row {row}, column {column}")

    def cell_changed(self, row, column) -> None:
        item = self.table.item(row, column)
        if item:
            print(f"Cell at row {row}, column {column} changed "
                  f"to: {item.text()}")

    def filter_table(self, text) -> None:
        for row in range(self.table.rowCount()):
            should_show = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    should_show = True
                    break
            self.table.setRowHidden(row, not should_show)
