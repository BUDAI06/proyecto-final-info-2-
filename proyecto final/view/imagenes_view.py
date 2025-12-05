from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QSlider
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class ImagenesView(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("ui/imagenes.ui", self)   # ESTE archivo lo crearás pronto

        # Referencias UI
        self.btn_cargar_imagen = self.findChild(QPushButton, "btn_cargar_imagen")

        self.lbl_axial = self.findChild(QLabel, "lbl_axial")
        self.lbl_coronal = self.findChild(QLabel, "lbl_coronal")
        self.lbl_sagital = self.findChild(QLabel, "lbl_sagital")

        self.sld_axial = self.findChild(QSlider, "sld_axial")
        self.sld_coronal = self.findChild(QSlider, "sld_coronal")
        self.sld_sagital = self.findChild(QSlider, "sld_sagital")

        self.lbl_metadatos = self.findChild(QLabel, "lbl_metadatos")

        # slider orientation
        self.sld_axial.setOrientation(Qt.Horizontal)
        self.sld_coronal.setOrientation(Qt.Horizontal)
        self.sld_sagital.setOrientation(Qt.Horizontal)

    # --- MÉTODOS PARA ACTUALIZAR LA VISTA ---

    def mostrar_metadatos(self, metadata: dict):
        texto = ""
        for clave, valor in metadata.items():
            texto += f"{clave}: {valor}\n"
        self.lbl_metadatos.setText(texto)

    def mostrar_slice(self, data: np.ndarray, label: QLabel):
        """Convierte un array HU a imagen y lo pone en un QLabel."""
        min_hu, max_hu = -1000, 400

        clip = np.clip(data, min_hu, max_hu)
        norm = ((clip - min_hu) / (max_hu - min_hu)) * 255
        img = norm.astype(np.uint8)

        h, w = img.shape
        qimg = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
        pix = QPixmap.fromImage(qimg)

        pix = pix.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pix)
