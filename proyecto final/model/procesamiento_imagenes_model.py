# modelo/procesamiento_imagenes_model.py
import numpy as np
import os
import pydicom
import nibabel as nib

class ProcesadorImagenesMedicasModelo:
    def __init__(self):
        self.volumen = None        # numpy array 3D
        self.metadata = {}         # diccionario con info del paciente
        self.shape = None          # (Z, Y, X)
        self.espaciado = None      # spacing (si existe)
        self.origen = None
        self.tipo_archivo = None   # "DICOM" o "NIFTI"

    # -----------------------------
    # CARGA PRINCIPAL
    # -----------------------------
    def cargar_y_procesar(self, ruta):
        """Detecta el tipo de archivo y carga automáticamente."""
        ext = ruta.lower()

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

            self.volumen = pixel[np.newaxis, :, :]   # convertimos a volumen 3D de 1 slice
            self.shape = self.volumen.shape          # (1, Y, X)

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
            print("No se encontraron DICOM en la carpeta.")
            return False

        slices = []
        for f in archivos:
            dic = pydicom.dcmread(os.path.join(carpeta, f))
            # Solo añadir si contiene datos de píxel
            if 'PixelData' in dic:
                slices.append(dic)

        if not slices:
            print("No se encontraron slices válidos en la carpeta.")
            return False

        # ordenar por número de instancia (InstanceNumber), ya que ImagePositionPatient[2] falla
        slices.sort(key=lambda x: int(x.InstanceNumber))

        # convertir a matriz 3D
        imgs = np.stack([s.pixel_array for s in slices]).astype(np.int16)

        self.volumen = imgs
        self.shape = imgs.shape  # (Z, Y, X)

        self._extraer_metadata_dicom(slices[0])
        self._convertir_a_hu_dicoms_serie(slices)

        return True
    # -----------------------------
    # CONVERSIÓN A HU (SÓLO DICOM)
    # -----------------------------
    def _convertir_a_hu_dicoms_unico(self, dic):
        intercept = float(getattr(dic, "RescaleIntercept", 0))
        slope = float(getattr(dic, "RescaleSlope", 1))

        hu = self.volumen.astype(np.float32)
        hu = hu * slope + intercept
        self.volumen = hu

    def _convertir_a_hu_dicoms_serie(self, slices):
        intercept = float(getattr(slices[0], "RescaleIntercept", 0))
        slope = float(getattr(slices[0], "RescaleSlope", 1))

        hu = self.volumen.astype(np.float32)
        hu = hu * slope + intercept
        self.volumen = hu

    # -----------------------------
    # METADATA
    # -----------------------------
    def _extraer_metadata_dicom(self, dic):
        self.metadata = {
            "Paciente": getattr(dic, "PatientName", "N/A"),
            "ID del Paciente": getattr(dic, "PatientID", "N/A"),
            "Estudio": getattr(dic, "StudyDescription", "N/A"),
            "Modalidad": getattr(dic, "Modality", "N/A"),
            "Dimensiones": str(self.shape)
        }

    # -----------------------------
    # OBTENER CORTES
    # -----------------------------
    def obtener_corte_axial(self, z):
        """Devuelve corte Z fijo: plano XY"""
        if self.volumen is None:
            return None
        return self.volumen[z, :, :]

    def obtener_corte_coronal(self, y):
        """Devuelve corte Y fijo: plano XZ"""
        if self.volumen is None:
            return None
        return self.volumen[:, y, :]

    def obtener_corte_sagital(self, x):
        """Devuelve corte X fijo: plano YZ"""
        if self.volumen is None:
            return None
        return self.volumen[:, :, x]

