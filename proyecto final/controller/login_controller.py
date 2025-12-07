# controller/login_controller.py

from view.login_view import LoginView
from model.base_datos_model import BaseDatosModel 

from PyQt5.QtGui import QImage
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, QCoreApplication
import base64
import sys

class LoginController:
    """
    Controlador encargado de la autenticación de usuario, la captura de la foto 
    al iniciar sesión, y la transición de control al MainController.
    """
    def __init__(self, main_controller, main_app_view):
        self.main_ctrl = main_controller
        self.main_app_view = main_app_view 
        self.db = BaseDatosModel() 
        self.login_view = LoginView()
        
        self.datos_usuario_logueado = None
        
        if self.login_view.btn_login is not None:
             self.login_view.btn_login.clicked.connect(self.handle_login) 
        
        if hasattr(self.login_view, 'btn_cancelar') and self.login_view.btn_cancelar is not None:
             self.login_view.btn_cancelar.clicked.connect(QCoreApplication.instance().quit)


    def handle_login(self):
        """Gestiona el intento de login: valida credenciales e inicia la captura de foto."""
        
        usuario_raw, password_raw = self.login_view.obtener_credenciales()
        
        # 🚨 CRÍTICO: Limpiar espacios y normalizar (a minúsculas) el usuario
        usuario = usuario_raw.strip().lower()
        password = password_raw.strip()
        
        # 2. Validar las credenciales
        datos_usuario = self.db.validar_credenciales(usuario, password) 
        
        if datos_usuario:
            self.datos_usuario_logueado = datos_usuario
            
            # 3. Iniciar el proceso de captura de la foto
            self._iniciar_captura_y_procesamiento()
            
        else:
            self.login_view.mostrar_mensaje("Error de Login", "Usuario o Contraseña incorrectos.")


    def _iniciar_captura_y_procesamiento(self):
        """Prepara la cámara, conecta la señal de captura y dispara la foto."""
        try:
            # 1. Conectar la señal de captura
            self.main_app_view.capture.imageCaptured.connect(self.procesar_y_guardar_foto)
            
            # 2. Iniciar la cámara (para mostrar el viewfinder)
            self.main_app_view.camera.start()
            
            # 3. Disparar la captura 
            self.main_app_view.capture.capture()
            
        except Exception as e:
            # Fallback en caso de fallo de cámara
            print(f"Error de Cámara (Fallback): {e}")
            self.login_view.mostrar_mensaje("Error de Cámara", f"No se pudo iniciar la cámara: {e}. Acceso permitido sin foto.")
            
            # Transición sin la foto
            self.login_view.close() 
            self.main_ctrl.mostrar_principal(self.datos_usuario_logueado)

    def procesar_y_guardar_foto(self, id_captura, imagen_qimage):
        """
        Procesa la QImage capturada: 
        1. Convierte a Blanco y Negro.
        2. Codifica a JPG y luego a Base64.
        3. Guarda en la base de datos.
        """
        
        # 1. Detener la cámara y desconectar la señal
        self.main_app_view.camera.stop()
        try:
            self.main_app_view.capture.imageCaptured.disconnect(self.procesar_y_guardar_foto)
        except TypeError:
            pass

        # 2. CONVERSIÓN A ESCALA DE GRISES (Blanco y Negro)
        imagen_bn = imagen_qimage.convertToFormat(QImage.Format_Grayscale8) 
        
        # 3. CONVERSIÓN A BASE64
        buffer = QByteArray()
        buffer_dispositivo = QBuffer(buffer)
        buffer_dispositivo.open(QIODevice.WriteOnly)
        
        # Guardar la imagen en el buffer como JPG con compresión
        imagen_bn.save(buffer_dispositivo, "JPG", 80)
        buffer_dispositivo.close()
        
        # Codificar los datos binarios del buffer a Base64 y luego a string
        datos_base64 = base64.b64encode(buffer.data()).decode('utf-8')
        
        # 4. GUARDAR EN LA BASE DE DATOS
        user_id = self.datos_usuario_logueado.get('id') 
        if user_id:
            self.db.guardar_foto_perfil(user_id, datos_base64)
        
        # 5. TRANSICIÓN FINAL
        self.login_view.close() 
        self.main_ctrl.mostrar_principal(self.datos_usuario_logueado)

    def mostrar_login(self):
        """Muestra la ventana de login al inicio de la aplicación."""
        self.login_view.show()