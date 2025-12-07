# view/login_view.py

from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QPushButton, QDialog
from PyQt5.uic import loadUi
import os

class LoginView(QDialog): 
    """
    Vista encargada de mostrar la interfaz de inicio de sesión.
    Carga el UI desde un archivo y mapea los widgets clave.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Determinar la ruta del archivo .ui
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.join(ruta_actual, "..", "ui", "login_window.ui")

        try:
            # Cargar el archivo .ui en la propia instancia (self)
            loadUi(ruta_ui, self) 
        except FileNotFoundError:
            # Si el UI no se encuentra, muestra un error crítico y retorna
            self.mostrar_mensaje("Error Crítico", f"No se encuentra el archivo: {ruta_ui}. Verifique la ruta.")
            return

        # --- Mapeo de Widgets ---
        # ⚠️ CRÍTICO: Los nombres deben coincidir EXACTAMENTE con el objectName de Qt Designer
        
        # Botón
        self.btn_login = self.findChild(QPushButton, "btn_login")
        
        # Campos de texto
        self.txt_usuario = self.findChild(QLineEdit, "txt_usuario")
        # El nombre debe ser "txt_contrasena" si es el que usaste en el UI (sin 'ñ')
        self.txt_contraseña = self.findChild(QLineEdit, "txt_contrasena") 
        
        # Opcional: Si tienes un botón de cancelar
        self.btn_cancelar = self.findChild(QPushButton, "btn_cancelar") 
        
        # Configurar campo de contraseña para ocultar el texto
        if self.txt_contraseña:
            self.txt_contraseña.setEchoMode(QLineEdit.Password)
        
        # Si el botón de login no se encontró (y no retornamos por FileNotFoundError)
        if self.btn_login is None:
             self.mostrar_mensaje("Error Crítico de UI", "No se encontró 'btn_login' en la interfaz. Verifique el objectName en Qt Designer.")


    def obtener_credenciales(self):
        """Devuelve el usuario y la contraseña de los campos de texto."""
        # Se asegura de que los widgets existan antes de acceder a .text()
        usuario = self.txt_usuario.text() if self.txt_usuario else ""
        password = self.txt_contraseña.text() if self.txt_contraseña else ""
        
        return usuario, password

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un mensaje de advertencia, error o información."""
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        
        # Usamos QMessageBox.Critical si es un error que detiene el flujo, 
        # o Warning/Information para mensajes de login.
        if "Crítico" in titulo or "Error" in titulo:
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Warning)
            
        msg.exec_()
