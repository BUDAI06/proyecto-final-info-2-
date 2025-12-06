from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QComboBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np

class SenalesView:
    def __init__(self, main_window):
        self.ui = main_window

        self.btn_cargar = self.ui.findChild(QPushButton, "btn_cargar_senal")
        self.btn_fft = self.ui.findChild(QPushButton, "btn_fft")
        self.btn_filtrar = self.ui.findChild(QPushButton, "btn_filtrar")

        self.cb_canal = self.ui.findChild(QComboBox, "cb_canal")

        self.lbl_senal = self.ui.findChild(QLabel, "lbl_senal_cruda")
        self.lbl_fft = self.ui.findChild(QLabel, "lbl_fft")

        self.lbl_info = self.ui.findChild(QLabel, "lbl_info_senal")

    def mostrar_senal(self, imagen_np):
        self._mostrar_imagen(imagen_np, self.lbl_senal)

    def mostrar_fft(self, imagen_np):
        self._mostrar_imagen(imagen_np, self.lbl_fft)

    def _mostrar_imagen(self, img_np, label):
        if label is None:
            return
            
        h, w, c = img_np.shape
        bytes_line = 3 * w
        qimg = QImage(img_np.data, w, h, bytes_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pix)

    def mostrar_info(self, texto):
        if self.lbl_info:
            self.lbl_info.setText(texto)