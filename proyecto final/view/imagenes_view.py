from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QSlider
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
import os

class ImagenesView:
    def __init__(self, main_window):
        self.ui = main_window

        # --- REFERENCIAS A LA UI ---
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
            print("CUIDADO: No se encontró 'sld_axial'. Revisa el objectName en Designer.")

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
            return print("label de metadatos no encontrada") # Evitamos error si el label no se encontró

        min_val = np.min(data)
        max_val = np.max(data)

        clip = data
        
        # Evitamos división por cero si min_val y max_val fueran iguales
        if max_val != min_val:
            norm = ((clip - min_val) / (max_val - min_val)) * 255
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