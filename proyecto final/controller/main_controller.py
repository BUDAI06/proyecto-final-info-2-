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
        
        # --- 1. Inicialización de Controladores Secundarios ---
        
        # Senales 
        if hasattr(self.vista, 'vista_senales') and self.vista.vista_senales:
            self.vista_senales = self.vista.vista_senales
            self.ctrl_senales = SenalesController(self.vista_senales)
        else:
            self.ctrl_senales = None
            print("ADVERTENCIA: vista_senales no encontrada en MainAppView.")

        # Imagenes
        if hasattr(self.vista, 'vista_imagenes') and self.vista.vista_imagenes:
            self.vista_imagenes = self.vista.vista_imagenes
            self.ctrl_imagenes = ImagenesController(self.vista_imagenes)
        else:
            self.ctrl_imagenes = None
            print("ADVERTENCIA: vista_imagenes no encontrada en MainAppView.")

        # Tabular
        self.ctrl_tabular = TabularController(self.vista)


        # --- 2. Inicialización de Perfil y Estado de Sesión ---
        
        self.usuario = None
        
        # Inicialización del PerfilController (maneja la lógica de las páginas Perfil/Login)
        # PerfilController requiere el MainController (self)
        self.ctrl_perfil = PerfilController(self.vista, self.vista.stacked, self)

        
        # --- 3. Conexión de Navegación y Sesión ---
        
        if hasattr(self.vista, 'btn_ir_imagenes'):
            self.vista.btn_ir_imagenes.clicked.connect(self.vista.mostrar_imagenes)
        if hasattr(self.vista, 'btn_ir_senales'):
            self.vista.btn_ir_senales.clicked.connect(self.vista.mostrar_senales)
        if hasattr(self.vista, 'btn_ir_tabular'):
            self.vista.btn_ir_tabular.clicked.connect(self.vista.mostrar_tabular)
        
        # El botón de perfil lo gestiona PerfilController.
        if hasattr(self.vista, 'btn_ir_perfil'):
             # Conexión del menú a la lógica de PerfilController
             self.vista.btn_ir_perfil.clicked.connect(self.ctrl_perfil.mostrar)
            
        if hasattr(self.vista, 'btn_logout'):
            self.vista.btn_logout.clicked.connect(self.logout)
        
        # Estado inicial
        self.deshabilitar_menu()


    def iniciar_flujo_login(self):
        """Llamado desde main.py. Inicia el ciclo de login de la aplicación."""
        print("--- INICIANDO FLUJO DE LOGIN ---")
        # El PerfilController es quien sabe cómo mostrar el LoginController
        self.ctrl_perfil.mostrar_login_forzado()


    def mostrar_principal(self, usuario):
        """
        Método llamado por LoginController tras un login exitoso.
        Abre la ventana principal e inicializa el estado del usuario.
        """
        self.usuario = usuario
        
        if 'username' in usuario:
            print(f"Login exitoso: {usuario['username']}")
        
        self.vista.mostrar_home()
        # La vista principal se hace visible aquí, si no lo estaba
        if not self.vista.isVisible():
             self.vista.show() 
             
        self.habilitar_menu()
        self.ctrl_perfil._sincronizar_estado_menu() 

    def set_usuario_logueado(self, datos_usuario):
        self.usuario = datos_usuario
        self.habilitar_menu()

    def logout(self):
        self.usuario = None
        self.deshabilitar_menu()
        self.ctrl_perfil.mostrar_login_forzado()

    def deshabilitar_menu(self):
        if hasattr(self.vista, 'btn_ir_imagenes') and self.vista.btn_ir_imagenes:
            self.vista.btn_ir_imagenes.setEnabled(False)
        if hasattr(self.vista, 'btn_ir_senales') and self.vista.btn_ir_senales:
            self.vista.btn_ir_senales.setEnabled(False)
        if hasattr(self.vista, 'btn_ir_tabular') and self.vista.btn_ir_tabular:
            self.vista.btn_ir_tabular.setEnabled(False)
        
        if hasattr(self.vista, 'btn_logout') and self.vista.btn_logout:
            self.vista.btn_logout.hide()
        if hasattr(self.vista, 'btn_ir_perfil') and self.vista.btn_ir_perfil:
            self.vista.btn_ir_perfil.setText("Iniciar sesión")

    def habilitar_menu(self):
        if hasattr(self.vista, 'btn_ir_imagenes') and self.vista.btn_ir_imagenes:
            self.vista.btn_ir_imagenes.setEnabled(True)
        if hasattr(self.vista, 'btn_ir_senales') and self.vista.btn_ir_senales:
            self.vista.btn_ir_senales.setEnabled(True)
        if hasattr(self.vista, 'btn_ir_tabular') and self.vista.btn_ir_tabular:
            self.vista.btn_ir_tabular.setEnabled(True)
        
        if hasattr(self.vista, 'btn_logout') and self.vista.btn_logout:
            self.vista.btn_logout.show()
        if hasattr(self.vista, 'btn_ir_perfil') and self.vista.btn_ir_perfil:
            self.vista.btn_ir_perfil.setText("Perfil")
