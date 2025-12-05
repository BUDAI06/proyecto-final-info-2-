
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class SenalesView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Módulo de señales EEG/ECG"))
        self.setLayout(layout)
