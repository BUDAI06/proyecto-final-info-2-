# Vista.py
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog 
from PyQt5.uic import loadUi
import numpy as np
# ... (código existente)

class LoginView(QMainWindow):
    """
    Clase que representa la interfaz de Login.
    Solo se encarga de cargar el diseño .ui y de mostrar/obtener datos.
    """
    def __init__(self):
        super().__init__()
        # Carga el diseño de la interfaz desde el archivo .ui
        loadUi('./ui_files/login_window.ui', self)
        
        # 1. Obtener referencias a los widgets clave (ASEGÚRATE DE USAR LOS NOMBRES CORRECTOS)
        # Reemplaza 'btn_login', 'txt_usuario', 'txt_password' con los nombres que diste en QtDesigner.
        self.btn_login = self.findChild(QtWidgets.QPushButton, 'btn_login') 
        self.txt_usuario = self.findChild(QtWidgets.QLineEdit, 'txt_usuario')
        self.txt_password = self.findChild(QtWidgets.QLineEdit, 'txt_password')
        
        # Configuración de seguridad visual
        self.txt_password.setEchoMode(QtWidgets.QLineEdit.Password)

    def obtener_credenciales(self):
        """Retorna las credenciales ingresadas por el usuario."""
        return self.txt_usuario.text(), self.txt_password.text()

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un cuadro de diálogo con información o error."""
        msg = QMessageBox()
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec_()

# Clase de Vista para la Aplicación Principal (se usará más adelante)
# Vista.py (Modificar la clase MainAppView)

# Necesitarás estas importaciones

# ... (código existente)

class MainAppView(QMainWindow):
    # ... (código __init__ existente y referencias a widgets de OpenCV)

    def __init__(self):
        super().__init__()
        loadUi('./ui_files/main_app_window.ui', self)
        
        # Referencias a widgets de Imágenes Médicas
        self.btn_cargar_dicom = self.findChild(QtWidgets.QPushButton, 'btn_cargar_dicom')
        self.lbl_axial = self.findChild(QtWidgets.QLabel, 'lbl_axial')
        self.lbl_coronal = self.findChild(QtWidgets.QLabel, 'lbl_coronal')
        self.lbl_sagital = self.findChild(QtWidgets.QLabel, 'lbl_sagital')
        self.lbl_metadata = self.findChild(QtWidgets.QLabel, 'lbl_metadata')
        self.sld_axial_slice = self.findChild(QtWidgets.QSlider, 'sld_axial_slice')
        self.sld_coronal_slice = self.findChild(QtWidgets.QSlider, 'sld_coronal_slice')
        self.sld_sagital_slice = self.findChild(QtWidgets.QSlider, 'sld_sagital_slice')
        
        # Configurar sliders inicialmente (vertical u horizontal, según diseño)
        self.sld_axial_slice.setOrientation(Qt.Horizontal) 
        # ... (configurar los otros dos)
        
    def configurar_sliders(self, z, y, x):
        """Ajusta el rango de los sliders según el tamaño del volumen."""
        self.sld_axial_slice.setMaximum(z - 1)
        self.sld_coronal_slice.setMaximum(y - 1)
        self.sld_sagital_slice.setMaximum(x - 1)
        
    def mostrar_metadata(self, metadata):
        """Muestra la información extraída en una etiqueta."""
        text = f"Paciente: {metadata['Paciente']}\n"
        text += f"ID Estudio: {metadata['ID_Estudio']}\n"
        # ... (añadir más metadatos relevantes)
        self.lbl_metadata.setText(text)

    def mostrar_imagen_hu(self, slice_data, label_widget):
        """
        Convierte un array de NumPy (slice en HU) a QPixmap para mostrarlo.
        Esto es crucial para visualizar los datos médicos.
        """
        # 1. Normalización para visualización (HU range to 0-255)
        # Esto es un paso básico de "Windowing". Se puede mejorar para rangos específicos (hueso, tejido).
        min_hu = -1000  # Aire / Agua
        max_hu = 400   # Tejido denso / Hueso
        
        # Limitar y escalar los valores: (datos - min) / (max - min) * 255
        slice_clipped = np.clip(slice_data, min_hu, max_hu)
        slice_normalized = ((slice_clipped - min_hu) / (max_hu - min_hu)) * 255
        
        # 2. Convertir a imagen de 8 bits (uint8)
        img_8bit = slice_normalized.astype(np.uint8)
        
        # 3. Convertir a QImage y QPixmap
        h, w = img_8bit.shape
        bytes_per_line = w
        q_img = QImage(img_8bit.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        
        # 4. Mostrar en el QLabel
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(label_widget.size(), 
                                     Qt.KeepAspectRatio, 
                                     Qt.SmoothTransformation)
        label_widget.setPixmap(scaled_pixmap)