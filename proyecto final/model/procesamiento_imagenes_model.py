import numpy as np
import os
import pydicom
import nibabel as nib
import cv2

class ProcesadorImagenesMedicasModelo:
    def __init__(self):
        self.volumen = None
        self.metadata = {}
        self.shape = None
        self.tipo_archivo = None
        self.img_original = None
        self.img_procesada = None

    def cargar_y_procesar(self, ruta):
        ext = ruta.lower()
        if ext.endswith((".jpg", ".png", ".jpeg")):
            self.tipo_archivo = "OPENCV"
            return self._cargar_opencv(ruta)
        if ext.endswith(".nii") or ext.endswith(".nii.gz"):
            self.tipo_archivo = "NIFTI"
            return self._cargar_nifti(ruta)
        if ext.endswith(".dcm"):
            self.tipo_archivo = "DICOM"
            return self._cargar_dicom_unico(ruta)
        if os.path.isdir(ruta):
            self.tipo_archivo = "DICOM"
            return self._cargar_dicom_serie(ruta)
        return False

    def _cargar_opencv(self, ruta):
        try:
            img = cv2.imread(ruta, cv2.IMREAD_UNCHANGED)
            if img is None:
                return False
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.img_original = img
            self.img_procesada = img.copy()
            self.metadata = {
                "Tipo": "Imagen Estándar",
                "Dimensiones": f"{img.shape[1]}x{img.shape[0]}",
                "Canales": str(img.shape[2]) if len(img.shape) == 3 else "1"
            }
            return True
        except:
            return False

    def aplicar_filtro_basico(self, tipo, k_size=3):
        if self.img_original is None:
            return
        img = self.img_original.copy()
        if k_size % 2 == 0:
            k_size += 1

        if tipo == "Desenfoque Gausiano":
            self.img_procesada = cv2.GaussianBlur(img, (k_size, k_size), 0)

        elif tipo == "Escala de Grises":
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            self.img_procesada = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

        elif tipo == "Negativo":
            self.img_procesada = cv2.bitwise_not(img)

        else:
            self.img_procesada = img

    def aplicar_binarizacion(self, tipo_umbral, valor_umbral):
        if self.img_original is None:
            return
        if tipo_umbral == "Ninguno":
            self.img_procesada = self.img_original.copy()
            return

        if len(self.img_original.shape) == 3:
            gray = cv2.cvtColor(self.img_original, cv2.COLOR_RGB2GRAY)
        else:
            gray = self.img_original.copy()

        mode = cv2.THRESH_BINARY
        if tipo_umbral == "Binario Invertido":
            mode = cv2.THRESH_BINARY_INV
        elif tipo_umbral == "Truncar":
            mode = cv2.THRESH_TRUNC
        elif tipo_umbral == "To Zero":
            mode = cv2.THRESH_TOZERO

        _, thresh = cv2.threshold(gray, valor_umbral, 255, mode)
        self.img_procesada = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

    def detectar_bordes_canny(self):
        if self.img_original is None:
            return

        if len(self.img_original.shape) == 3:
            gray = cv2.cvtColor(self.img_original, cv2.COLOR_RGB2GRAY)
        else:
            gray = self.img_original.copy()

        edges = cv2.Canny(gray, 100, 200)
        self.img_procesada = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    def aplicar_morfologia(self, tipo, iteraciones):
        if self.img_original is None:
            return

        if len(self.img_original.shape) == 3:
            gray = cv2.cvtColor(self.img_original, cv2.COLOR_RGB2GRAY)
        else:
            gray = self.img_original.copy()

        kernel = np.ones((5, 5), np.uint8)
        operation = None

        if tipo == "Erosión":
            operation = cv2.MORPH_ERODE
        elif tipo == "Dilatación":
            operation = cv2.MORPH_DILATE
        elif tipo == "Apertura":
            operation = cv2.MORPH_OPEN
        elif tipo == "Cierre":
            operation = cv2.MORPH_CLOSE

        if operation is not None:
            result = cv2.morphologyEx(gray, operation, kernel, iterations=iteraciones)
            self.img_procesada = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

    def reset_imagen(self):
        if self.img_original is not None:
            self.img_procesada = self.img_original.copy()

    def exportar_imagen(self, ruta):
        if self.img_procesada is None:
            raise RuntimeError("No hay imagen para exportar")
        img = self.img_procesada.copy()
        if img.ndim == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(ruta, img)

    def _cargar_nifti(self, ruta):
        try:
            img = nib.load(ruta)
            data = img.get_fdata()
            self.volumen = data.astype(np.float32)
            self.shape = self.volumen.shape
            self.metadata = {
                "Tipo": "NIFTI",
                "Dimensiones": str(self.shape),
                "Voxel": str(img.header.get_zooms())
            }
            return True
        except:
            return False

    def _cargar_dicom_unico(self, ruta):
        try:
            dic = pydicom.dcmread(ruta)
            self.volumen = dic.pixel_array.astype(np.int16)[np.newaxis, :, :]
            self.shape = self.volumen.shape
            self._extraer_metadata_dicom(dic)
            self._convertir_a_hu_dicoms_unico(dic)
            return True
        except:
            return False

    def _cargar_dicom_serie(self, carpeta):
        files = [f for f in os.listdir(carpeta) if f.lower().endswith(".dcm")]
        if not files:
            return False

        slices = [pydicom.dcmread(os.path.join(carpeta, f)) for f in files]
        slices = [s for s in slices if "PixelData" in s]
        if not slices:
            return False

        slices.sort(key=lambda x: int(x.InstanceNumber))
        self.volumen = np.stack([s.pixel_array for s in slices]).astype(np.int16)
        self.shape = self.volumen.shape
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
            "ID": getattr(dic, "PatientID", "N/A"),
            "Estudio": getattr(dic, "StudyDescription", "N/A"),
            "Modality": getattr(dic, "Modality", "N/A"),
            "Dimensiones": str(self.shape),
            "Fecha": getattr(dic, "StudyDate", "N/A"),
            "UID": getattr(dic, "StudyInstanceUID", "N/A")
        }

    def obtener_metadata_para_csv(self):
        return self.metadata if self.metadata else None

    def obtener_corte_axial(self, z):
        return self.volumen[z, :, :] if self.volumen is not None else None

    def obtener_corte_coronal(self, y):
        return self.volumen[:, y, :] if self.volumen is not None else None

    def obtener_corte_sagital(self, x):
        return self.volumen[:, :, x] if self.volumen is not None else None
