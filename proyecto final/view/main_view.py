# view/main_view.py

from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QStackedWidget
from PyQt5.uic import loadUi
from view.imagenes_view import ImagenesView
from view.senales_view import SenalesView
from view.tabular_view import TabularView

from PyQt5.QtMultimedia import QCamera, QCameraImageCapture, QImageEncoderSettings
from PyQt5.QtCore import QSize
import os

class MainAppView(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- CARGA DEL UI ---
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.join(ruta_actual, "..", "ui", "main_app_window.ui")
        
        try:
            loadUi(ruta_ui, self)
        except FileNotFoundError:
            print(f"ERROR: No se encontró el archivo UI en: {ruta_ui}")

        # --- WIDGETS DE NAVEGACIÓN ---
        self.btn_ir_imagenes = self.findChild(QPushButton, "btn_ir_imagenes")
        self.btn_ir_senales = self.findChild(QPushButton, "btn_ir_senales")
        self.btn_ir_tabular = self.findChild(QPushButton, "btn_ir_tabular")
        self.btn_ir_perfil = self.findChild(QPushButton, "btn_ir_perfil")
        self.btn_ir_logout = self.findChild(QPushButton, "btn_ir_logout")

        # --- STACKED ---
        self.stacked = self.findChild(QStackedWidget, "stacked_contenido")

        self.page_home = self.findChild(QWidget, "page_home")
        self.page_imagenes = self.findChild(QWidget, "page_imagenes")
        self.page_senales = self.findChild(QWidget, "page_senales")
        self.page_tabular = self.findChild(QWidget, "tabular")
        self.page_perfil = self.findChild(QWidget, "perfil")

        # --- VISTAS ---
        self.vista_imagenes = ImagenesView(self)
        self.vista_senales = SenalesView(self) 
        self.vista_tabular = TabularView(self)

        # --- CÁMARA ---
        self._configurar_camara()

    # -------------------------------------------------

    def _configurar_camara(self):
        # Buscar el widget viewfinder dentro del UI
        self.viewfinder = self.findChild(QWidget, "viewfinder")

        self.camera = QCamera()
        self.capture = QCameraImageCapture(self.camera)

        # Configuración básica
        self.capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)

        # Si el viewfinder EXISTE, conectar la cámara
        if self.viewfinder:
            try:
                self.camera.setViewfinder(self.viewfinder)
            except Exception as e:
                print("[CÁMARA] Error al vincular viewfinder:", e)
        else:
            print("[CÁMARA] No existe widget 'viewfinder'. Cámara no conectada.")

        # Intentar configurar resolución segura
        try:
            resolutions = self.camera.supportedViewfinderResolutions()
            if resolutions:
                img_settings = QImageEncoderSettings()
                img_settings.setResolution(resolutions[0])
                self.capture.setEncodingSettings(img_settings)
        except Exception as e:
            print("[CÁMARA] Error configurando resolución:", e)

        # Solo iniciar cámara si hay viewfinder
        if self.viewfinder:
            try:
                self.camera.start()
                self.camera.stop()
            except Exception as e:
                print("[CÁMARA] Error iniciando cámara:", e)

    # -------------------------------------------------

    # --- MÉTODOS DE NAVEGACIÓN ---
    def mostrar_home(self):
        self.stacked.setCurrentWidget(self.page_home)

    def mostrar_imagenes(self):
        self.stacked.setCurrentWidget(self.page_imagenes)

    def mostrar_senales(self):
        self.stacked.setCurrentWidget(self.page_senales)

    def mostrar_tabular(self):
        self.stacked.setCurrentWidget(self.page_tabular)

    def mostrar_perfil(self):
        self.stacked.setCurrentWidget(self.page_perfil)
