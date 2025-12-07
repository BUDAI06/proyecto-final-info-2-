from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QComboBox
from model.procesamiento_imagenes_model import ProcesadorImagenesMedicasModelo
import os
import numpy as np
import pandas as pd
from datetime import datetime
import cv2

CARPETA_EXPORTACION = "datos_exportados"

class ImagenesController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorImagenesMedicasModelo()

        # --- Eventos para imágenes médicas ---
        if self.vista.btn_cargar_imagen:
            self.vista.btn_cargar_imagen.clicked.connect(self.cargar_archivo)

        if self.vista.btn_guardardatos:
            self.vista.btn_guardardatos.clicked.connect(self.guardar_datos_csv)

        if self.vista.sld_axial:
            self.vista.sld_axial.valueChanged.connect(self.actualizar_cortes)

        if self.vista.sld_coronal:
            self.vista.sld_coronal.valueChanged.connect(self.actualizar_cortes)

        if self.vista.sld_sagital:
            self.vista.sld_sagital.valueChanged.connect(self.actualizar_cortes)

        # --- Inicialización OpenCV ---
        self.inicializar_controles_opencv()

    # ---------------------------------------------------------
    #   🔧 Inicialización controles OpenCV
    # ---------------------------------------------------------
    def inicializar_controles_opencv(self):
        # FILTROS
        if self.vista.cb_filtro_tipo:
            self.vista.cb_filtro_tipo.clear()
            self.vista.cb_filtro_tipo.addItems([
                "Ninguno",
                "Desenfoque Gausiano",
                "Median Blur",
                "Bilateral"
            ])
            self.vista.cb_filtro_tipo.currentIndexChanged.connect(self.aplicar_procesamiento)

        # UMBRAL
        if self.vista.cb_umbral_tipo:
            self.vista.cb_umbral_tipo.clear()
            self.vista.cb_umbral_tipo.addItems([
                "Ninguno",
                "Binario Simple",
                "Binario Invertido",
                "Otsu",
                "Adaptativo"
            ])
            self.vista.cb_umbral_tipo.currentIndexChanged.connect(self.aplicar_procesamiento)

        # MORFOLOGÍA
        if self.vista.cb_morfologia:
            self.vista.cb_morfologia.clear()
            self.vista.cb_morfologia.addItems([
                "Ninguna",
                "Erosión",
                "Dilatación",
                "Apertura",
                "Cierre"
            ])
            self.vista.cb_morfologia.currentIndexChanged.connect(self.aplicar_procesamiento)

        # SLIDERS
        if self.vista.sld_intensidad:
            self.vista.sld_intensidad.setRange(1, 20)
            self.vista.sld_intensidad.setValue(5)
            self.vista.sld_intensidad.valueChanged.connect(self._on_intensidad_changed)
            self.vista.sld_intensidad.sliderReleased.connect(self.aplicar_procesamiento)

        if self.vista.sld_umbral:
            self.vista.sld_umbral.setRange(0, 255)
            self.vista.sld_umbral.setValue(127)
            self.vista.sld_umbral.sliderReleased.connect(self.aplicar_procesamiento)

        if self.vista.sld_morfologia:
            self.vista.sld_morfologia.setRange(1, 10)
            self.vista.sld_morfologia.setValue(1)
            self.vista.sld_morfologia.sliderReleased.connect(self.aplicar_procesamiento)

        # BOTONES
        if self.vista.btn_reset_opencv:
            self.vista.btn_reset_opencv.clicked.connect(self.reset_filtros)

        if self.vista.btn_canny:
            self.vista.btn_canny.clicked.connect(self.detectar_bordes)

        if self.vista.btn_exportar:
            self.vista.btn_exportar.clicked.connect(self.exportar_imagen)
            
        if self.vista.btn_invertir:
            self.vista.btn_invertir.clicked.connect(self.aplicar_procesamiento)

    # ---------------------------------------------------------
    def _on_intensidad_changed(self, val):
        # Asegurar impar para filtros
        if val % 2 == 0: val += 1
        if self.vista.lbl_valor_filtro:
            self.vista.lbl_valor_filtro.setText(str(val))

    # ---------------------------------------------------------
    #   📂 Cargar archivo o carpeta
    # ---------------------------------------------------------
    def cargar_archivo(self):
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
            ruta, _ = QFileDialog.getOpenFileName(
                None, "Cargar", "",
                "Médicas (*.dcm *.nii *.nii.gz);;Estándar (*.jpg *.png *.jpeg);;Todos (*.*)"
            )
        elif msg.clickedButton() == btn_carpeta:
            ruta = QFileDialog.getExistingDirectory(None, "Seleccionar Carpeta")

        if not ruta:
            return

        if self.modelo.cargar_y_procesar(ruta):
            if self.modelo.tipo_archivo == "OPENCV":
                if self.vista.stacked_procesamiento:
                    self.vista.stacked_procesamiento.setCurrentIndex(1)
                self.actualizar_vista_opencv()
            else:
                if self.vista.stacked_procesamiento:
                    self.vista.stacked_procesamiento.setCurrentIndex(0)
                z, y, x = self.modelo.shape
                if self.vista.sld_axial: self.vista.sld_axial.setMaximum(z - 1)
                if self.vista.sld_coronal: self.vista.sld_coronal.setMaximum(y - 1)
                if self.vista.sld_sagital: self.vista.sld_sagital.setMaximum(x - 1)
                self.actualizar_cortes()

            self.vista.mostrar_metadatos(self.modelo.metadata)

    # ---------------------------------------------------------
    def aplicar_procesamiento(self):
        if self.modelo.img_original is None:
            return

        img = self.modelo.img_original.copy()
        
        # 1. Recuperar valores UI
        filtro = self.vista.cb_filtro_tipo.currentText() if self.vista.cb_filtro_tipo else "Ninguno"
        k_size = self.vista.sld_intensidad.value() if self.vista.sld_intensidad else 3
        if k_size % 2 == 0: k_size += 1 # Asegurar impar

        umbral_tipo = self.vista.cb_umbral_tipo.currentText() if self.vista.cb_umbral_tipo else "Ninguno"
        thresh_val = self.vista.sld_umbral.value() if self.vista.sld_umbral else 127
        
        morfo = self.vista.cb_morfologia.currentText() if self.vista.cb_morfologia else "Ninguna"
        iteraciones = self.vista.sld_morfologia.value() if self.vista.sld_morfologia else 1

        # 2. Aplicar lógica (Cascada de procesamiento)
        
        # A. FILTROS
        if filtro == "Desenfoque Gausiano":
            img = cv2.GaussianBlur(img, (k_size, k_size), 0)
        elif filtro == "Median Blur":
            img = cv2.medianBlur(img, k_size)
        elif filtro == "Bilateral":
            img = cv2.bilateralFilter(img, 9, 75, 75)

        # B. UMBRAL (Requiere conversión a gris si es color)
        if umbral_tipo != "Ninguno":
            if len(img.shape) == 3:
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                img_gray = img
            
            if umbral_tipo == "Binario Simple":
                _, img = cv2.threshold(img_gray, thresh_val, 255, cv2.THRESH_BINARY)
            elif umbral_tipo == "Binario Invertido":
                _, img = cv2.threshold(img_gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
            elif umbral_tipo == "Otsu":
                _, img = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif umbral_tipo == "Adaptativo":
                img = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # C. MORFOLOGÍA
        if morfo != "Ninguna":
            kernel = np.ones((3,3), np.uint8)
            if morfo == "Erosión":
                img = cv2.erode(img, kernel, iterations=iteraciones)
            elif morfo == "Dilatación":
                img = cv2.dilate(img, kernel, iterations=iteraciones)
            elif morfo == "Apertura":
                img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
            elif morfo == "Cierre":
                img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

        # 3. Guardar en modelo y mostrar
        self.modelo.img_procesada = img
        self.actualizar_vista_opencv()

    # ---------------------------------------------------------
    def detectar_bordes(self):
        if self.modelo.img_original is None: return
        try:
            # Canny usa dos umbrales, usamos el slider para controlar uno
            t_lower = 50
            t_upper = 150
            if self.vista.sld_umbral:
                t_lower = self.vista.sld_umbral.value()
                t_upper = t_lower * 2
            
            img_gray = cv2.cvtColor(self.modelo.img_original, cv2.COLOR_BGR2GRAY) if len(self.modelo.img_original.shape) == 3 else self.modelo.img_original
            procesada = cv2.Canny(img_gray, t_lower, t_upper)
            
            self.modelo.img_procesada = procesada
            self.actualizar_vista_opencv()
        except Exception as e:
            print(f"Error Canny: {e}")

    # ---------------------------------------------------------
    def reset_filtros(self):
        if self.modelo.img_original is not None:
            self.modelo.img_procesada = self.modelo.img_original.copy()
            
        if self.vista.cb_filtro_tipo: self.vista.cb_filtro_tipo.setCurrentIndex(0)
        if self.vista.cb_umbral_tipo: self.vista.cb_umbral_tipo.setCurrentIndex(0)
        if self.vista.cb_morfologia: self.vista.cb_morfologia.setCurrentIndex(0)
        if self.vista.sld_intensidad: self.vista.sld_intensidad.setValue(5)
        
        self.actualizar_vista_opencv()

    # ---------------------------------------------------------
    def actualizar_vista_opencv(self):
        if self.modelo.img_original is not None:
            self.vista.mostrar_slice(self.modelo.img_original, self.vista.lbl_img_original)
            self.vista.mostrar_slice(self.modelo.img_procesada, self.vista.lbl_img_procesada)

    # ---------------------------------------------------------
    def exportar_imagen(self):
        if self.modelo.img_procesada is None:
            QMessageBox.warning(None, "Exportar", "No hay imagen procesada para exportar.")
            return
        
        ruta, _ = QFileDialog.getSaveFileName(None, "Exportar imagen", "imagen_procesada.png", "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if not ruta:
            return

        try:
            # Usamos cv2 directamente aquí para garantizar escritura correcta
            cv2.imwrite(ruta, self.modelo.img_procesada)
            QMessageBox.information(None, "Exportar", f"Imagen exportada correctamente en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(None, "Exportar", f"Error exportando imagen: {e}")

    # ---------------------------------------------------------
    def guardar_datos_csv(self):
        metadata = self.modelo.obtener_metadata_para_csv()
        if metadata is None:
            self.vista.mostrar_mensaje_guardado("Error: No hay datos para guardar.")
            return

        nombre_archivo, ok = QInputDialog.getText(None, 'Guardar', 'Ingrese nombre del archivo:')
        if not ok or not nombre_archivo:
            return

        df = pd.DataFrame(metadata.items(), columns=['Etiqueta', 'Valor'])
        if not os.path.exists(CARPETA_EXPORTACION):
            os.makedirs(CARPETA_EXPORTACION)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in nombre_archivo if c.isalnum() or c in (' ', '_')).rstrip()
        final_filename = f"{safe_name}_{timestamp}.csv"
        ruta_guardado = os.path.join(CARPETA_EXPORTACION, final_filename)

        try:
            df.to_csv(ruta_guardado, index=False)
            self.vista.mostrar_mensaje_guardado(f"Datos guardados: {final_filename}")
        except Exception as e:
            self.vista.mostrar_mensaje_guardado(f"Error: {e}")

    # ---------------------------------------------------------
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
            sagital = np.rot90(sagital, k=3)

        self.vista.mostrar_slice(axial, self.vista.lbl_axial)
        self.vista.mostrar_slice(coronal, self.vista.lbl_coronal)
        self.vista.mostrar_slice(sagital, self.vista.lbl_sagital)