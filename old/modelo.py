# Modelo.py
import xml.etree.ElementTree as ET
import pydicom
import numpy as np
import os

class AutenticadorModelo:
    """
    Clase que contiene la lógica de negocio para la autenticación.
    """
    def __init__(self, xml_path='./users/credenciales.xml'):
        self.xml_path = xml_path

    def validar_credenciales(self, usuario, password):
        """
        Verifica si el usuario y la contraseña son válidos buscando en el XML.
        """
        if not usuario or not password:
            return False # No permite campos vacíos
            
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            # Recorre todos los tags <usuario>
            for user_tag in root.findall('usuario'):
                nombre = user_tag.find('nombre').text
                clave = user_tag.find('password').text
                
                if nombre == usuario and clave == password:
                    return True # ¡Éxito!
                    
            return False # Fallo: credenciales no encontradas
            
        except FileNotFoundError:
            print("ERROR: Archivo XML de credenciales no encontrado.")
            return False
        except Exception as e:
            print(f"ERROR al procesar XML: {e}")
            return False

# Aquí se agregarán más clases de Modelo (ProcesadorSenales, DBManager, etc.)

# Modelo.py (Agregar esta nueva clase)
class ProcesadorImagenesMedicasModelo:
    """Contiene la lógica para DICOM, NIFTI y la conversión HU."""
    def __init__(self):
        self.volumen_hu = None      # El volumen 3D en unidades HU
        self.volumen_original = None # Datos originales del píxel
        self.metadata = {}          # Para almacenar información del paciente/estudio
        self.shape = (0, 0, 0)      # Dimensiones del volumen (Z, Y, X)
        
    def cargar_y_procesar(self, file_path):
        """
        Carga una imagen y realiza la conversión a la escala Hounsfield (si es DICOM/TC).
        Retorna True si fue exitoso.
        """
        if file_path.lower().endswith(('.dcm', '.dicom')):
            return self._procesar_dicom(file_path)
        # Aquí se añadiría la lógica para NIFTI, JPG/PNG (usando OpenCV), etc.
        # Por ahora, nos enfocamos en DICOM y HU.
        return False # Tipo de archivo no soportado o error
        
    def _procesar_dicom(self, file_path):
        """
        Lógica interna para DICOM: carga, extrae metadatos y convierte a HU.
        """
        try:
            ds = pydicom.dcmread(file_path)
            self.volumen_original = ds.pixel_array.astype(np.float32)
            
            # 1. Extracción de Metadatos (Requisito)
            self.metadata['Paciente'] = getattr(ds, 'PatientName', 'ANONIMIZADO')
            self.metadata['ID_Estudio'] = getattr(ds, 'StudyID', 'N/A')
            self.metadata['RescaleSlope'] = float(getattr(ds, 'RescaleSlope', 1.0))
            self.metadata['RescaleIntercept'] = float(getattr(ds, 'RescaleIntercept', 0.0))
            
            # 2. Conversión a Escala Hounsfield (HU) (Requisito Clave)
            # HU = PixelValue * RescaleSlope + RescaleIntercept
            slope = self.metadata['RescaleSlope']
            intercept = self.metadata['RescaleIntercept']
            
            self.volumen_hu = self.volumen_original * slope + intercept
            self.shape = self.volumen_hu.shape

            # Si es un único slice, podemos simular el 3D para la visualización
            if len(self.shape) == 2:
                self.volumen_hu = np.expand_dims(self.volumen_hu, axis=0)
                self.shape = self.volumen_hu.shape
                
            return True
            
        except Exception as e:
            print(f"Error al procesar DICOM: {e}")
            return False

    def obtener_corte_axial(self, slice_index):
        """Devuelve el corte axial (slice Z) en formato HU."""
        if self.volumen_hu is not None and slice_index < self.shape[0]:
            # Retorna el slice Z (el primero es el eje Z en (Z, Y, X))
            return self.volumen_hu[slice_index, :, :]
        return None

    # Métodos para obtener cortes coronal y sagital (se implementan con NumPy)
    def obtener_corte_coronal(self, slice_index):
        """Devuelve el corte coronal (slice Y)."""
        if self.volumen_hu is not None and slice_index < self.shape[1]:
            # Retorna el slice Y (el segundo índice en (Z, Y, X))
            return self.volumen_hu[:, slice_index, :]
        return None

    def obtener_corte_sagital(self, slice_index):
        """Devuelve el corte sagital (slice X)."""
        if self.volumen_hu is not None and slice_index < self.shape[2]:
            # Retorna el slice X (el tercer índice en (Z, Y, X))
            return self.volumen_hu[:, :, slice_index]
        return None