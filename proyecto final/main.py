# main.py
import sys
from PyQt5.QtWidgets import QApplication
from controller.main_controller import MainController
from controller.login_controller import LoginController

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_ctrl = MainController()
    login_ctrl = LoginController(main_ctrl)

    login_ctrl.mostrar()

    sys.exit(app.exec_())
