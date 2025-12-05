from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QStackedWidget
from PyQt5.uic import loadUi
from view.imagenes_view import ImagenesView
from view.senales_view import SenalesView
from view.tabular_view import TabularView

class MainAppView(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi("ui/main_app_window.ui", self)

        # --- Botones de navegacion ---
        self.btn_ir_imagenes = self.findChild(QPushButton, "btn_ir_imagenes")
        self.btn_ir_senales = self.findChild(QPushButton, "btn_ir_senales")
        self.btn_ir_tabular = self.findChild(QPushButton, "btn_ir_tabular")
        self.btn_ir_perfil = self.findChild(QPushButton, "btn_ir_perfil")
        self.btn_ir_logout = self.findChild(QPushButton, "btn_ir_logout")

        # --- Contenedor dinamico ---
        self.stacked = self.findChild(QStackedWidget, "stacked_contenido")

        # --- Páginas internas aunq esten vacias ---
        self.page_home = self.findChild(QWidget, "page_home")
        self.page_imagenes = self.findChild(QWidget, "page_imagenes")
        self.page_senales = self.findChild(QWidget, "page_senales")
        self.page_tabular = self.findChild(QWidget, "tabular")
        self.page_perfil = self.findChild(QWidget, "perfil")

        # Insertar vistas reales dentro de las páginas
        self.vista_imagenes = ImagenesView()
        self.vista_senales = SenalesView()
        self.vista_tabular = TabularView()

        # Añadir vistas a las páginas
        self.page_imagenes.layout() or self.page_imagenes.setLayout(QVBoxLayout())
        self.page_imagenes.layout().addWidget(self.vista_imagenes)

        self.page_senales.layout() or self.page_senales.setLayout(QVBoxLayout())
        self.page_senales.layout().addWidget(self.vista_senales)

        self.page_tabular.layout() or self.page_tabular.setLayout(QVBoxLayout())
        self.page_tabular.layout().addWidget(self.vista_tabular)

    # ---------------- metodos de navegacion ----------------

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
