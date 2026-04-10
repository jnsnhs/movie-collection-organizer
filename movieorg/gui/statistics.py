from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout
)


class StatisticsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistics")

        QBtns = QDialogButtonBox.Ok  # type: ignore
        self.buttonBox = QDialogButtonBox(QBtns)
        self.buttonBox.accepted.connect(lambda: self.close())

        layout = QVBoxLayout()
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
