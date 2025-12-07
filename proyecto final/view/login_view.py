# view/login_view.py

from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit, QPushButton, QLabel
from PyQt5.uic import loadUi
# Importaciones necesarias para la cámara
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture, QCameraInfo, QImageEncoderSettings
from PyQt5.QtMultimediaWidgets import QCameraViewfinder 
import os

class LoginView(QDialog): 
    """
    Vista encargada de mostrar la interfaz de inicio de sesión con soporte para biometría (cámara).
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- 1. CARGA ROBUSTA DEL UI ---
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        # 🚨 ASEGÚRESE DE QUE ESTA RUTA SEA CORRECTA (ui/login_window.ui)
        ruta_ui = os.path.join(ruta_actual, "..", "ui", "login_window.ui") 

        try:
            loadUi(ruta_ui, self) 
        except FileNotFoundError:
            self.mostrar_alerta("Error Crítico", f"No se encuentra el archivo UI: {ruta_ui}. Verifique la ruta.")
            # Es vital que self.lbl_mensaje exista antes de intentar usarlo
            self.lbl_mensaje = None
            return

        # --- 2. MAPEO DE WIDGETS DE LOGIN (CRÍTICO para el error anterior) ---
        
        # 💡 CRÍTICO: Aseguramos que el atributo interno se llame 'lbl_mensaje', 
        # y asumimos que ese es el objectName en Qt Designer.
        self.lbl_mensaje = self.findChild(QLabel, "lbl_mensaje") 
        
        # Mapeo de otros widgets
        self.btn_login = self.findChild(QPushButton, "btn_login")
        self.txt_usuario = self.findChild(QLineEdit, "txt_usuario")
        self.txt_contraseña = self.findChild(QLineEdit, "txt_contrasena") 
        self.btn_cancelar = self.findChild(QPushButton, "btn_cancelar") 
        
        # Configurar campo de contraseña
        if self.txt_contraseña:
            self.txt_contraseña.setEchoMode(QLineEdit.Password)
        
        # --- 3. MAPEO Y CONFIGURACIÓN DE CÁMARA ---
        self.camera = None
        self.capture = None
        
        # CRÍTICO: Mapear el Viewfinder usando el objectName: "widget"
        self.viewfinder = self.findChild(QCameraViewfinder, "widget") 
        
        # Inicializar los objetos de cámara después de mapear el visor
        self._inicializar_camara()


    def _inicializar_camara(self):
        """Inicializa los objetos QCamera y QCameraImageCapture."""
        
        available_cameras = QCameraInfo.availableCameras()
        
        if available_cameras and self.viewfinder:
            # 1. Objeto Cámara
            self.camera = QCamera(available_cameras[0])
            self.camera.setViewfinder(self.viewfinder)
            
            # 2. Objeto de Captura
            self.capture = QCameraImageCapture(self.camera)
            # Capturar a buffer para procesar en memoria sin guardar en disco (más limpio)
            self.capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer) 
            
            # 3. Configuración de Resolución
            supported_resolutions = self.camera.supportedViewfinderResolutions()
            if supported_resolutions:
                image_settings = QImageEncoderSettings()
                # Usar la resolución soportada
                capture_size = supported_resolutions[0] 
                image_settings.setResolution(capture_size)
                self.capture.setEncodingSettings(image_settings)
            
            self.set_message("Cámara inicializada. Listo para iniciar sesión.")
            print("[LoginView] Cámara inicializada y enlazada al Viewfinder.")
        else:
            self.camera = None
            self.capture = None
            # Si self.lbl_mensaje es None, esta llamada usa el print de fallback
            self.set_message("❌ ERROR: No se detectó cámara en el sistema.", error=True)
            print("[LoginView] ❌ ADVERTENCIA: No se detectó cámara o 'widget' no es un QCameraViewfinder.")
            
    
    # 💡 MÉTODO ROBUSTO PARA ACTUALIZAR MENSAJES (Ahora usado por LoginController)
    def set_message(self, mensaje: str, error: bool = False):
        """Muestra un mensaje de estado o error en la etiqueta lbl_mensaje de forma segura."""
        if self.lbl_mensaje:
            if error:
                self.lbl_mensaje.setText(f"<b style='color: red;'>{mensaje}</b>")
            else:
                self.lbl_mensaje.setText(mensaje)
        else:
            # Esto evita el AttributeError si el widget no se mapeó
            print(f"Alerta UI: El widget de mensaje no está mapeado. Mensaje: {mensaje}")

    def close_and_stop_camera(self):
        """Detiene la cámara y cierra la ventana usando accept()."""
        if self.camera and self.camera.state() == QCamera.ActiveState:
            self.camera.stop()
        self.accept() 


    def obtener_credenciales(self):
        """Devuelve el usuario y la contraseña de los campos de texto."""
        usuario = self.txt_usuario.text().strip() if self.txt_usuario else ""
        password = self.txt_contraseña.text() if self.txt_contraseña else ""
        return usuario, password

    def mostrar_alerta(self, titulo, mensaje):
        """Muestra un mensaje de advertencia o error en un QMessageBox."""
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        
        if "Crítico" in titulo or "Error" in titulo:
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Warning)
            
        msg.exec_()
