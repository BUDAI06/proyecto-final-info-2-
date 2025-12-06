# Controlador.py

# Importar las clases de los otros archivos
from view import LoginView, MainAppView
from model import AutenticadorModelo
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets

# Controlador.py (Modificar la clase MainAppController)
# Añadir la importación
from model import AutenticadorModelo, ProcesadorOpenCVModelo, ProcesadorImagenesMedicasModelo 
# También necesitarás importar QtWidgets y QFileDialog de PyQt

class MainAppController:
    # ... (código __init__ y mostrar_app_principal existente)
    
    def __init__(self, app):
        # ... (código existente)
        self.procesador_cv_modelo = ProcesadorOpenCVModelo()
        self.procesador_med_modelo = ProcesadorImagenesMedicasModelo() # <-- NUEVA INSTANCIA
        
    def mostrar_app_principal(self, usuario_autenticado):
        # ... (código existente)
        
        # Conexiones para el módulo de Imagen Médica
        self.main_view.btn_cargar_dicom.clicked.connect(self.cargar_imagen_medica)
        self.main_view.sld_axial_slice.valueChanged.connect(self.actualizar_cortes)
        # Conectar los otros dos sliders (coronal y sagital) de forma similar

    def cargar_imagen_medica(self):
        """Maneja la selección del archivo y llama al Modelo."""
        # Abrir diálogo para seleccionar archivo
        import os
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main_view, 
            "Seleccionar Imagen Médica", 
            "", 
            "DICOM Files (*.dcm);;NIFTI Files (*.nii);;All Files (*.*)"
        )
        if file_path:
            # Convertir a ruta relativa respecto al directorio del proyecto
            project_dir = os.path.dirname(os.path.abspath(__file__))
            rel_path = os.path.relpath(file_path, project_dir)
            # 1. Llamar al Modelo para procesar
            if self.procesador_med_modelo.cargar_y_procesar(rel_path):
                
                # 2. Configurar los sliders de la Vista según las dimensiones del volumen
                z, y, x = self.procesador_med_modelo.shape
                self.main_view.configurar_sliders(z, y, x)
                
                # 3. Mostrar metadatos y el corte inicial
                self.main_view.mostrar_metadata(self.procesador_med_modelo.metadata)
                self.actualizar_cortes() # Muestra el primer slice
            else:
                self.main_view.mostrar_mensaje("Error", "El archivo no pudo ser procesado o no es compatible.")

    def actualizar_cortes(self):
        """
        Lee la posición de los sliders y pide al Modelo los cortes correspondientes.
        """
        # Obtener posiciones de los sliders de la Vista
        z_index = self.main_view.sld_axial_slice.value()
        y_index = self.main_view.sld_coronal_slice.value()
        x_index = self.main_view.sld_sagital_slice.value()
        
        # Pedir los cortes al Modelo
        axial_slice = self.procesador_med_modelo.obtener_corte_axial(z_index)
        coronal_slice = self.procesador_med_modelo.obtener_corte_coronal(y_index)
        sagital_slice = self.procesador_med_modelo.obtener_corte_sagital(x_index)
        
        # Pedir a la Vista que muestre los cortes (la Vista necesita un método para esto)
        if axial_slice is not None:
             self.main_view.mostrar_imagen_hu(axial_slice, self.main_view.lbl_axial)
             self.main_view.mostrar_imagen_hu(coronal_slice, self.main_view.lbl_coronal)
             self.main_view.mostrar_imagen_hu(sagital_slice, self.main_view.lbl_sagital)


class LoginController:
    """
    Controlador específico para manejar la ventana de Login.
    """
    def __init__(self, main_app_controller):
        self.main_app_controller = main_app_controller
        self.vista = LoginView()
        self.modelo = AutenticadorModelo()
        
        # Conexión OBLIGATORIA: Enlaza el evento del botón de la Vista a la función del Controlador.
        self.vista.btn_login.clicked.connect(self.autenticar_usuario)

    def autenticar_usuario(self):
        """Función que se ejecuta cuando se hace clic en el botón de login."""
        usuario, password = self.vista.obtener_credenciales()
        
        if self.modelo.validar_credenciales(usuario, password):
            # Llama al controlador principal para hacer el cambio de ventana
            self.main_app_controller.mostrar_app_principal(usuario)
        else:
            # Pide a la Vista que muestre el mensaje de error
            self.vista.mostrar_mensaje("Error", "Credenciales incorrectas o campos vacíos.")