import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


BASE_URL = "http://www.omdbapi.com/?apikey="
CONFIG_FILE_NAME = "movieorg.conf"
APP_TITLE = "Movie Collection Organizer"

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
