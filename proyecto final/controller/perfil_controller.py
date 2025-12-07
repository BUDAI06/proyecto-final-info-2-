# controller/perfil_controller.py

from PyQt5.QtWidgets import QPushButton, QWidget, QLabel
from model.autenticacion_model import AutenticacionModel 
from controller.login_controller import LoginController # <--- Necesario para la cámara

class PerfilController:
    """
    Controlador puente que gestiona la página de Perfil y DELEGA la autenticación
    y la captura de cámara al LoginController.
    """
    def __init__(self, main_view, stacked_widget, controlador_principal):

        self.main_view = main_view
        self.stacked = stacked_widget
        self.ctrl_main = controlador_principal
        self.modelo = AutenticacionModel() 
        
        # El usuario actual se obtiene del MainController (la fuente de verdad)
        self.usuario_actual = self.ctrl_main.usuario 

        # --- 1. Inicialización del Controlador de Login/Cámara ---
        # El LoginController ahora solo requiere el MainController (2 argumentos en total)
        self.ctrl_login = LoginController(self.ctrl_main) 

        # --- 2. Mapeo de Widgets de Navegación y Perfil ---
        
        self.page_perfil = self.stacked.findChild(QWidget, "page_perfil")
        
        # Mapeo de widgets de perfil
        if self.page_perfil:
            self.lbl_perfil = self.page_perfil.findChild(QLabel, "lbl_perfil_info")
            self.btn_logout = self.page_perfil.findChild(QPushButton, "btn_logout")
        else:
            self.lbl_perfil = None
            self.btn_logout = None
        
        self.btn_menu_perfil = self.main_view.findChild(QPushButton, "btn_ir_perfil")

        # --- 3. Conexiones de Botones ---
        
        if self.btn_logout is not None:
            self.btn_logout.clicked.connect(self.logout)
        
        if self.btn_menu_perfil is not None:
            self.btn_menu_perfil.clicked.connect(self.mostrar)
            
        self._sincronizar_estado_menu()


    def _sincronizar_estado_menu(self):
        """Ajusta el texto del botón 'Perfil' según si hay sesión iniciada."""
        self.usuario_actual = self.ctrl_main.usuario
        if self.usuario_actual is None:
            if self.btn_menu_perfil:
                self.btn_menu_perfil.setText("Iniciar sesión")
        else:
            if self.btn_menu_perfil:
                self.btn_menu_perfil.setText("Perfil")

    def mostrar_login_forzado(self):
        """
        Muestra la ventana de Login (cámara) y detiene el menú principal. 
        Llamado al inicio de la aplicación o cuando se requiere login.
        """
        self.usuario_actual = None
        self.ctrl_main.deshabilitar_menu()
        
        # Delega la tarea de mostrar la ventana de login (cámara) al LoginController
        self.ctrl_login.mostrar_login()
        
        # 🚨 LÍNEA CRÍTICA ELIMINADA:
        # La ventana principal (self.main_view) NO se muestra aquí. 
        # Debe permanecer oculta hasta MainController.mostrar_principal().
        # self.main_view.show() # <- ¡Esta línea fue eliminada!

    def mostrar(self):
        """
        Muestra la página de Perfil si el usuario está logueado, o INICIA el proceso de Login.
        """
        self.usuario_actual = self.ctrl_main.usuario 
        
        if self.usuario_actual is None:
            # Si no hay usuario, iniciamos el proceso de login (que abre la ventana externa)
            self.mostrar_login_forzado()
        else:
            # Si hay usuario, navegamos a la página de perfil dentro del stacked widget
            if self.page_perfil:
                self.actualizar_perfil()
                self.stacked.setCurrentWidget(self.page_perfil)
                self.ctrl_main.habilitar_menu() 
    
    def actualizar_perfil(self):
        """Muestra los datos del usuario logueado en la etiqueta lbl_perfil_info."""
        self.usuario_actual = self.ctrl_main.usuario 
        
        if self.usuario_actual and self.lbl_perfil:
            info = (
                f"<b>Usuario:</b> {self.usuario_actual.get('username', 'N/A')}<br>"
                f"<b>Nombre:</b> {self.usuario_actual.get('nombre', 'N/A')}<br>"
                f"<b>Rol:</b> {self.usuario_actual.get('rol', 'N/A')}"
            )
            if isinstance(self.lbl_perfil, QLabel):
                self.lbl_perfil.setText(info)

    def logout(self):
        """Cierra la sesión del usuario."""
        if self.lbl_perfil:
             if isinstance(self.lbl_perfil, QLabel):
                self.lbl_perfil.setText("")
            
        self.ctrl_main.logout()
        self._sincronizar_estado_menu()
        
        # Forzar la vista de login después del logout
        self.mostrar_login_forzado()
