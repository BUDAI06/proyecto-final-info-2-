from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QStackedWidget, QComboBox, QSlider, QLabel
from PyQt5.uic import loadUi
from view.imagenes_view import ImagenesView
from view.senales_view import SenalesView
from view.tabular_view import TabularView
import os

class MainAppView(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- 1. CARGA DE UI ---
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_ui = os.path.join(ruta_actual, "..", "ui", "main_app_window.ui")
        
        try:
            loadUi(ruta_ui, self)
        except Exception as e:
            print(f"❌ ERROR CRÍTICO AL CARGAR UI: {e}")

        # --- 2. INICIALIZAR VISTAS ---
        self.vista_imagenes = ImagenesView(self)
        self.vista_senales = SenalesView(self) 
        self.vista_tabular = TabularView(self)

        # --- 3. INYECCIÓN INTELIGENTE (SOLUCIÓN FINAL) ---
        print("\n--- 🧠 REALIZANDO CONEXIÓN INTELIGENTE DE WIDGETS ---")
        
        # Obtenemos TODOS los ComboBoxes de la aplicación
        todos_combos = self.findChildren(QComboBox)
        
        # Variables temporales para encontrar los dueños correctos
        combo_filtro = None
        combo_umbral = None
        combo_morfo = None
        
        for cb in todos_combos:
            nombre = cb.objectName().lower().strip() # Convertimos a minúsculas y quitamos espacios
            
            # DIAGNÓSTICO: Ver qué estamos escaneando
            print(f"   🔎 Analizando: '{nombre}'")
            
            # FILTRADO INTELIGENTE
            if "canal" in nombre:
                print("      ⛔ Ignorando (Pertenece a Señales)")
                continue # Saltamos este ciclo
            
            if "filtro" in nombre:
                combo_filtro = cb
                print("      ✅ ES EL FILTRO!")
            
            elif "umbral" in nombre:
                combo_umbral = cb
                print("      ✅ ES EL UMBRAL!")
            
            elif "morf" in nombre:
                combo_morfo = cb
                print("      ✅ ES LA MORFOLOGÍA!")

        # ASIGNACIÓN FINAL A LA VISTA DE IMÁGENES
        self.vista_imagenes.cb_filtro_tipo = combo_filtro
        self.vista_imagenes.cb_umbral_tipo = combo_umbral
        self.vista_imagenes.cb_morfologia = combo_morfo

        # --- 4. INYECCIÓN DEL RESTO DE CONTROLES (Estos ya funcionaban bien) ---
        def inyectar(nombre_ui, nombre_en_vista, tipo):
            for w in self.findChildren(QWidget):
                if w.objectName() == nombre_ui:
                    setattr(self.vista_imagenes, nombre_en_vista, w)
                    return
        
        # Mapeo manual seguro para el resto
        inyectar("btn_canny_bordes", "btn_canny_bordes", QPushButton)
        inyectar("btn_invertir_bin", "btn_invertir_bin", QPushButton)
        
        inyectar("sld_intensidad_filtro", "sld_intensidad_filtro", QSlider)
        inyectar("sld_umbral_manual", "sld_umbral_manual", QSlider)
        inyectar("sld_morfologia_it", "sld_morfologia_it", QSlider)
        
        inyectar("label_valor_filtro", "lbl_valor_filtro", QLabel) # Nombre corregido
        inyectar("btn_exportar_procesada", "btn_exportar_procesada", QPushButton)

        print("-------------------------------------------------------\n")

        # --- 5. REFERENCIAS DE NAVEGACIÓN ---
        self.btn_ir_imagenes = self.findChild(QPushButton, "btn_ir_imagenes")
        self.btn_ir_senales = self.findChild(QPushButton, "btn_ir_senales")
        self.btn_ir_tabular = self.findChild(QPushButton, "btn_ir_tabular")
        self.btn_ir_perfil = self.findChild(QPushButton, "btn_ir_perfil")
        self.btn_ir_logout = self.findChild(QPushButton, "btn_ir_logout")
        self.stacked = self.findChild(QStackedWidget, "stacked_contenido")
        
        self.page_home = self.findChild(QWidget, "page_home")
        self.page_imagenes = self.findChild(QWidget, "page_imagenes")
        self.page_senales = self.findChild(QWidget, "page_senales")
        self.page_tabular = self.findChild(QWidget, "tabular")
        self.page_perfil = self.findChild(QWidget, "perfil")
        
    # --- MÉTODOS DE NAVEGACIÓN ---
    def mostrar_home(self):
        if self.page_home: self.stacked.setCurrentWidget(self.page_home)
    def mostrar_imagenes(self):
        if self.page_imagenes: self.stacked.setCurrentWidget(self.page_imagenes)
    def mostrar_senales(self):
        if self.page_senales: self.stacked.setCurrentWidget(self.page_senales)
    def mostrar_tabular(self):
        if self.page_tabular: self.stacked.setCurrentWidget(self.page_tabular)
    def mostrar_perfil(self):
        if self.page_perfil: self.stacked.setCurrentWidget(self.page_perfil)