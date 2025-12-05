# Vista.py
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog 
from PyQt5.uic import loadUi
import numpy as np

class LoginView(QMainWindow):
    """
    Clase que representa la interfaz de Login.
    Solo se encarga de cargar el diseño .ui y de mostrar/obtener datos.
    """
    def __init__(self):
        super().__init__()
        # Carga el diseño de la interfaz desde el archivo .ui
        loadUi('./ui_files/login_window.ui', self)
        
        # 1. Obtener referencias a los widgets clave (ASEGÚRATE DE USAR LOS NOMBRES CORRECTOS)
        # Reemplaza 'btn_login', 'txt_usuario', 'txt_password' con los nombres que diste en QtDesigner.
        self.btn_login = self.findChild(QtWidgets.QPushButton, 'btn_login') 
        self.txt_usuario = self.findChild(QtWidgets.QLineEdit, 'txt_usuario')
        self.txt_password = self.findChild(QtWidgets.QLineEdit, 'txt_password')
        
        # Configuración de seguridad visual
        self.txt_password.setEchoMode(QtWidgets.QLineEdit.Password)

    def obtener_credenciales(self):
        """Retorna las credenciales ingresadas por el usuario."""
        return self.txt_usuario.text(), self.txt_password.text()

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un cuadro de diálogo con información o error."""
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec_()