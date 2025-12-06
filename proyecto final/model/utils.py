import os

def validar_ruta(ruta):
    """
    Verifica si una ruta de archivo existe.
    Retorna True si existe, False si no.
    """
    if not ruta:
        return False
    return os.path.exists(ruta)

def obtener_extension(ruta):
    if not ruta:
        return ""
    return os.path.splitext(ruta)[1].lower()
