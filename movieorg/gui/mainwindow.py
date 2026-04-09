import json
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QFileDialog
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
        self.initial_data = None
        self.current_data = None
        self.movies: list[dict] = list()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        help_menu = menu_bar.addMenu("Help")

        # new menu item
        new_action = QAction(QIcon('./assets/new.png'), '&New', self)
        new_action.triggered.connect(lambda: self.create_new_database())
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # open menu item
        open_action = QAction('&Open File...', self)
        open_action.triggered.connect(lambda: self.load_database())
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # save menu item
        save_action = QAction('&Save', self)
        save_action.triggered.connect(lambda: print("save"))
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)

        # save as menu item
        save_as_action = QAction('&Save As...', self)
        save_as_action.triggered.connect(
            lambda: self.save_database())
        save_as_action.setShortcut('Ctrl+Shift+S')
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # exit menu item
        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(
            lambda: self.exit_application())
        exit_action.setStatusTip("Close Application")
        file_menu.addAction(exit_action)

        # add menu item
        about_action = QAction('&Add Movie...', self)
        about_action.triggered.connect(
            lambda: self.add_movie())
        about_action.setShortcut("Ctrl+A")
        edit_menu.addAction(about_action)

        # about menu item
        add_action = QAction(text='About', parent=self)
        add_action.triggered.connect(lambda: print("About..."))
        help_menu.addAction(add_action)

        self.status_bar = self.statusBar()

        self.initialize_table()

        # self.import_data()
        # self.update_table()

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
        self.table.cellClicked.connect(self.cell_clicked)
        self.table.cellDoubleClicked.connect(self.cell_double_clicked)
        self.table.cellChanged.connect(self.cell_changed)
        self.table.setColumnCount(len(MOVIE_ATTRIBUTES))
        self.table.setHorizontalHeaderLabels(MOVIE_ATTRIBUTES)
        # self.table.setColumnWidth(1, 45)
        # self.table.horizontalHeader().resizeSection(1, 15)
        self.table.horizontalHeader().setSectionsMovable(True)

    def update_table(self) -> None:
        # horizontalHeaderItem(column)
        self.table.setRowCount(0)
        for row_index in range(len(self.movies)):
            self.table.insertRow(row_index)
            for (col_index, attribute) in enumerate(MOVIE_ATTRIBUTES):
                item = QTableWidgetItem(self.movies[row_index][attribute])
                self.table.setItem(row_index, col_index, item)

    def save_database(self) -> None:
        movies = list()
        for row_index in range(self.table.rowCount()):
            single_movie = dict()
            for col_index in range(self.table.columnCount()):
                item = self.table.item(row_index, col_index)
                single_movie[MOVIE_ATTRIBUTES[col_index]] = \
                    item.text()  # type: ignore
            movies.append(single_movie)
        self.save_dict_to_json(movies)

    def save_dict_to_json(self, data: list[dict]) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save Report",
            dir="",
            filter="JSON Files (*.json)"
        )
        if filename:
            with open(filename, "wt") as file:
                json.dump(data, file, indent=4)
            print(f"Successfully saved {len(data)} movies.")

    def load_json_file_to_dict(self, file_name: str) -> dict:
        with open(file_name, "rt") as file_content:
            data = json.load(file_content)
        return data

    def load_database(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open Data File",
            dir="",
            filter="JSON Files (*.json);;MCO Files (*.mco)"
        )
        if filename:
            data = self.load_json_file_to_dict(filename)
            self.table.setRowCount(0)
            for movie in data:
                self.add_new_bottom_row(movie)

    def add_movie(self) -> None:
        print("About to add a new movie.")
        self.add_window = AddWindow(self)
        self.add_window.show()

    def exit_application(self) -> None:
        self.close()
        
    def create_new_database(self):
        self.table.setRowCount(0)
    
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
