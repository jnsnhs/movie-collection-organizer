from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QDialog
)
import requests

from ..defaults import BASE_URL


class GetApiDataWindow(QDialog):

    def __init__(self, parent, apikey: str) -> None:
        super().__init__()
        self.parent_window = parent
        self.setWindowTitle("Get data from API")
        self.API_KEY = apikey

        self.last_search_term = None
        self.last_search_list_of_results = list()
        self.last_search_count_of_results = 0

        self.label_title = QLabel("Title")
        self.entry_title = QLineEdit()
        self.button_apirequest = QPushButton("Search API")
        self.button_apirequest.clicked.connect(
            lambda: self.on_click_button_api_request())
        self.label_api_results = QLabel("API Results")
        self.list_apidata = QListWidget()
        self.list_apidata.itemSelectionChanged.connect(
            lambda: self.on_selection_change())
        self.button_load_more = QPushButton("Load more results")
        self.button_load_more.clicked.connect(
            lambda: self.on_click_button_load_more())
        self.label_selected_movie = QLabel()
        self.button_apply = QPushButton("Apply")
        self.button_apply.clicked.connect(
            lambda: self.on_click_button_apply())
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.clicked.connect(lambda: self.close())

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

        self.setLayout(layout)
        self.show()

    def add_item_to_list(self, content):
        self.list_apidata.addItem(QListWidgetItem(content))

    def on_click_button_api_request(self):
        title = self.entry_title.text().strip(" ")
        if title:
            self.last_search_term = title
            print(f"api request for {title}...")
            self.get_api_data(title)
            self.display_api_response()
        else:
            print("no valid input")

    def on_click_button_apply(self):
        self.get_movie_details(self.get_selected_movie_imdbId())

    def on_click_button_load_more(self):
        self.append_more_results()
        self.list_apidata.clear()
        self.label_api_results.setText(
            f"API results "
            f"({self.last_search_count_of_results}, showing 1-"
            f"{len(self.last_search_list_of_results)})")
        for result in self.last_search_list_of_results:
            self.add_item_to_list(f"{result["Title"]} ({result["Year"]})")

    def append_more_results(self):
        page = len(self.last_search_list_of_results) / 10 + 1
        request = f"{BASE_URL}{self.API_KEY}&s='{self.last_search_term}'" \
                  f"&type=movie&page={page}"
        response = requests.get(request)
        if response.status_code == 200:
            api_data = response.json()
            self.last_search_list_of_results.extend(api_data["Search"])
        else:
            print(f"Failed to retrieve data: {response.status_code}")

    def get_api_data(self, title="", page=1):
        if title:
            request = f"{BASE_URL}{self.API_KEY}&" \
                      f"s='{title}'&type=movie&page={page}"
            response = requests.get(request)
        else:
            print("No input to search for.")
        if response.status_code == 200:
            api_data = response.json()
            self.last_search_list_of_results = api_data["Search"]
            self.last_search_count_of_results = int(api_data["totalResults"])
        else:
            print(f"Failed to retrieve data: {response.status_code}")

    def display_api_response(self):
        if not self.last_search_list_of_results:
            return
        self.list_apidata.clear()
        self.label_api_results.setText(
            f"API results "
            f"({self.last_search_count_of_results}, "
            f"showing 1-{len(self.last_search_list_of_results)})")
        for result in self.last_search_list_of_results:
            self.add_item_to_list(f"{result["Title"]} ({result["Year"]})")

    def on_selection_change(self):
        selection = self.list_apidata.selectedItems()[0].text()
        self.label_selected_movie.setText(f"Selected movie: {selection}")

    def get_selected_movie_imdbId(self) -> str:
        selected_row = self.list_apidata.row(
            self.list_apidata.selectedItems()[0])
        imdbId = self.last_search_list_of_results[selected_row]["imdbID"]
        return imdbId

    def get_movie_details(self, imdbId: str):
        request = f"{BASE_URL}{self.API_KEY}&i={imdbId}"
        response = requests.get(request)
        if response.status_code == 200:
            api_data = response.json()
            print("Got some movie details:", api_data)
            self.parent_window.fill_entry_fields(api_data)
            self.close()
        else:
            print(f"Failed to retrieve data: {response.status_code}")
