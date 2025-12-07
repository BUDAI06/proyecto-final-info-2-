# controlador/imagenes_controller.py
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from model.procesamiento_imagenes_model import ProcesadorImagenesMedicasModelo
import os
import numpy as np
import pandas as pd
from datetime import datetime

# Definir la carpeta de destino relativa al directorio de ejecución
CARPETA_EXPORTACION = "datos_exportados"

class ImagenesController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorImagenesMedicasModelo()

        # Eventos
        self.vista.btn_cargar_imagen.clicked.connect(self.cargar_archivo)
        self.vista.btn_guardardatos.clicked.connect(self.guardar_datos_csv)
        self.vista.sld_axial.valueChanged.connect(self.actualizar_cortes)
        self.vista.sld_coronal.valueChanged.connect(self.actualizar_cortes)
        self.vista.sld_sagital.valueChanged.connect(self.actualizar_cortes)

    
    def cargar_archivo(self):
        
        # Primero, limpiar el mensaje de guardado anterior
        self.vista.mostrar_mensaje_guardado("")
        
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

    def guardar_datos_csv(self):
        metadata = self.modelo.obtener_metadata_para_csv()
        
        # Verificar si hay datos cargados
        if metadata is None:
            self.vista.mostrar_mensaje_guardado("Error: No hay datos de imagen cargados para guardar.")
            return

        # 1. Solicitar el nombre para el archivo
        nombre_archivo, ok = QInputDialog.getText(
            None, 
            'Guardar Metadatos del Estudio', 
            'Ingrese un nombre descriptivo para el archivo CSV:'
        )
        
        if not ok or not nombre_archivo:
            self.vista.mostrar_mensaje_guardado("Guardado cancelado por el usuario.")
            return

        # 2. Preparar el DataFrame y la ruta
        # Convertir el diccionario de metadatos a DataFrame (Etiqueta | Valor)
        df = pd.DataFrame(metadata.items(), columns=['Etiqueta', 'Valor'])

        # Crear la carpeta de exportación si no existe
        if not os.path.exists(CARPETA_EXPORTACION):
            os.makedirs(CARPETA_EXPORTACION)

        # Generar nombre de archivo único con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Limpiar el nombre para asegurar que sea válido para un archivo
        safe_name = "".join(c for c in nombre_archivo if c.isalnum() or c in (' ', '_')).rstrip()
        final_filename = f"{safe_name}_{timestamp}.csv"
        ruta_guardado = os.path.join(CARPETA_EXPORTACION, final_filename)

        # 3. Guardar el archivo CSV
        try:
            df.to_csv(ruta_guardado, index=False)
            
            # 4. Mostrar confirmación en lbl_guardardatos
            msg = (f"✅ Datos guardados con éxito:<br>"
                   f"Nombre: <b>{final_filename}</b><br>"
                   f"Ruta: <i>{CARPETA_EXPORTACION}{os.sep}</i>")
            self.vista.mostrar_mensaje_guardado(msg)
            
        except Exception as e:
            self.vista.mostrar_mensaje_guardado(f"❌ Error al guardar CSV: {e}")


    def actualizar_cortes(self):
        
        if self.modelo.volumen is None:
            return
        

        z = self.vista.sld_axial.value()
        y = self.vista.sld_coronal.value()
        x = self.vista.sld_sagital.value()

        axial = self.modelo.obtener_corte_axial(z)
        coronal = self.modelo.obtener_corte_coronal(y)
        sagital = self.modelo.obtener_corte_sagital(x)
        
        if sagital is not None:
            # Rotamos 270 grados (k=3) en sentido antihorario, que a menudo corrige la orientación sagital.
            sagital = np.rot90(sagital, k=3)

        self.vista.mostrar_slice(axial, self.vista.lbl_axial)
        self.vista.mostrar_slice(coronal, self.vista.lbl_coronal)
        self.vista.mostrar_slice(sagital, self.vista.lbl_sagital)