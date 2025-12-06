import sys
from PyQt5.QtWidgets import QApplication
from controller.main_controller import MainController
from view.main_view import MainAppView

if __name__ == '__main__':

    app = QApplication(sys.argv)

    # Crear la vista principal
    vista = MainAppView()

    # Crear el controlador principal usando la vista
    controller = MainController(vista)

    # Mostrar la vista principal
    vista.show()

    # Iniciar mostrando login/perfil
    controller.ctrl_perfil.mostrar()
    
    sys.exit(app.exec_())
