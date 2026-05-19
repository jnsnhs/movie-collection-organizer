from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QDialog,
    QMessageBox
)
import requests

from ..defaults import BASE_URL


class GetApiDataWindow(QDialog):

    def __init__(self, parent, apikey: str) -> None:
        super().__init__()
        self.parent_window = parent
        self.API_KEY = apikey
        self.current_search_term = None
        self.latest_search_list_of_results = list()
        self.latest_search_count_of_results = 0
        self.configure_window()
        self.create_widgets()
        self.setLayout(self.create_layout())
        self.register_events()
        self.show()

    def configure_window(self) -> None:
        self.setWindowTitle("Get data from API")

    def create_widgets(self) -> None:
        self.label_title = QLabel("Title")
        self.entry_title = QLineEdit()
        self.button_apirequest = QPushButton("Search API")
        self.label_api_results = QLabel("API Results")
        self.list_apidata = QListWidget()
        self.button_load_more = QPushButton("Load more results")
        self.label_selected_movie = QLabel()
        self.button_apply = QPushButton("Apply")
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.clicked.connect(lambda: self.close())

    def create_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self.label_title)
        layout.addWidget(self.entry_title)
        layout.addWidget(self.button_apirequest)
        layout.addWidget(self.label_api_results)
        layout.addWidget(self.list_apidata)
        layout.addWidget(self.button_load_more)
        layout.addWidget(self.label_selected_movie)
        layout.addWidget(self.button_apply)
        layout.addWidget(self.button_cancel)
        return layout

    def register_events(self) -> None:
        self.button_apirequest.clicked.connect(
            lambda: self.on_click_button_api_request())
        self.list_apidata.itemSelectionChanged.connect(
            lambda: self.on_selection_change())
        self.button_load_more.clicked.connect(
            lambda: self.on_click_button_load_more())
        self.button_apply.clicked.connect(
            lambda: self.on_click_button_apply())

    def on_click_button_api_request(self) -> None:
        movie_title = self.entry_title.text().strip(" ")
        if movie_title:
            self.current_search_term = movie_title
            try:
                api_data = self.get_api_title_list(movie_title)
            except Exception as exception:
                print(exception)
            else:
                print(api_data)
                try:
                    self.latest_search_list_of_results = api_data["Search"]
                except KeyError:
                    error_dialog = self.create_error_message(api_data["Error"])
                    error_dialog.exec()
                else:
                    self.latest_search_count_of_results = int(
                        api_data["totalResults"])
                    self.display_api_response()

    def create_error_message(self, text_to_display: str) -> QMessageBox:
        message = QMessageBox()
        message.setWindowTitle("Error")
        message.setText(text_to_display)
        message.setStandardButtons(QMessageBox.Ok)  # type: ignore
        message.setIcon(QMessageBox.Critical)  # type: ignore
        return message

    def on_click_button_apply(self) -> None:
        try:
            api_data = self.get_movie_details(self.get_selected_movie_imdbId())
        except Exception as exception:
            print(exception)
        else:
            self.parent_window.fill_entry_fields_with_movie_data(api_data)
            self.close_window()

    def on_click_button_load_more(self) -> None:
        try:
            api_data = self.get_more_results()
        except Exception as exception:
            print(exception)
        else:
            self.latest_search_list_of_results.extend(api_data["Search"])
            self.update_display_of_results()

    def update_display_of_results(self) -> None:
        self.list_apidata.clear()
        self.label_api_results.setText(
            f"API results "
            f"({self.latest_search_count_of_results}, showing 1-"
            f"{len(self.latest_search_list_of_results)})")
        for result in self.latest_search_list_of_results:
            self.list_apidata.addItem(
                QListWidgetItem(f"{result["Title"]} ({result["Year"]})"))

    def get_more_results(self) -> dict:
        page = len(self.latest_search_list_of_results) / 10 + 1
        request = f"{BASE_URL}{self.API_KEY}&s='{self.current_search_term}'" \
                  f"&type=movie&page={page}"
        response = requests.get(request)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code}")

    def get_api_title_list(self, title, page=1) -> dict:
        request = f"{BASE_URL}{self.API_KEY}&" \
                  f"s='{title}'&type=movie&page={page}"
        response = requests.get(request)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code}")

    def display_api_response(self) -> None:
        if not self.latest_search_list_of_results:
            return
        self.list_apidata.clear()
        self.label_api_results.setText(
            f"API results "
            f"({self.latest_search_count_of_results}, "
            f"showing 1-{len(self.latest_search_list_of_results)})")
        for result in self.latest_search_list_of_results:
            self.list_apidata.addItem(
                QListWidgetItem(f"{result["Title"]} ({result["Year"]})"))

    def on_selection_change(self) -> None:
        selection = self.list_apidata.selectedItems()[0].text()
        self.label_selected_movie.setText(f"Selected movie: {selection}")

    def get_selected_movie_imdbId(self) -> str:
        selected_row = self.list_apidata.row(
            self.list_apidata.selectedItems()[0])
        imdbId = self.latest_search_list_of_results[selected_row]["imdbID"]
        return imdbId

    def get_movie_details(self, imdbId: str) -> dict:
        request = f"{BASE_URL}{self.API_KEY}&i={imdbId}"
        response = requests.get(request)
        if response.status_code == 200:
            api_data = response.json()
            return api_data
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code}")

    def close_window(self) -> None:
        self.close()
