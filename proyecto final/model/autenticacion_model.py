import xml.etree.ElementTree as ET
import os

class AutenticacionModel:
    def __init__(self):

        # Carpeta de este archivo .py
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Subir un nivel (model/) → al root del proyecto
        proyecto_dir = os.path.abspath(os.path.join(base_dir, ".."))

        # Ruta FINAL al XML
        ruta = os.path.join(proyecto_dir, "data", "usuarios.xml")

        if not os.path.exists(ruta):
            raise FileNotFoundError(f"ERROR: No se encontró usuarios.xml en:\n{ruta}")

        # Cargar XML
        self.tree = ET.parse(ruta)
        self.root = self.tree.getroot()

    def validar_credenciales(self, username, password):
        for usuario in self.root.findall("usuario"):
            user = usuario.find("username").text
            pwd = usuario.find("password").text

            if username == user and password == pwd:
                return {
                    "username": user,
                    "nombre": usuario.find("nombre").text,
                    "rol": usuario.find("rol").text
                }

        return None
