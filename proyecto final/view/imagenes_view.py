from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QSlider, QStackedWidget, QComboBox
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class ImagenesView:
    def __init__(self, main_window):
        self.ui = main_window

        # --- 1. VARIABLES INYECTADAS (Desde main_view o búsqueda directa) ---
        self.cb_filtro_tipo = None
        self.cb_umbral_tipo = None
        self.cb_morfologia = None
        
        self.btn_canny_bordes = None
        self.btn_invertir_bin = None
        
        self.sld_intensidad_filtro = None
        self.sld_umbral_manual = None
        self.sld_morfologia_it = None
        
        self.lbl_valor_filtro = None 
        self.btn_exportar_procesada = None

        # --- 2. BÚSQUEDA Y REGISTRO FORMAL DE WIDGETS ---
        # Definimos una función de búsqueda para centralizar el registro
        def encontrar(tipo, nombre):
            return self.ui.findChild(tipo, nombre)

        # Registro de Contenedores
        self.stacked_procesamiento = encontrar(QStackedWidget, "stacked_procesamiento")
        self.cb_filtro_tipo = encontrar(QComboBox, "cb_filtro_tipo")
        self.cb_umbral_tipo = encontrar(QComboBox, "cb_umbral_tipo")
        self.cb_morfologia = encontrar(QComboBox, "cb_morfologia")
        # Registro de Botones
        self.btn_cargar_imagen = encontrar(QPushButton, "btn_cargar_imagen")
        self.btn_guardardatos = encontrar(QPushButton, "btn_guardardatos")
        self.btn_reset_opencv = encontrar(QPushButton, "btn_reset_opencv")
        self.btn_canny_bordes = encontrar(QPushButton, "btn_canny_bordes")
        self.btn_invertir_bin = encontrar(QPushButton, "btn_invertir_bin")
        self.btn_exportar_procesada = encontrar(QPushButton, "btn_exportar_procesada")
        # --- CORRECCIÓN DE RAÍZ: Registro de Labels de Visualización ---
        # Labels DICOM
        self.lbl_axial = encontrar(QLabel, "lbl_axial")
        self.lbl_coronal = encontrar(QLabel, "lbl_coronal")
        self.lbl_sagital = encontrar(QLabel, "lbl_sagital")

        # Labels PNG/JPG (El punto de falla anterior)
        # Se registran formalmente aquí para que el controlador tenga acceso
        self.lbl_img_original = encontrar(QLabel, "lbl_img_original")
        self.lbl_img_procesada = encontrar(QLabel, "lbl_img_procesada")
        
        # Registro de Sliders
        self.sld_axial = encontrar(QSlider, "sld_axial")
        self.sld_coronal = encontrar(QSlider, "sld_coronal")
        self.sld_sagital = encontrar(QSlider, "sld_sagital")
        self.sld_intensidad_filtro = encontrar(QSlider, "sld_intensidad_filtro")
        self.sld_umbral_manual = encontrar(QSlider, "sld_umbral_manual")
        self.sld_morfologia_it = encontrar(QSlider, "sld_morfologia_it")
        # Registro de Información
        self.lbl_metadatos = encontrar(QLabel, "lbl_metadatos")
        self.lbl_guardardatos = encontrar(QLabel, "lbl_guardardatos") 
        self.lbl_valor_filtro = encontrar(QLabel, "label_valor_filtro")
        # Configuración inicial de Sliders
        if self.sld_axial: self.sld_axial.setOrientation(Qt.Horizontal)
        if self.sld_coronal: self.sld_coronal.setOrientation(Qt.Horizontal)
        if self.sld_sagital: self.sld_sagital.setOrientation(Qt.Horizontal)

    # --- ALIAS DE COMPATIBILIDAD (Para el controlador) ---
    @property
    def btn_canny(self): return self.btn_canny_bordes
    @property
    def btn_invertir(self): return self.btn_invertir_bin
    @property
    def sld_intensidad(self): return self.sld_intensidad_filtro
    @property
    def sld_umbral(self): return self.sld_umbral_manual
    @property
    def sld_morfologia(self): return self.sld_morfologia_it
    @property
    def btn_exportar(self): return self.btn_exportar_procesada
    @property
    def lbl_valor_filtro_ref(self): return self.lbl_valor_filtro

    # --- MÉTODOS DE VISUALIZACIÓN ---
    def mostrar_metadatos(self, metadata: dict):
        if self.lbl_metadatos:
            texto = "".join([f"<b>{k}:</b> {v}<br>" for k, v in metadata.items()])
            self.lbl_metadatos.setText(texto)
        
        if self.lbl_guardardatos:
            self.lbl_guardardatos.setText("")

    def mostrar_mensaje_guardado(self, mensaje):
        if self.lbl_guardardatos:
            self.lbl_guardardatos.setText(mensaje)

    def mostrar_slice(self, data: np.ndarray, label: QLabel):
        """Convierte datos numpy a QPixmap y los renderiza en el label correspondiente."""
        # Se mantiene la verificación para depuración, pero la solución de raíz es el __init__
        if label is None:
            return 

        # Normalización y procesamiento de imagen
        min_val, max_val = np.min(data), np.max(data)
        if max_val != min_val:
            norm = ((data - min_val) / (max_val - min_val)) * 255
        else:
            norm = data

        img = norm.astype(np.uint8)
        img = np.ascontiguousarray(img)

        # Manejo de formatos (Grayscale vs RGB)
        h, w = img.shape[:2]
        if len(img.shape) == 2: # Monocromática
            qimg = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
        else: # Color (RGB/BGR)
            qimg = QImage(img.data, w, h, w * 3, QImage.Format_RGB888).rgbSwapped()

        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pix)