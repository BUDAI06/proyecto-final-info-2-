from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QPushButton
from PyQt5.uic import loadUi
import os

class LoginView(QWidget):
    def __init__(self):
        super().__init__()

        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.join(ruta_actual, "..", "ui", "login_window.ui")

        try:
            loadUi(ruta_ui, self)
        except FileNotFoundError:
            self.mostrar_mensaje("Error Crítico", f"No se encuentra el archivo: {ruta_ui}")

        self.btn_login = self.findChild(QPushButton, "btn_login")
        self.txt_usuario = self.findChild(QLineEdit, "txt_usuario")
        self.txt_password = self.findChild(QLineEdit, "txt_password")

        if self.txt_password:
            self.txt_password.setEchoMode(QLineEdit.Password)

    def obtener_credenciales(self):
        if self.txt_usuario and self.txt_password:
            return self.txt_usuario.text(), self.txt_password.text()
        return "", ""

    def mostrar_mensaje(self, titulo, mensaje):
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()
