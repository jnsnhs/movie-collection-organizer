from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout
)
from numpy import array
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

from ..defaults import APP_TITLE


class MplCanvas(Canvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class StatisticsWindow(QWidget):

    def __init__(self, database) -> None:
        super().__init__(
            windowTitle=f"{APP_TITLE} - Statistics"
        )
        tabs = QTabWidget(self)
        tabs.addTab(self.create_runtimes_plot(database), "Runtimes")
        tabs.addTab(self.create_genres_plot(database), "Genres")
        tabs.addTab(self.create_decades_plot(database), "Decades")
        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_runtimes_plot(self, data: dict) -> QWidget:
        widget = QWidget(self)
        runtimes_data = [
            int(movie["runtime"].strip(" min")) for movie in data]
        plot = MplCanvas(self, width=5, height=4, dpi=100)
        plot.axes.hist(runtimes_data)
        plot.axes.set_title("Movies by Runtime")
        plot.axes.set_xlim(left=0)
        plot.axes.yaxis.get_major_locator().set_params(
            integer=True)  # type: ignore
        layout = QVBoxLayout()
        layout.addWidget(plot)
        widget.setLayout(layout)
        return widget

    def create_genres_plot(self, data: dict) -> QWidget:
        widget = QWidget(self)
        genres = []
        for movie in data:
            genres.extend(movie["genre"].split(","))
        genres = [genre.strip() for genre in genres]
        genre_dict = dict().fromkeys(set(genres), 0)
        number_of_movies = len(data)
        for key in genre_dict.keys():
            genre_dict[key] = genres.count(key)
        threshold = number_of_movies // 10
        if threshold:
            highest_count = max([val for val in genre_dict.values()])
            others = 0
            print(threshold, highest_count)
            for key, val in genre_dict.items():
                if val <= threshold and highest_count >= 3 * threshold:
                    others += val
                    del genre_dict[key]
        if others:
            genre_dict["Others"] = others
        genre_frequencies = array(list(genre_dict.values()))
        genre_labels = list(genre_dict.keys())
        plot = MplCanvas(self, width=5, height=4, dpi=100)
        plot.axes.pie(genre_frequencies, labels=genre_labels)
        plot.axes.set_title("Movies by Genre")
        layout = QVBoxLayout()
        layout.addWidget(plot)
        widget.setLayout(layout)
        return widget

    def create_decades_plot(self, data: dict) -> QWidget:
        widget = QWidget(self)
        release_years = [int(movie["year"]) for movie in data]
        decades = list({int(movie["year"]) // 10 * 10 for movie in data})
        decades.sort()
        decades_labels = [str(first_year) + "s" for first_year in decades]
        decades_frequencies = [0] + [0] * (len(decades)-1)
        for release_year in release_years:
            for decade in decades:
                if release_year // 10 == decade // 10:
                    decades_frequencies[decades.index(decade)] += 1
                    break
        plot = MplCanvas(self, width=5, height=4, dpi=100)
        decades_labels_short = [label[2:] for label in decades_labels]
        plot.axes.bar(
            array(decades_labels_short), array(decades_frequencies))
        plot.axes.set_title("Movies by Decade")
        layout = QVBoxLayout()
        layout.addWidget(plot)
        widget.setLayout(layout)
        return widget
