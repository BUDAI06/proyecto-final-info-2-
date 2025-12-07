# controller/main_controller.py

from model.base_datos_model import BaseDatosModel
from view.main_view import MainAppView
# Importamos todas las dependencias
from controller.imagenes_controller import ImagenesController
from controller.senales_controller import SenalesController
from controller.tabular_controller import TabularController
from controller.perfil_controller import PerfilController
from PyQt5.QtWidgets import QPushButton

# La clase MainController debe estar definida aquí en el nivel superior
class MainController: 
    """
    Controlador principal de la aplicación.
    Gestiona la inicialización de otros controladores y la navegación entre vistas.
    """
    def __init__(self, vista: MainAppView):
        self.db = BaseDatosModel()
        self.vista = vista
        self.stacked = self.vista.stacked 
        
        # Ocultar la ventana principal inmediatamente en el constructor
        self.vista.hide()
        
        # --- 1. Inicialización de Controladores Secundarios ---
        
        # Senales 
        if hasattr(self.vista, 'vista_senales') and self.vista.vista_senales:
            self.vista_senales = self.vista.vista_senales
            self.ctrl_senales = SenalesController(self.vista_senales)
        else:
            self.ctrl_senales = None

        # Imagenes
        if hasattr(self.vista, 'vista_imagenes') and self.vista.vista_imagenes:
            self.vista_imagenes = self.vista.vista_imagenes
            self.ctrl_imagenes = ImagenesController(self.vista_imagenes)
        else:
            self.ctrl_imagenes = None

        # Tabular
        self.ctrl_tabular = TabularController(self.vista)

        # --- 2. Inicialización de Perfil y Estado de Sesión ---
        
        self.usuario = None
        self.ctrl_perfil = PerfilController(self.vista, self.vista.stacked, self)

        # --- 3. Conexión de Navegación y Sesión ---
        
        if hasattr(self.vista, 'btn_ir_imagenes') and self.vista.btn_ir_imagenes:
            self.vista.btn_ir_imagenes.clicked.connect(self.vista.mostrar_imagenes)
        if hasattr(self.vista, 'btn_ir_senales') and self.vista.btn_ir_senales:
            self.vista.btn_ir_senales.clicked.connect(self.vista.mostrar_senales)
        if hasattr(self.vista, 'btn_ir_tabular') and self.vista.btn_ir_tabular:
            self.vista.btn_ir_tabular.clicked.connect(self.vista.mostrar_tabular)
        
        if hasattr(self.vista, 'btn_ir_perfil') and self.vista.btn_ir_perfil:
             self.vista.btn_ir_perfil.clicked.connect(self.ctrl_perfil.mostrar)
            
        if hasattr(self.vista, 'btn_logout') and self.vista.btn_logout:
            self.vista.btn_logout.clicked.connect(self.logout)
        
        # Estado inicial: Menú deshabilitado
        self.deshabilitar_menu()

    def mostrar_login_inicial(self):
        """Prepara el login. Si el login es un widget interno, se mostrará
        vía ctrl_perfil, pero la ventana sigue oculta hasta que se valide."""
        print("--- FLUJO DE LOGIN INICIADO ---")
        self.ctrl_perfil.mostrar_login_forzado()
        # NOTA: Si el login es una VENTANA aparte, aquí se llamaría a esa ventana.
        # Si el login es parte del .ui de la principal, la ventana DEBE mostrarse 
        # pero podemos forzar que se vea solo el widget de login.
        self.vista.show()

    def mostrar_principal(self, usuario):
        """
        Método llamado tras login exitoso. 
        AQUÍ es donde la ventana principal se hace visible finalmente.
        """
        self.usuario = usuario
        
        if 'username' in usuario:
            print(f"Sesión iniciada para: {usuario['username']}")
        
        # Habilitar elementos antes de mostrar
        self.habilitar_menu()
        self.ctrl_perfil._sincronizar_estado_menu()
        
        # Ir a la página de inicio y MOSTRAR la ventana
        self.vista.mostrar_home()
        self.vista.show() 

    def set_usuario_logueado(self, datos_usuario):
        self.usuario = datos_usuario
        self.habilitar_menu()

    def logout(self):
        self.usuario = None
        self.deshabilitar_menu()
        self.vista.hide() # Ocultar todo al cerrar sesión
        self.ctrl_perfil.mostrar_login_forzado()
        self.vista.show()

    def deshabilitar_menu(self):
        """Oculta los botones laterales para que no existan visualmente durante el login."""
        botones = ['btn_ir_imagenes', 'btn_ir_senales', 'btn_ir_tabular', 'btn_logout']
        for btn_name in botones:
            if hasattr(self.vista, btn_name):
                getattr(self.vista, btn_name).hide()
        
        if hasattr(self.vista, 'btn_ir_perfil'):
            self.vista.btn_ir_perfil.setText("Iniciar sesión")

    def habilitar_menu(self):
        """Muestra los botones laterales una vez el usuario ha ingresado."""
        botones = ['btn_ir_imagenes', 'btn_ir_senales', 'btn_ir_tabular', 'btn_logout']
        for btn_name in botones:
            if hasattr(self.vista, btn_name):
                getattr(self.vista, btn_name).show()
        
        if hasattr(self.vista, 'btn_ir_perfil'):
            self.vista.btn_ir_perfil.setText("Perfil")