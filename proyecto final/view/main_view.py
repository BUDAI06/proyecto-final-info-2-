# view/main_view.py

from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QStackedWidget
from PyQt5.uic import loadUi
from view.imagenes_view import ImagenesView
from view.senales_view import SenalesView
from view.tabular_view import TabularView
# IMPORTACIONES CRÍTICAS para la cámara y el viewfinder
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture, QImageEncoderSettings
from PyQt5.QtMultimediaWidgets import QCameraViewfinder 
from PyQt5.QtCore import QSize
import os

class MainAppView(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- 1. CARGA ROBUSTA DEL UI ---
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.join(ruta_actual, "..", "ui", "main_app_window.ui")
        
        try:
            loadUi(ruta_ui, self)
        except FileNotFoundError:
            print(f"ERROR CRÍTICO: No se encontró el archivo de diseño en: {ruta_ui}")
            return

        # --- 2. Mapeo del Viewfinder de la Cámara ---
        # Asegúrate de que el objectName en Qt Designer sea 'viewfinder_camara'
        self.viewfinder = self.findChild(QCameraViewfinder, "viewfinder_camara") 

        # --- (Resto de mapeo de navegación omitido por brevedad) ---
        self.stacked = self.findChild(QStackedWidget, "stacked_contenido")
        self.page_home = self.findChild(QWidget, "page_home")
        self.page_imagenes = self.findChild(QWidget, "page_imagenes")
        self.page_senales = self.findChild(QWidget, "page_senales")
        self.page_tabular = self.findChild(QWidget, "page_tabular")
        self.page_perfil = self.findChild(QWidget, "page_perfil")
        
        self.vista_imagenes = ImagenesView(self)
        self.vista_senales = SenalesView(self) 
        self.vista_tabular = TabularView(self)
        
        
        # --- 3. CONFIGURACIÓN DE CÁMARA (CRÍTICO) ---
        
        self.camera = QCamera()
        self.capture = QCameraImageCapture(self.camera)
        self.capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer) 
        
        # Conectar la cámara al Viewfinder si existe
        if self.viewfinder and self.camera:
            self.camera.setViewfinder(self.viewfinder)
            print("[CÁMARA] Viewfinder conectado.")
        
        # Configuración de resolución (solución al AttributeError)
        supported_resolutions = self.camera.supportedViewfinderResolutions()

        if supported_resolutions:
            image_settings = QImageEncoderSettings()
            capture_size = supported_resolutions[0] 
            image_settings.setResolution(capture_size)
            self.capture.setEncodingSettings(image_settings)

        # La cámara se inicia y se detiene aquí para validar el hardware, luego el controlador la gestiona.
        self.camera.start()
        self.camera.stop()
        
        
    # --- MÉTODOS DE NAVEGACIÓN ---

    def mostrar_home(self):
        if self.page_home:
            self.stacked.setCurrentWidget(self.page_home)
            
    def mostrar_imagenes(self):
        if self.page_imagenes:
            self.stacked.setCurrentWidget(self.page_imagenes)

    def mostrar_senales(self):
        if self.page_senales:
            self.stacked.setCurrentWidget(self.page_senales)

    def mostrar_tabular(self):
        if self.page_tabular:
            self.stacked.setCurrentWidget(self.page_tabular)

    def mostrar_perfil(self):
        if self.page_perfil:
            self.stacked.setCurrentWidget(self.page_perfil)

