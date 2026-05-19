import sys

from movieorg.app import Application

if __name__ == "__main__":
    app = Application()
    sys.exit(app.exec())
