# controller/login_controller.py

from view.login_view import LoginView
from model.base_datos_model import BaseDatosModel 

from PyQt5.QtGui import QImage
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, QCoreApplication, Qt
import base64
import sys

class LoginController:
    """
    Controlador encargado de la autenticación de usuario, la captura de la foto 
    al iniciar sesión, y la transición de control al MainController.
    """
    # CRÍTICO: Eliminamos main_app_view del constructor
    def __init__(self, main_controller): 
        self.main_ctrl = main_controller
        self.db = BaseDatosModel() 
        self.login_view = LoginView() # Instancia de la ventana de cámara/login
        
        self.datos_usuario_logueado = None
        
        # Conexiones de botones (se mantienen)
        if self.login_view.btn_login is not None:
             self.login_view.btn_login.clicked.connect(self.handle_login) 
        
        if hasattr(self.login_view, 'btn_cancelar') and self.login_view.btn_cancelar is not None:
             self.login_view.btn_cancelar.clicked.connect(self.login_view.close_and_stop_camera)

    # --- Flujo de Navegación ---
    
    def mostrar_login(self):
        """Muestra la ventana de login al inicio de la aplicación."""
        self.login_view.show()
        # Iniciar la cámara para mostrar el viewfinder al abrir la ventana
        if self.login_view.camera:
            self.login_view.camera.start()
            # ✅ CORRECCIÓN 1: Usamos set_message()
            self.login_view.set_message("Ingrese sus credenciales y tome la foto.")

    # --- Flujo de Autenticación y Captura ---

    def handle_login(self):
        """Gestiona el intento de login: valida credenciales e inicia la captura de foto."""
        
        usuario_raw, password_raw = self.login_view.obtener_credenciales()
        
        usuario = usuario_raw.strip().lower()
        password = password_raw.strip()
        
        datos_usuario = self.db.validar_credenciales(usuario, password) 
        
        if datos_usuario:
            self.datos_usuario_logueado = datos_usuario
            
            # 🚨 CORRECCIÓN CRÍTICA (Anterior Línea 57)
            # ✅ Reemplazamos .lbl_mensaje.setText() por el método seguro set_message()
            self.login_view.set_message("Credenciales correctas. Tomando foto...")
            
            self._iniciar_captura_y_procesamiento()
            
        else:
            # ✅ CORRECCIÓN 3: Usamos set_message() para errores en la etiqueta
            self.login_view.set_message("Usuario o Contraseña incorrectos.", error=True)


    def _iniciar_captura_y_procesamiento(self):
        """Prepara la cámara, conecta la señal de captura y dispara la foto."""
        
        # 🚨 CRÍTICO: Usamos los objetos de cámara de self.login_view
        if not self.login_view.capture or not self.login_view.camera:
            print("Error: Objetos de cámara no disponibles en la vista.")
            # ✅ CORRECCIÓN 4: Usamos set_message() para el error de cámara
            self.login_view.set_message("Objetos de cámara no disponibles. Acceso permitido sin foto.", error=True)
            
            self.login_view.close_and_stop_camera() 
            self.main_ctrl.mostrar_principal(self.datos_usuario_logueado)
            return

        try:
            # 1. Conectar la señal de captura
            if self.login_view.camera.state() != self.login_view.camera.ActiveState:
                 self.login_view.camera.start()

            # Desconectar si estaba conectada previamente para evitar múltiples disparos
            try:
                self.login_view.capture.imageCaptured.disconnect()
            except:
                pass 
                
            self.login_view.capture.imageCaptured.connect(self.procesar_y_guardar_foto)
            
            # 2. Disparar la captura 
            self.login_view.capture.capture()
            
        except Exception as e:
            # Fallback en caso de fallo de cámara
            print(f"Error de Cámara (Fallback): {e}")
            self.login_view.set_message(f"No se pudo iniciar la cámara: {e}. Acceso permitido sin foto.", error=True)
            
            self.login_view.close_and_stop_camera() 
            self.main_ctrl.mostrar_principal(self.datos_usuario_logueado)

    # --- Flujo de Procesamiento ---
    
    def procesar_y_guardar_foto(self, id_captura, imagen_qimage):
        """
        Procesa la QImage capturada: 
        1. Convierte a Blanco y Negro.
        2. Codifica a JPG y luego a Base64.
        3. Guarda en la base de datos.
        """
        
        # 1. Detener la cámara y desconectar la señal (usando self.login_view)
        self.login_view.camera.stop()
        try:
            self.login_view.capture.imageCaptured.disconnect(self.procesar_y_guardar_foto)
        except TypeError:
             pass
        
        # 2. CONVERSIÓN A ESCALA DE GRISES (Blanco y Negro)
        imagen_bn = imagen_qimage.convertToFormat(QImage.Format_Grayscale8) 
        
        # 3. CONVERSIÓN A BASE64
        buffer = QByteArray()
        buffer_dispositivo = QBuffer(buffer)
        buffer_dispositivo.open(QIODevice.WriteOnly)
        
        # Guardar la imagen B&N en el buffer como JPG con compresión media
        imagen_bn.save(buffer_dispositivo, "JPG", 80)
        buffer_dispositivo.close()
        
        # Codificar los datos binarios del buffer a Base64 y luego a string
        datos_base64 = base64.b64encode(buffer.data()).decode('utf-8')
        
        # 4. GUARDAR EN LA BASE DE DATOS
        user_id = self.datos_usuario_logueado.get('id') 
        if user_id:
            self.db.guardar_foto_perfil(user_id, datos_base64)
            
        # 5. TRANSICIÓN FINAL
        self.login_view.close() # Cierra la ventana de login
        self.main_ctrl.mostrar_principal(self.datos_usuario_logueado)
