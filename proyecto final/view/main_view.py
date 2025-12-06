from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QStackedWidget
from PyQt5.uic import loadUi
from view.imagenes_view import ImagenesView
from view.senales_view import SenalesView
from view.tabular_view import TabularView
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

        # --- 2. REFERENCIAS A WIDGETS DE NAVEGACIÓN ---
        self.btn_ir_imagenes = self.findChild(QPushButton, "btn_ir_imagenes")
        self.btn_ir_senales = self.findChild(QPushButton, "btn_ir_senales")
        self.btn_ir_tabular = self.findChild(QPushButton, "btn_ir_tabular")
        self.btn_ir_perfil = self.findChild(QPushButton, "btn_ir_perfil")
        self.btn_ir_logout = self.findChild(QPushButton, "btn_ir_logout")

        # --- 3. REFERENCIAS AL STACKED WIDGET Y SUS PÁGINAS ---
        self.stacked = self.findChild(QStackedWidget, "stacked_contenido")
        
        # Estas referencias sirven para decirle al StackedWidget qué página mostrar
        self.page_home = self.findChild(QWidget, "page_home")
        self.page_imagenes = self.findChild(QWidget, "page_imagenes")
        self.page_senales = self.findChild(QWidget, "page_senales")
        self.page_tabular = self.findChild(QWidget, "tabular")
        self.page_perfil = self.findChild(QWidget, "perfil")

        self.vista_imagenes = ImagenesView(self)
        self.vista_senales = SenalesView(self) 
        self.vista_tabular = TabularView(self)
        
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