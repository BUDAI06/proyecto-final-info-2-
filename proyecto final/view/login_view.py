from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout

class LoginView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.lbl_title = QLabel("Iniciar sesión")
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Usuario")
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Ingresar")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.txt_usuario)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def obtener_credenciales(self):
        return self.txt_usuario.text(), self.txt_password.text()
