from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class TabularView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Módulo de datos tabulares CSV"))
        self.setLayout(layout)
