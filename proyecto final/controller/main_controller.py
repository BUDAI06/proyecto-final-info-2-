from model.base_datos_model import BaseDatosModel
from view.main_view import MainAppView

from controller.imagenes_controller import ImagenesController
from controller.senales_controller import SenalesController
from controller.tabular_controller import TabularController
from controller.perfil_controller import PerfilController

class MainController:
    def __init__(self,vista):
        self.db = BaseDatosModel()
        self.vista = vista
        self.stacked = self.vista.stacked
        # --- SEÑALES ---
        self.vista_senales = self.vista.vista_senales
        self.ctrl_senales = SenalesController(self.vista_senales)

        # --- IMÁGENES ---
        self.vista_imagenes = self.vista.vista_imagenes
        self.ctrl_imagenes = ImagenesController(self.vista_imagenes)

        # --- TABULAR ---
        self.vista_tabular = self.vista.vista_tabular
        self.ctrl_tabular = TabularController(self.vista_tabular)


        # --- CONEXIÓN DE NAVEGACIÓN (Botones del menú lateral) ---
        self.vista.btn_ir_imagenes.clicked.connect(self.vista.mostrar_imagenes)
        self.vista.btn_ir_senales.clicked.connect(self.vista.mostrar_senales)
        self.vista.btn_ir_tabular.clicked.connect(self.vista.mostrar_tabular)
        
        # --- USUARIO / PERFIL ---
        self.usuario = None  # user actual (None = no logueado)
        
        # Conexión botón perfil
        self.ctrl_perfil = PerfilController(self.vista, self.vista.stacked)

        
        # Lógica de botones de perfil
        self.vista.btn_ir_perfil.clicked.connect(self.ctrl_perfil.mostrar)
        self.vista.btn_ir_logout.clicked.connect(self.logout)
        

    def mostrar_principal(self, usuario):
        self.usuario = usuario
        self.db.registrar_log(usuario['username'], "LOGIN", "Inicio de sesión exitoso")
        self.vista.mostrar_home()
        self.actualizar_estado_botones() # Actualizamos la UI al entrar
        self.vista.show()

    def logout(self):
        self.usuario = None
        self.actualizar_estado_botones()
        self.ctrl_perfil.mostrar()  # regresar al login o mostrar pantalla de logout

    def actualizar_estado_botones(self):
        if self.usuario is None:
            self.vista.btn_ir_perfil.setText("Iniciar sesión")
            self.vista.btn_ir_logout.hide()
        else:
            self.vista.btn_ir_perfil.setText("Perfil")
            self.vista.btn_ir_logout.show()
