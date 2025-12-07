from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QStackedWidget, QComboBox
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
        except Exception as e:
            print(f"❌ ERROR CRÍTICO AL CARGAR UI: {e}")

        # --- 2. INICIALIZAR VISTAS HIJAS ---
        self.vista_imagenes = ImagenesView(self)
        self.vista_senales = SenalesView(self) 
        self.vista_tabular = TabularView(self)

        # --- 3. CONEXIÓN MANUAL Y DIRECTA (INFALIBLE) ---
        print("\n--- 🔌 CONECTANDO WIDGETS POR NOMBRE EXACTO ---")
        
        def conectar(nombre_xml, atributo_vista, es_combo=False):
            # Buscamos el widget por su nombre exacto definido en el XML
            widget = self.findChild(QWidget, nombre_xml)
            
            if widget:
                # Asignamos el widget encontrado a la vista de imágenes
                setattr(self.vista_imagenes, atributo_vista, widget)
                print(f"   ✅ Conectado: {nombre_xml}")
                
                # SI ES COMBOBOX: LE QUITAMOS EL ESTILO PARA QUE SE VEA SI O SI
                if es_combo and isinstance(widget, QComboBox):
                    widget.setStyleSheet("") # Borra cualquier estilo corrupto del XML
                    widget.setMinimumHeight(25) # Fuerza altura mínima
                    widget.addItem("Cargando...") # Texto de prueba
            else:
                print(f"   ❌ ERROR FATAL: No se encontró '{nombre_xml}' en el UI.")

        # --- A. COMBOBOXES (Limpiamos estilo para evitar texto invisible) ---
        conectar("cb_filtro_tipo", "cb_filtro_tipo", es_combo=True)
        conectar("cb_umbral_tipo", "cb_umbral_tipo", es_combo=True)
        conectar("cb_morfologia", "cb_morfologia", es_combo=True)

        # --- B. RESTO DE CONTROLES ---
        conectar("btn_canny_bordes", "btn_canny_bordes")
        conectar("btn_invertir_bin", "btn_invertir_bin")
        
        conectar("sld_intensidad_filtro", "sld_intensidad_filtro")
        conectar("sld_umbral_manual", "sld_umbral_manual")
        conectar("sld_morfologia_it", "sld_morfologia_it")
        
        conectar("label_valor_filtro", "lbl_valor_filtro")
        conectar("btn_exportar_procesada", "btn_exportar_procesada")
        
        print("-----------------------------------------------\n")

        # --- 4. REFERENCIAS DE NAVEGACIÓN ---
        self.btn_ir_imagenes = self.findChild(QPushButton, "btn_ir_imagenes")
        self.btn_ir_senales = self.findChild(QPushButton, "btn_ir_senales")
        self.btn_ir_tabular = self.findChild(QPushButton, "btn_ir_tabular")
        self.btn_ir_perfil = self.findChild(QPushButton, "btn_ir_perfil")
        self.btn_ir_logout = self.findChild(QPushButton, "btn_ir_logout")

        # --- 5. REFERENCIAS AL STACKED WIDGET Y SUS PÁGINAS ---
        self.stacked = self.findChild(QStackedWidget, "stacked_contenido")
        
        self.page_home = self.findChild(QWidget, "page_home")
        self.page_imagenes = self.findChild(QWidget, "page_imagenes")
        self.page_senales = self.findChild(QWidget, "page_senales")
        self.page_tabular = self.findChild(QWidget, "tabular")
        self.page_perfil = self.findChild(QWidget, "perfil")

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