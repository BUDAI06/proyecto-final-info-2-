from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QByteArray # Necesitas QByteArray para cargar datos binarios
import numpy as np

class SenalesView:
    
    def __init__(self, main_window):
        # La ventana principal que contiene todos los widgets
        self.ui = main_window 

        # --- Búsqueda y Enlace de Controles ---
        # Asegúrate de que los nombres de los objetos (el segundo argumento) 
        # coincidan EXACTAMENTE con los nombres en Qt Designer.
        self.btn_cargar = self.ui.findChild(QPushButton, "btn_cargar_senal")
        self.btn_fft = self.ui.findChild(QPushButton, "btn_fft")
        self.btn_filtrar = self.ui.findChild(QPushButton, "btn_filtrar")

        self.cb_canal = self.ui.findChild(QComboBox, "cb_canal")

        # Nombres de las etiquetas (Basado en tu diseño: lbl_senal_cruda y lbl_fft)
        self.lbl_senal = self.ui.findChild(QLabel, "lbl_senal_cruda")
        self.lbl_fft = self.ui.findChild(QLabel, "lbl_fft")

        self.lbl_info = self.ui.findChild(QLabel, "lbl_info_senal")


    def mostrar_senal(self, img_bytes):
        """Muestra la gráfica de tiempo. Espera datos de imagen PNG en bytes."""
        self._mostrar_imagen_desde_bytes(img_bytes, self.lbl_senal)

    def mostrar_fft(self, img_bytes):
        """Muestra la gráfica FFT. Espera datos de imagen PNG en bytes."""
        self._mostrar_imagen_desde_bytes(img_bytes, self.lbl_fft)

    def _mostrar_imagen_desde_bytes(self, img_bytes, label):
        """
        Carga la imagen PNG (recibida como bytes) usando QPixmap.loadFromData()
        y la escala para ajustarse al QLabel.
        """
        if label is None or not img_bytes:
            return
            
        pixmap = QPixmap()
        
        # 🚨 CORRECCIÓN CLAVE: Cargar desde bytes PNG
        # El Modelo devuelve bytes PNG, no un array de numpy
        if pixmap.loadFromData(QByteArray(img_bytes), "PNG"):
            
            # Escalar el QPixmap para que se ajuste al tamaño del QLabel
            pixmap_escalado = pixmap.scaled(
                label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            label.setPixmap(pixmap_escalado)
        else:
            print("Error al cargar los datos de imagen PNG.")

    def mostrar_info(self, texto):
        """Muestra texto en la etiqueta de información."""
        if self.lbl_info:
            self.lbl_info.setText(texto)
