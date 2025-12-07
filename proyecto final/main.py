# main.py

import sys
import os
from PyQt5.QtWidgets import QApplication

# Configuración de ruta 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir) 

from controller.main_controller import MainController
from view.main_view import MainAppView

def main():
    app = QApplication(sys.argv)
    
    # 2. Instanciar la VISTA PRINCIPAL
    vista_principal = MainAppView() 

    # 🚨 CRÍTICO: OCULTAR LA VISTA PRINCIPAL INMEDIATAMENTE (Correcto)
    vista_principal.hide() 

    # 3. Instanciar los Controladores
    controlador_principal = MainController(vista_principal)

    # 4. Iniciar el flujo de Login forzado (Correcto)
    # Esto llama a LoginController, que sí llama a su propia ventana de cámara/login.
    controlador_principal.iniciar_flujo_login() 
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
