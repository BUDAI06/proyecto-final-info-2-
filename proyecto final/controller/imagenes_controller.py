from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
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

        # Eventos
        if self.vista.btn_cargar_imagen:
            self.vista.btn_cargar_imagen.clicked.connect(self.cargar_archivo)
        if self.vista.btn_guardardatos:
            self.vista.btn_guardardatos.clicked.connect(self.guardar_datos_csv)
        
        # Sliders DICOM
        for sld in [self.vista.sld_axial, self.vista.sld_coronal, self.vista.sld_sagital]:
            if sld: sld.valueChanged.connect(self.actualizar_cortes)

        # INICIALIZACIÓN DE COMBOS
        self.inicializar_controles_opencv()

    def inicializar_controles_opencv(self):
        print("\n--- 🎮 INICIALIZANDO CONTROLADOR OPENCV ---")
        
        # 1. FILTROS
        if self.vista.cb_filtro_tipo:
            print("   ✅ Configurando Filtros...")
            self.vista.cb_filtro_tipo.clear() # Borra el "Cargando..."
            self.vista.cb_filtro_tipo.addItems(["Ninguno", "Gaussian Blur", "Median Blur", "Bilateral"])
            self.vista.cb_filtro_tipo.currentIndexChanged.connect(self.aplicar_procesamiento)
        else:
            print("   ❌ ERROR: No se encontró cb_filtro_tipo en la vista")

        # 2. UMBRAL
        if self.vista.cb_umbral_tipo:
            print("   ✅ Configurando Umbral...")
            self.vista.cb_umbral_tipo.clear()
            self.vista.cb_umbral_tipo.addItems(["Ninguno", "Binario Simple", "Binario Invertido", "Otsu", "Adaptativo"])
            self.vista.cb_umbral_tipo.currentIndexChanged.connect(self.aplicar_procesamiento)

        # 3. MORFOLOGÍA
        if self.vista.cb_morfologia:
            print("   ✅ Configurando Morfología...")
            self.vista.cb_morfologia.clear()
            self.vista.cb_morfologia.addItems(["Ninguna", "Erosion", "Dilatacion", "Apertura", "Cierre"])
            self.vista.cb_morfologia.currentIndexChanged.connect(self.aplicar_procesamiento)

        # Sliders y Botones
        if self.vista.sld_intensidad:
            self.vista.sld_intensidad.setRange(1, 20)
            self.vista.sld_intensidad.setValue(5)
            self.vista.sld_intensidad.sliderReleased.connect(self.aplicar_procesamiento)
            self.vista.sld_intensidad.valueChanged.connect(self.actualizar_lbl_filtro)

        if self.vista.sld_umbral:
            self.vista.sld_umbral.setRange(0, 255)
            self.vista.sld_umbral.setValue(127)
            self.vista.sld_umbral.sliderReleased.connect(self.aplicar_procesamiento)

        if self.vista.sld_morfologia:
            self.vista.sld_morfologia.setRange(1, 10)
            self.vista.sld_morfologia.sliderReleased.connect(self.aplicar_procesamiento)

        if self.vista.btn_canny: self.vista.btn_canny.clicked.connect(self.detectar_bordes)
        if self.vista.btn_reset_opencv: self.vista.btn_reset_opencv.clicked.connect(self.reset_opencv)
        if self.vista.btn_exportar: self.vista.btn_exportar.clicked.connect(self.exportar_imagen)
        if self.vista.btn_invertir: self.vista.btn_invertir.clicked.connect(self.aplicar_procesamiento)
        
        print("-------------------------------------------\n")

    def actualizar_lbl_filtro(self):
        val = self.vista.sld_intensidad.value()
        if val % 2 == 0: val += 1
        if self.vista.lbl_valor_filtro_ref:
            self.vista.lbl_valor_filtro_ref.setText(str(val))

    def cargar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(None, "Abrir Imagen", "", "Images (*.png *.jpg *.dcm *.nii);;All (*)")
        if ruta:
            if self.modelo.cargar_y_procesar(ruta):
                if self.modelo.tipo_archivo == "OPENCV":
                    self.vista.stacked_procesamiento.setCurrentIndex(1)
                    self.actualizar_vista_opencv()
                else:
                    self.vista.stacked_procesamiento.setCurrentIndex(0)
                    self.actualizar_cortes()
                self.vista.mostrar_metadatos(self.modelo.metadata)

    def aplicar_procesamiento(self):
        if self.modelo.img_original is None: return
        
        img = self.modelo.img_original.copy()
        
        # Filtros
        filtro = self.vista.cb_filtro_tipo.currentText()
        k = self.vista.sld_intensidad.value()
        if k % 2 == 0: k += 1
        
        if filtro == "Gaussian Blur": img = cv2.GaussianBlur(img, (k, k), 0)
        elif filtro == "Median Blur": img = cv2.medianBlur(img, k)
        elif filtro == "Bilateral": img = cv2.bilateralFilter(img, 9, 75, 75)

        # Umbral
        umbral_tipo = self.vista.cb_umbral_tipo.currentText()
        th_val = self.vista.sld_umbral.value()
        
        if umbral_tipo != "Ninguno":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            if umbral_tipo == "Binario Simple": _, img = cv2.threshold(gray, th_val, 255, cv2.THRESH_BINARY)
            elif umbral_tipo == "Binario Invertido": _, img = cv2.threshold(gray, th_val, 255, cv2.THRESH_BINARY_INV)
            elif umbral_tipo == "Otsu": _, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif umbral_tipo == "Adaptativo": img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Morfología
        morfo = self.vista.cb_morfologia.currentText()
        its = self.vista.sld_morfologia.value()
        kernel = np.ones((3,3), np.uint8)
        
        if morfo == "Erosion": img = cv2.erode(img, kernel, iterations=its)
        elif morfo == "Dilatacion": img = cv2.dilate(img, kernel, iterations=its)
        elif morfo == "Apertura": img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        elif morfo == "Cierre": img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

        self.modelo.img_procesada = img
        self.actualizar_vista_opencv()

    def detectar_bordes(self):
        if self.modelo.img_original is None: return
        gray = cv2.cvtColor(self.modelo.img_original, cv2.COLOR_BGR2GRAY) if len(self.modelo.img_original.shape) == 3 else self.modelo.img_original
        self.modelo.img_procesada = cv2.Canny(gray, 50, 150)
        self.actualizar_vista_opencv()

    def reset_opencv(self):
        if self.modelo.img_original is not None:
            self.modelo.img_procesada = self.modelo.img_original.copy()
            self.vista.cb_filtro_tipo.setCurrentIndex(0)
            self.vista.cb_umbral_tipo.setCurrentIndex(0)
            self.vista.cb_morfologia.setCurrentIndex(0)
            self.actualizar_vista_opencv()

    def actualizar_vista_opencv(self):
        self.vista.mostrar_slice(self.modelo.img_original, self.vista.lbl_img_original)
        self.vista.mostrar_slice(self.modelo.img_procesada, self.vista.lbl_img_procesada)

    def exportar_imagen(self):
        if self.modelo.img_procesada is None: return
        ruta, _ = QFileDialog.getSaveFileName(None, "Guardar", "procesada.png", "PNG (*.png)")
        if ruta: cv2.imwrite(ruta, self.modelo.img_procesada)

    def guardar_datos_csv(self):
        pass # Tu lógica CSV

    def actualizar_cortes(self):
        pass # Tu lógica DICOM