# modelo/procesamiento_imagenes_model.py
import numpy as np
import os
import pydicom
import nibabel as nib
import cv2  # <--- Agregado para soporte PNG/JPG

class ProcesadorImagenesMedicasModelo:
    def __init__(self):
        self.volumen = None        # numpy array 3D
        self.metadata = {}         # diccionario con info del paciente
        self.shape = None          # (Z, Y, X)
        self.espaciado = None      # spacing (si existe)
        self.origen = None
        self.tipo_archivo = None   # "DICOM", "NIFTI" u "OPENCV"
        
        # --- NUEVOS ATRIBUTOS PARA IMÁGENES ESTÁNDAR ---
        self.img_original = None
        self.img_procesada = None

    # -----------------------------
    # CARGA PRINCIPAL
    # -----------------------------
    def cargar_y_procesar(self, ruta):
        """Detecta el tipo de archivo y carga automáticamente."""
        ext = ruta.lower()

        # Soporte para Imágenes Estándar (OpenCV)
        if ext.endswith((".png", ".jpg", ".jpeg")):
            return self._cargar_opencv(ruta)

        if ext.endswith(".nii") or ext.endswith(".nii.gz"):
            self.tipo_archivo = "NIFTI"
            return self._cargar_nifti(ruta)

        if ext.endswith(".dcm"):
            self.tipo_archivo = "DICOM"
            return self._cargar_dicom_unico(ruta)

        # Si es carpeta → es una serie DICOM
        if os.path.isdir(ruta):
            self.tipo_archivo = "DICOM"
            return self._cargar_dicom_serie(ruta)

        return False

    # -----------------------------
    # CARGA IMAGEN ESTÁNDAR
    # -----------------------------
    def _cargar_opencv(self, ruta):
        try:
            self.tipo_archivo = "OPENCV"
            self.img_original = cv2.imread(ruta)
            if self.img_original is None:
                return False
            self.img_procesada = self.img_original.copy()
            self.metadata = {
                "Tipo": "Imagen Estándar",
                "Resolución": f"{self.img_original.shape[1]}x{self.img_original.shape[0]}",
                "Canales": str(self.img_original.shape[2]) if len(self.img_original.shape) > 2 else "1"
            }
            return True
        except Exception as e:
            print("Error cargando imagen estándar:", e)
            return False

    # -----------------------------
    # CARGA NIFTI
    # -----------------------------
    def _cargar_nifti(self, ruta):
        try:
            img = nib.load(ruta)
            data = img.get_fdata()
            self.volumen = data.astype(np.float32)

            self.shape = self.volumen.shape  # (Z, Y, X)
            self.metadata = {
                "Tipo": "NIFTI",
                "Dimensiones": str(self.shape),
                "Voxel size": str(img.header.get_zooms())
            }
            return True
        except Exception as e:
            print("Error cargando NIFTI:", e)
            return False

    # -----------------------------
    # CARGA DICOM INDIVIDUAL
    # -----------------------------
    def _cargar_dicom_unico(self, ruta):
        try:
            dic = pydicom.dcmread(ruta)
            pixel = dic.pixel_array.astype(np.int16)

            self.volumen = pixel[np.newaxis, :, :]
            self.shape = self.volumen.shape

            self._extraer_metadata_dicom(dic)
            self._convertir_a_hu_dicoms_unico(dic)
            return True
        except Exception as e:
            print("Error cargando DICOM único:", e)
            return False

    # -----------------------------
    # CARGA SERIE DICOM
    # -----------------------------
    def _cargar_dicom_serie(self, carpeta):
        archivos = [f for f in os.listdir(carpeta) if f.lower().endswith(".dcm")]
        if not archivos:
            return False

        slices = []
        for f in archivos:
            dic = pydicom.dcmread(os.path.join(carpeta, f))
            if 'PixelData' in dic:
                slices.append(dic)

        if not slices:
            return False

        slices.sort(key=lambda x: int(x.InstanceNumber))
        imgs = np.stack([s.pixel_array for s in slices]).astype(np.int16)

        self.volumen = imgs
        self.shape = imgs.shape

        self._extraer_metadata_dicom(slices[0])
        self._convertir_a_hu_dicoms_serie(slices)
        return True

    def _convertir_a_hu_dicoms_unico(self, dic):
        intercept = float(getattr(dic, "RescaleIntercept", 0))
        slope = float(getattr(dic, "RescaleSlope", 1))
        self.volumen = self.volumen.astype(np.float32) * slope + intercept

    def _convertir_a_hu_dicoms_serie(self, slices):
        intercept = float(getattr(slices[0], "RescaleIntercept", 0))
        slope = float(getattr(slices[0], "RescaleSlope", 1))
        self.volumen = self.volumen.astype(np.float32) * slope + intercept

    def _extraer_metadata_dicom(self, dic):
        self.metadata = {
            "Paciente": getattr(dic, "PatientName", "N/A"),
            "ID del Paciente": getattr(dic, "PatientID", "N/A"),
            "Estudio": getattr(dic, "StudyDescription", "N/A"),
            "Modalidad": getattr(dic, "Modality", "N/A"),
            "Dimensiones": str(self.shape),
            "Fecha del Estudio": getattr(dic, "StudyDate", "N/A"),
            "UID del Estudio": getattr(dic, "StudyInstanceUID", "N/A")
        }
        
    def obtener_metadata_para_csv(self):
        return self.metadata if self.metadata else None
        
    def obtener_corte_axial(self, z):
        return self.volumen[z, :, :] if self.volumen is not None else None

    def obtener_corte_coronal(self, y):
        return self.volumen[:, y, :] if self.volumen is not None else None

    def obtener_corte_sagital(self, x):
        return self.volumen[:, :, x] if self.volumen is not None else None