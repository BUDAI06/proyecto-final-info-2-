# controller/perfil_controller.py

from PyQt5.QtWidgets import QPushButton, QWidget
from model.autenticacion_model import AutenticacionModel 
from controller.login_controller import LoginController # <--- 🚨 CRÍTICO: Necesario para la cámara

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
        # Le pasamos el MainController y la vista principal (para la cámara).
        self.ctrl_login = LoginController(self.ctrl_main, self.main_view)

        # --- 2. Mapeo de Widgets de Navegación y Perfil ---
        
        # Estas páginas solo se usan para la navegación interna si el usuario está logueado
        # NOTA: page_login en el stacked widget ya no se usa para la lógica de login.
        self.page_login = self.stacked.findChild(QWidget, "page_login")
        self.page_perfil = self.stacked.findChild(QWidget, "page_perfil")
        
        # Mapeo de widgets de perfil
        if self.page_perfil:
            self.lbl_perfil = self.page_perfil.findChild(object, "lbl_perfil_info")
            self.btn_logout = self.page_perfil.findChild(object, "btn_logout")
        else:
            self.lbl_perfil = None
            self.btn_logout = None
        
        self.btn_menu_perfil = self.main_view.findChild(QPushButton, "btn_ir_perfil")

        # --- 3. Conexiones de Botones ---
        
        # btn_login ya NO se conecta aquí, lo hace el LoginController externo.
        
        if self.btn_logout is not None:
            # Conecta el botón de la página de perfil a la función logout
            self.btn_logout.clicked.connect(self.logout)
        
        if self.btn_menu_perfil is not None:
            # Conecta el botón del menú principal a la función mostrar
            self.btn_menu_perfil.clicked.connect(self.mostrar)
            
        # El MainController se encargará de llamar a deshabilitar_menu() al inicio.


    def mostrar_login_forzado(self):
        """
        Muestra la vista de Login DELEGANDO la tarea al LoginController externo.
        Esto activa la ventana con la cámara.
        """
        self.usuario_actual = None
        # 🚨 CRÍTICO: Llamamos al controlador de Login/Cámara.
        self.ctrl_login.mostrar_login()
        
        # Asegura que la ventana principal esté visible
        self.main_view.show()

    def mostrar(self):
        """
        Muestra la página de Perfil si el usuario está logueado, o INICIA el proceso de Login.
        """
        # Sincronizar el estado del usuario con el MainController
        self.usuario_actual = self.ctrl_main.usuario 
        
        if self.usuario_actual is None:
            # Si no hay usuario, iniciamos el proceso de login (que abre la ventana externa)
            self.mostrar_login_forzado()
        else:
            # Si hay usuario, navegamos a la página de perfil dentro del stacked widget
            if self.page_perfil:
                self.actualizar_perfil()
                self.stacked.setCurrentWidget(self.page_perfil)
    
    # El método intentar_login ha sido ELIMINADO ya que la autenticación es delegada a LoginController.

    def actualizar_perfil(self):
        """Muestra los datos del usuario logueado en la etiqueta lbl_perfil_info."""
        # Sincronizar el estado del usuario
        self.usuario_actual = self.ctrl_main.usuario 
        
        if self.usuario_actual and self.lbl_perfil:
            info = (
                f"<b>Usuario:</b> {self.usuario_actual.get('username', 'N/A')}<br>"
                f"<b>Nombre:</b> {self.usuario_actual.get('nombre', 'N/A')}<br>"
                f"<b>Rol:</b> {self.usuario_actual.get('rol', 'N/A')}"
            )
            self.lbl_perfil.setText(info)

    def logout(self):
        """Cierra la sesión del usuario."""
        self.usuario_actual = None
        
        # Limpiar la información de la vista
        if self.lbl_perfil:
            self.lbl_perfil.setText("")
            
        # Delegar el manejo de la interfaz y la redirección al MainController
        self.ctrl_main.logout()
        
        # El MainController ahora se encarga de la redirección al login.
