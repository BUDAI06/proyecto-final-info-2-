from PyQt5.QtWidgets import QPushButton, QWidget
from model.autenticacion_model import AutenticacionModel

class PerfilController:
    def __init__(self, main_view, stacked_widget, controlador_principal):

        self.main_view = main_view
        self.stacked = stacked_widget
        self.ctrl_main = controlador_principal
        self.modelo = AutenticacionModel()
        self.usuario_actual = None

        self.page_login = self.stacked.findChild(QWidget, "page_login")
        self.page_perfil = self.stacked.findChild(QWidget, "page_perfil")

        self.txt_user = self.page_login.findChild(object, "txt_login_usuario")
        self.txt_pass = self.page_login.findChild(object, "txt_login_password")
        self.btn_login = self.page_login.findChild(object, "btn_login")
        self.lbl_login_msg = self.page_login.findChild(object, "lbl_login_msg")

        self.lbl_perfil = self.page_perfil.findChild(object, "lbl_perfil_info")
        self.btn_logout = self.page_perfil.findChild(object, "btn_logout")

        self.btn_menu_perfil = self.main_view.findChild(QPushButton, "btn_ir_perfil")

        self.btn_login.clicked.connect(self.intentar_login)
        self.btn_logout.clicked.connect(self.logout)
        self.btn_menu_perfil.clicked.connect(self.mostrar)
        
    def mostrar_login_forzado(self):
        self.usuario_actual = None
        self.stacked.setCurrentWidget(self.page_login)

    def mostrar(self):
        if self.usuario_actual is None:
            self.stacked.setCurrentWidget(self.page_login)
        else:
            self.actualizar_perfil()
            self.stacked.setCurrentWidget(self.page_perfil)

    def intentar_login(self):
        username = self.txt_user.text().strip()
        password = self.txt_pass.text().strip()

        datos = self.modelo.validar_credenciales(username, password)
        
        if datos is None:
            self.lbl_login_msg.setText("Credenciales incorrectas.")
            return
        
        self.usuario_actual = datos
        self.btn_menu_perfil.setText("Perfil")
        self.lbl_login_msg.setText("")

        self.actualizar_perfil()
        self.stacked.setCurrentWidget(self.page_perfil)

        self.ctrl_main.set_usuario_logueado(datos)

    def actualizar_perfil(self):
        if self.usuario_actual:
            info = (
                f"<b>Usuario:</b> {self.usuario_actual['username']}<br>"
                f"<b>Nombre:</b> {self.usuario_actual['nombre']}<br>"
                f"<b>Rol:</b> {self.usuario_actual['rol']}"
            )
            self.lbl_perfil.setText(info)

    def logout(self):
        self.usuario_actual = None
        self.txt_user.setText("")
        self.txt_pass.setText("")
        self.lbl_login_msg.setText("")
        self.lbl_perfil.setText("")
        self.btn_menu_perfil.setText("Iniciar sesión")
        self.stacked.setCurrentWidget(self.page_login)
