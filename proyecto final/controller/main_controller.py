# controlador/main_controller.py
from view.main_view import MainAppView
from view.imagenes_view import ImagenesView
from controller.imagenes_controller import ImagenesController

class MainController:
    def __init__(self):
        self.vista = MainAppView()

        
        self.vista_imagenes = ImagenesView()
        self.ctrl_imagenes = ImagenesController(self.vista_imagenes)
        self.vista.page_imagenes.layout().addWidget(self.vista_imagenes)

        # Conexión de navegación
        self.vista.btn_ir_imagenes.clicked.connect(self.vista.mostrar_imagenes)
        self.vista.btn_ir_senales.clicked.connect(self.vista.mostrar_senales)
        self.vista.btn_ir_tabular.clicked.connect(self.vista.mostrar_tabular)
        self.vista.btn_ir_perfil.clicked.connect(self.vista.mostrar_perfil)

        # Botón logout → volver al login
        self.vista.btn_ir_logout.clicked.connect(self.logout)

    def mostrar_principal(self, usuario):
        self.usuario = usuario
        self.vista.mostrar_home()
        self.vista.show()

    def logout(self):
        self.vista.close()
        # Return to login when we add app bootstrap logic
