import sys
import os
from PyQt5.QtWidgets import QApplication

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from controller.main_controller import MainController
from view.main_view import MainAppView

def main():
    app = QApplication(sys.argv)

    
    vista_principal = MainAppView()

    controlador = MainController(vista_principal)

    vista_principal.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
