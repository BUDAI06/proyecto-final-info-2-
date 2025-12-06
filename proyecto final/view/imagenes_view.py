from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QSlider
# from PyQt5.uic import loadUi  <-- Ya no lo necesitas aquí
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
import os

class ImagenesView:
    def __init__(self, main_window):
        # Ya no necesitamos super().__init__() porque no heredamos de QWidget
        self.ui = main_window

        # --- REFERENCIAS A LA UI ---
        # BUSCAMOS LOS WIDGETS DENTRO DE LA VENTANA PRINCIPAL (self.ui)
        
        self.btn_cargar_imagen = self.ui.findChild(QPushButton, "btn_cargar_imagen")

        self.lbl_axial = self.ui.findChild(QLabel, "lbl_axial")
        self.lbl_coronal = self.ui.findChild(QLabel, "lbl_coronal")
        self.lbl_sagital = self.ui.findChild(QLabel, "lbl_sagital")

        self.sld_axial = self.ui.findChild(QSlider, "sld_axial")
        self.sld_coronal = self.ui.findChild(QSlider, "sld_coronal")
        self.sld_sagital = self.ui.findChild(QSlider, "sld_sagital")

        self.lbl_metadatos = self.ui.findChild(QLabel, "lbl_metadatos")

        # --- CONFIGURACIÓN INICIAL ---
        
        # Validación de seguridad: Solo configuramos si los encontramos
        if self.sld_axial:
            self.sld_axial.setOrientation(Qt.Horizontal)
        else:
            print("⚠️ CUIDADO: No se encontró 'sld_axial'. Revisa el objectName en Designer.")

        if self.sld_coronal:
            self.sld_coronal.setOrientation(Qt.Horizontal)
            
        if self.sld_sagital:
            self.sld_sagital.setOrientation(Qt.Horizontal)

    # --- MÉTODOS PARA ACTUALIZAR LA VISTA ---

    def mostrar_metadatos(self, metadata: dict):
        # Verificamos que la etiqueta exista antes de intentar escribir en ella
        if self.lbl_metadatos:
            texto = ""
            for clave, valor in metadata.items():
                texto += f"{clave}: {valor}\n"
            self.lbl_metadatos.setText(texto)

    def mostrar_slice(self, data: np.ndarray, label: QLabel):
        """Convierte un array HU a imagen y lo pone en un QLabel."""
        if label is None:
            return # Evitamos error si el label no se encontró

        min_hu, max_hu = -1000, 400

        clip = np.clip(data, min_hu, max_hu)
        # Evitamos división por cero si min_hu y max_hu fueran iguales
        if max_hu != min_hu:
            norm = ((clip - min_hu) / (max_hu - min_hu)) * 255
        else:
            norm = clip

        img = norm.astype(np.uint8)

        h, w = img.shape
        # bytesPerLine es importante para evitar deformaciones en algunas imágenes
        bytesPerLine = w 
        qimg = QImage(img.data, w, h, bytesPerLine, QImage.Format_Grayscale8)
        pix = QPixmap.fromImage(qimg)

        # Usamos el tamaño del label actual para escalar
        pix = pix.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pix)