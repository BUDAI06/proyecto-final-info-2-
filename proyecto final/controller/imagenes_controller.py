from PyQt5.QtWidgets import QFileDialog, QMessageBox
from model.procesamiento_imagenes_model import ProcesadorImagenesMedicasModelo
import os
import numpy as np
class ImagenesController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorImagenesMedicasModelo()

        # Eventos
        self.vista.btn_cargar_imagen.clicked.connect(self.cargar_archivo)
        self.vista.sld_axial.valueChanged.connect(self.actualizar_cortes)
        self.vista.sld_coronal.valueChanged.connect(self.actualizar_cortes)
        self.vista.sld_sagital.valueChanged.connect(self.actualizar_cortes)

    
    def cargar_archivo(self):
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("¿Qué tipo de recurso deseas cargar?")
        msg.setWindowTitle("Selección de recurso")
        
        btn_archivo = msg.addButton("Archivo Individual", QMessageBox.YesRole)
        btn_carpeta = msg.addButton("Carpeta (Serie DICOM)", QMessageBox.NoRole)
        msg.exec_()

        ruta = None

        if msg.clickedButton() == btn_archivo:
            # Opción A: Cargar archivo individual
            ruta, _ = QFileDialog.getOpenFileName(
                None,
                "Cargar archivo de imagen",
                "",
                "DICOM (*.dcm);;NIFTI (*.nii *.nii.gz);;Todos (*.*)"
            )
        elif msg.clickedButton() == btn_carpeta:
            # Opción B: Cargar carpeta (Serie DICOM)
            ruta = QFileDialog.getExistingDirectory(
                None,
                "Seleccionar Carpeta con Serie DICOM",
                os.path.expanduser("~")
            )

        if not ruta:
            return

        if self.modelo.cargar_y_procesar(ruta):
            # Actualizar sliders
            z, y, x = self.modelo.shape
            self.vista.sld_axial.setMaximum(z-1)
            self.vista.sld_coronal.setMaximum(y-1)
            self.vista.sld_sagital.setMaximum(x-1)

            # Mostrar metadata
            self.vista.mostrar_metadatos(self.modelo.metadata)

            # Mostrar cortes iniciales
            self.actualizar_cortes()

    def actualizar_cortes(self):
        z = self.vista.sld_axial.value()
        y = self.vista.sld_coronal.value()
        x = self.vista.sld_sagital.value()

        axial = self.modelo.obtener_corte_axial(z)
        coronal = self.modelo.obtener_corte_coronal(y)
        sagital = self.modelo.obtener_corte_sagital(x)
        
        if sagital is not None:
            sagital = np.rot90(sagital, k=1)

        self.vista.mostrar_slice(axial, self.vista.lbl_axial)
        self.vista.mostrar_slice(coronal, self.vista.lbl_coronal)
        self.vista.mostrar_slice(sagital, self.vista.lbl_sagital)