# controller/main_controller.py

from model.base_datos_model import BaseDatosModel
from view.main_view import MainAppView
from controller.imagenes_controller import ImagenesController
from controller.senales_controller import SenalesController
from controller.tabular_controller import TabularController
from controller.perfil_controller import PerfilController

class MainController:
    """
    Controlador principal de la aplicación.
    Gestiona la inicialización de otros controladores y la navegación entre vistas.
    """
    def __init__(self, vista):
        self.db = BaseDatosModel()
        self.vista = vista
        # stacked es el QStackedWidget que maneja las diferentes páginas (Home, Perfil, Tabular, etc.)
        self.stacked = self.vista.stacked 
        
        # --- 1. Inicialización de Controladores Secundarios ---
        
        # Senales 
        if hasattr(self.vista, 'vista_senales'):
            self.vista_senales = self.vista.vista_senales
            self.ctrl_senales = SenalesController(self.vista_senales)
        else:
            print("ADVERTENCIA: vista_senales no encontrada en MainAppView.")

        # Imagenes
        if hasattr(self.vista, 'vista_imagenes'):
            self.vista_imagenes = self.vista.vista_imagenes
            self.ctrl_imagenes = ImagenesController(self.vista_imagenes)
        else:
            print("ADVERTENCIA: vista_imagenes no encontrada en MainAppView.")

        # Tabular
        self.ctrl_tabular = TabularController(self.vista)


        # --- 2. Inicialización de Perfil y Estado de Sesión ---
        
        self.usuario = None
        
        # Inicialización del PerfilController (maneja la lógica de las páginas Perfil/Login)
        self.ctrl_perfil = PerfilController(self.vista, self.vista.stacked, self)

        
        # --- 3. Conexión de Navegación y Sesión (Blindada) ---
        
        if hasattr(self.vista, 'btn_ir_imagenes'):
            self.vista.btn_ir_imagenes.clicked.connect(self.vista.mostrar_imagenes)
        if hasattr(self.vista, 'btn_ir_senales'):
            self.vista.btn_ir_senales.clicked.connect(self.vista.mostrar_senales)
        if hasattr(self.vista, 'btn_ir_tabular'):
            self.vista.btn_ir_tabular.clicked.connect(self.vista.mostrar_tabular)
        
        if hasattr(self.vista, 'btn_ir_perfil'):
            self.vista.btn_ir_perfil.clicked.connect(self.ctrl_perfil.mostrar)
        if hasattr(self.vista, 'btn_logout'):
            self.vista.btn_logout.clicked.connect(self.logout)
        
        # Estado inicial
        self.deshabilitar_menu()
        
    def mostrar_principal(self, usuario):
        """
        Método llamado por LoginController tras un login exitoso.
        Abre la ventana principal e inicializa el estado del usuario.
        """
        self.usuario = usuario
        
        # Log en base de datos
        if 'username' in usuario:
            self.db.registrar_log(usuario['username'], "LOGIN", "Inicio de sesión exitoso")
        
        self.vista.mostrar_home()
        self.actualizar_estado_botones()
        
        # Habilitar menú y mostrar la vista principal (MainAppView)
        self.habilitar_menu()
        self.vista.show() # La vista principal se hace visible aquí

    def set_usuario_logueado(self, datos_usuario):
        """Método auxiliar para actualizar el estado del usuario y menú desde otros controladores."""
        self.usuario = datos_usuario
        self.habilitar_menu()

    def logout(self):
        """Maneja el cierre de sesión."""
        self.usuario = None
        
        # Deshabilitar menú y redirigir al login
        self.deshabilitar_menu()
        self.ctrl_perfil.mostrar_login_forzado()

    def deshabilitar_menu(self):
        """Deshabilita los botones de navegación y cambia el texto de perfil/login."""
        if hasattr(self.vista, 'btn_ir_imagenes'):
            self.vista.btn_ir_imagenes.setEnabled(False)
        if hasattr(self.vista, 'btn_ir_senales'):
            self.vista.btn_ir_senales.setEnabled(False)
        if hasattr(self.vista, 'btn_ir_tabular'):
            self.vista.btn_ir_tabular.setEnabled(False)
        
        if hasattr(self.vista, 'btn_logout'):
            self.vista.btn_logout.hide()
        if hasattr(self.vista, 'btn_ir_perfil'):
            self.vista.btn_ir_perfil.setText("Iniciar sesión")

    def habilitar_menu(self):
        """Habilita los botones de navegación y muestra el estado de perfil."""
        if hasattr(self.vista, 'btn_ir_imagenes'):
            self.vista.btn_ir_imagenes.setEnabled(True)
        if hasattr(self.vista, 'btn_ir_senales'):
            self.vista.btn_ir_senales.setEnabled(True)
        if hasattr(self.vista, 'btn_ir_tabular'):
            self.vista.btn_ir_tabular.setEnabled(True)
        
        if hasattr(self.vista, 'btn_logout'):
            self.vista.btn_logout.show()
        if hasattr(self.vista, 'btn_ir_perfil'):
            self.vista.btn_ir_perfil.setText("Perfil")

    def actualizar_estado_botones(self):
        """Ejecuta cualquier lógica adicional para el estado de los botones (ej: permisos de rol)."""
        pass
