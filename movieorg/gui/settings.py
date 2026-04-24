from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QMessageBox
)
from configparser import ConfigParser
import requests

from ..defaults import BASE_URL, CONFIG_FILE_NAME


class SettingsWindow(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.setWindowTitle("Settings")
        self.api_key, self.db_path = self.load_config_data(CONFIG_FILE_NAME)

        QBtns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel  # type: ignore
        self.buttonBox = QDialogButtonBox(QBtns)
        self.buttonBox.accepted.connect(lambda: self.on_click_button_ok())
        self.buttonBox.rejected.connect(lambda: self.on_click_button_cancel())

        self.entry_apikey = self.init_entry_apikey()
        label_apikey = QLabel("API Key")

        self.label_default_db = QLabel(self.db_path)
        button_choose_db = self.init_button_choose_file()
        button_choose_db.clicked.connect(lambda: self.set_defaut_path())

        layout = QVBoxLayout()
        layout.addWidget(self.label_default_db)
        layout.addWidget(button_choose_db)
        layout.addWidget(label_apikey)
        layout.addWidget(self.entry_apikey)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def init_entry_apikey(self) -> QLineEdit:
        entry_field = QLineEdit()
        entry_field.setText(self.api_key)
        return entry_field

    def init_button_choose_file(self) -> QPushButton:
        return QPushButton("Choose File...")

    def on_click_button_ok(self):
        api_key: str = self.entry_apikey.text() + "\n"
        json_path: str = self.label_default_db.text() + "\n"
        config = ConfigParser()
        config["API"] = {"key": api_key}
        config["Database"] = {"default_db": json_path}
        try:
            with open(CONFIG_FILE_NAME, "wt", encoding="utf8") as file:
                config.write(file)
        except Exception as exception:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"Config file could not be written.\n\n{exception}")
            msg.setStandardButtons(QMessageBox.Ok)  # type: ignore
            msg.setIcon(QMessageBox.Critical)  # type: ignore
            msg.exec()
        self.close()

    def on_click_button_cancel(self):
        self.close()

    def set_defaut_path(self):
        filename, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Choose default database file",
            dir="",
            filter="JSON Files (*.json)"
        )
        self.label_default_db.setText(filename)

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

    def is_apikey_valid(self, apikey: str) -> None:
        request = f"{BASE_URL}{apikey}"
        response = requests.get(request)
        if response.status_code == 200:
            print("valid api key")
        else:
            print("key is invalid")
