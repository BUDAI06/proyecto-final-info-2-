from view.login_view import LoginView
from model.autenticacion_model import AutenticacionModelo

class LoginController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.vista = LoginView()
        self.modelo = AutenticadorModelo()

        # Evento del botón de login
        self.vista.btn_login.clicked.connect(self.autenticar_usuario)

    def mostrar(self):
        self.vista.show()

    def autenticar_usuario(self):
        usuario, password = self.vista.obtener_credenciales()

        if self.modelo.validar_credenciales(usuario, password):
            # Login exitoso → ir al main controller
            self.vista.close()
            self.main_controller.mostrar_principal(usuario)
        else:
            self.vista.mostrar_mensaje("Error", "Credenciales incorrectas")
