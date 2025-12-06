from model.base_datos_model import BaseDatosModel
from view.main_view import MainAppView
from controller.imagenes_controller import ImagenesController
from controller.senales_controller import SenalesController
from controller.tabular_controller import TabularController
from controller.perfil_controller import PerfilController

class MainController:
    def __init__(self, vista):
        self.db = BaseDatosModel()
        self.vista = vista
        self.stacked = self.vista.stacked
        
        # Senales 
        self.vista_senales = self.vista.vista_senales
        self.ctrl_senales = SenalesController(self.vista_senales)

        # Imagenes
        self.vista_imagenes = self.vista.vista_imagenes
        self.ctrl_imagenes = ImagenesController(self.vista_imagenes)

        # Tabular
        self.ctrl_tabular = TabularController(self.vista)


        # Conexion de navegacion
        if hasattr(self.vista, 'btn_ir_imagenes'):
            self.vista.btn_ir_imagenes.clicked.connect(self.vista.mostrar_imagenes)
        if hasattr(self.vista, 'btn_ir_senales'):
            self.vista.btn_ir_senales.clicked.connect(self.vista.mostrar_senales)
        if hasattr(self.vista, 'btn_ir_tabular'):
            self.vista.btn_ir_tabular.clicked.connect(self.vista.mostrar_tabular)
        
        # Usuario
        self.usuario = None
        
        # Iniciar controlador de perfil
        self.ctrl_perfil = PerfilController(self.vista, self.vista.stacked)

        if hasattr(self.vista, 'btn_ir_perfil'):
            self.vista.btn_ir_perfil.clicked.connect(self.ctrl_perfil.mostrar)
        if hasattr(self.vista, 'btn_logout'): # A veces se llama btn_ir_logout
            self.vista.btn_logout.clicked.connect(self.logout)
        

    def mostrar_principal(self, usuario):
        self.usuario = usuario
        # Log en base de datos
        self.db.registrar_log(usuario['username'], "LOGIN", "Inicio de sesión exitoso")
        
        self.vista.mostrar_home()
        self.actualizar_estado_botones()
        self.vista.show()

    def logout(self):
        self.usuario = None
        self.actualizar_estado_botones()
        self.ctrl_perfil.mostrar() 

    def actualizar_estado_botones(self):
        # Lógica visual opcional
        pass