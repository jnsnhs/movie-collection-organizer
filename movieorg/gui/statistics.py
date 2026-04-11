from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout
)
from numpy import array
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure


class MplCanvas(Canvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class StatisticsWindow(QWidget):
    def __init__(self, current_database):
        super().__init__()
        self.data = current_database
        self.setWindowTitle("Movie Collection Organizer - Statistics")
        self.tabs = QTabWidget(self)
        self.initialize_runtimes_plot()
        # self.initialize_directors_plot()
        self.initialize_genres_plot(5)
        self.initialize_decades_plot()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def initialize_runtimes_plot(self):
        runtimes_plot = QWidget(self)
        runtimes_data = [
            int(movie["runtime"].strip(" min")) for movie in self.data]
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.hist(runtimes_data)
        sc.axes.set_title("Movies by Runtime")
        sc.axes.set_xlim(left=0)
        sc.axes.yaxis.get_major_locator().set_params(
            integer=True)  # type: ignore
        self.add_plot_to_widget(sc, runtimes_plot)
        self.tabs.addTab(runtimes_plot, "Runtimes")

    def initialize_genres_plot(self, threshold=1):
        genres_plot = QWidget(self)
        genres = []
        for movie in self.data:
            genres.extend(movie["genre"].split(","))
        genres = [genre.strip() for genre in genres]
        genre_labels = set(genres)
        genre_dict = dict().fromkeys(genre_labels)
        others = 0
        for key in genre_dict.keys():
            if genres.count(key) >= threshold:
                genre_dict[key] = genres.count(key)
            else:
                genre_dict[key] = 0
                others += genres.count(key)
        if others:
            genre_dict = {key: value for (key, value)
                          in genre_dict.items()
                          if value >= threshold}  # type: ignore
            genre_dict["Others"] = others
        genre_frequencies = array(list(genre_dict.values()))
        genre_labels = list(genre_dict.keys())
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.pie(genre_frequencies, labels=genre_labels)
        sc.axes.set_title("Movies by Genre")
        self.add_plot_to_widget(sc, genres_plot)
        self.tabs.addTab(genres_plot, "Genres")

    def initialize_directors_plot(self):
        # TODO: format and optimize the chart's layout
        directors_plot = QWidget(self)
        raw_data = []
        for movie in self.data:
            raw_data.extend(movie["director"].split(","))
        raw_data = [director.strip() for director in raw_data]
        directors = set(raw_data)
        aggregated_data = dict().fromkeys(directors)
        for director in aggregated_data.keys():
            aggregated_data[director] = raw_data.count(director)
        sorted_tuples = sorted(
            aggregated_data.items(), key=lambda t: t[1])  # type: ignore
        aggregated_data = {k: v for k, v in sorted_tuples}
        frequencies = array(list(aggregated_data.values()))
        labels = array(list(aggregated_data.keys()))
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.barh(array(labels), array(frequencies))
        self.add_plot_to_widget(sc, directors_plot)
        self.tabs.addTab(directors_plot, "Directors")

    def initialize_decades_plot(self):
        decades_plot = QWidget(self)
        release_years = [int(movie["year"]) for movie in self.data]
        decades = list({int(movie["year"]) // 10 * 10 for movie in self.data})
        decades.sort()
        decades_labels = [str(first_year) + "s" for first_year in decades]
        decades_frequencies = [0] + [0] * (len(decades)-1)
        for release_year in release_years:
            for decade in decades:
                if release_year // 10 == decade // 10:
                    decades_frequencies[decades.index(decade)] += 1
                    break
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        decades_labels_short = [label[2:] for label in decades_labels]
        sc.axes.bar(array(decades_labels_short), array(decades_frequencies))
        sc.axes.set_title("Movies by Decade")
        self.add_plot_to_widget(sc, decades_plot)
        self.tabs.addTab(decades_plot, "Decades")

    def add_plot_to_widget(self, plot, widget):
        layout = QVBoxLayout()
        layout.addWidget(plot)
        widget.setLayout(layout)
