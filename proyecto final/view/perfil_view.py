from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class PerfilView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.lbl_info = QLabel("Perfil del usuario")

        layout.addWidget(self.lbl_info)
        self.setLayout(layout)

    def mostrar_info(self, usuario):
        self.lbl_info.setText(f"Usuario: {usuario}\nEstado: Sesión activa")
