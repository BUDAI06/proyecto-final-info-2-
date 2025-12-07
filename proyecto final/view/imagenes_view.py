from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QSlider, QStackedWidget
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
import os

class ImagenesView:
    def __init__(self, main_window):
        self.ui = main_window

        # --- 1. VARIABLES INYECTADAS (Se llenan desde main_view) ---
        self.cb_filtro_tipo = None
        self.cb_umbral_tipo = None
        self.cb_morfologia = None
        
        self.btn_canny_bordes = None
        self.btn_invertir_bin = None
        
        self.sld_intensidad_filtro = None
        self.sld_umbral_manual = None
        self.sld_morfologia_it = None
        
        # Esta es la variable clave que fallaba antes:
        self.lbl_valor_filtro = None 
        self.btn_exportar_procesada = None

        # --- 2. BÚSQUEDA DE LO QUE NO FALLA ---
        def encontrar(tipo, nombre):
            return self.ui.findChild(tipo, nombre)

        self.stacked_procesamiento = encontrar(QStackedWidget, "stacked_procesamiento")
        self.btn_cargar_imagen = encontrar(QPushButton, "btn_cargar_imagen")
        self.btn_guardardatos = encontrar(QPushButton, "btn_guardardatos")
        self.btn_reset_opencv = encontrar(QPushButton, "btn_reset_opencv")

        self.lbl_axial = self.ui.findChild(QLabel, "lbl_axial")
        self.lbl_coronal = self.ui.findChild(QLabel, "lbl_coronal")
        self.lbl_sagital = self.ui.findChild(QLabel, "lbl_sagital")

        self.sld_axial = self.ui.findChild(QSlider, "sld_axial")
        self.sld_coronal = self.ui.findChild(QSlider, "sld_coronal")
        self.sld_sagital = self.ui.findChild(QSlider, "sld_sagital")

        self.lbl_metadatos = self.ui.findChild(QLabel, "lbl_metadatos")
        self.lbl_guardardatos = self.ui.findChild(QLabel, "lbl_guardardatos") 

        # Configuración básica
        if self.sld_axial: self.sld_axial.setOrientation(Qt.Horizontal)
        if self.sld_coronal: self.sld_coronal.setOrientation(Qt.Horizontal)
        if self.sld_sagital: self.sld_sagital.setOrientation(Qt.Horizontal)

    # --- ALIAS (Compatibilidad con nombres del controlador) ---
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
    
    # IMPORTANTE: El controlador busca 'lbl_valor_filtro_ref' en un método auxiliar
    @property
    def lbl_valor_filtro_ref(self): return self.lbl_valor_filtro

    # --- MÉTODOS DE VISUALIZACIÓN ---
    def mostrar_metadatos(self, metadata: dict):
        if self.lbl_metadatos:
            texto = ""
            for clave, valor in metadata.items():
                texto += f"{clave}: {valor}\n"
            self.lbl_metadatos.setText(texto)
        
        if self.lbl_guardardatos:
            self.lbl_guardardatos.setText("")


    def mostrar_mensaje_guardado(self, mensaje):
        """Muestra un mensaje de confirmación de guardado en lbl_guardardatos."""
        if self.lbl_guardardatos:
            self.lbl_guardardatos.setText(mensaje)


    def mostrar_slice(self, data: np.ndarray, label: QLabel):
        """Convierte un array HU a imagen y lo pone en un QLabel."""
        if label is None:
            return print("label de metadatos no encontrada") 

        min_val = np.min(data)
        max_val = np.max(data)

        clip = data
        
        # Evitamos división por cero si min_val y max_val fueran iguales
        if max_val != min_val:
            norm = ((clip - min_val) / (max_val - min_val)) * 255
        else:
            norm = clip

        img = norm.astype(np.uint8)

        
        img = np.ascontiguousarray(img)

        h, w = img.shape
        # bytesPerLine es importante para evitar deformaciones en algunas imágenes
        bytesPerLine = w 
        qimg = QImage(img.data, w, h, bytesPerLine, QImage.Format_Grayscale8)
        pix = QPixmap.fromImage(qimg)

        # Usamos el tamaño del label actual para escalar
        pix = pix.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pix)