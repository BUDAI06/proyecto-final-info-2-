# main.py
import sys
from PyQt5.QtWidgets import QApplication
from controller import controlador
# NOTA: Necesitas una clase MainAppController dummy por ahora
# para simular la apertura de la ventana principal.

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Crear un Controlador de la App principal (dummy por ahora)
    class DummyMainAppController:
        def show_main_window(self):
            print("Login exitoso. Abrir la ventana principal de la aplicación.")
            # Aquí iría la lógica para instanciar la Vista principal
            pass 
            
    main_controller = DummyMainAppController()
    
    # Iniciar el proceso de login
    login_controller = LoginController(main_controller)
    
    sys.exit(app.exec_())