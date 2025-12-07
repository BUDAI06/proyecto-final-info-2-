# model/base_datos_model.py

import sqlite3
import os
from datetime import datetime
import xml.etree.ElementTree as ET # Necesaria para leer XML

class BaseDatosModel:
    def __init__(self, db_name="historial_medico.db"):
        # Determinar la ruta correcta para la base de datos y el XML
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir) 
        
        data_dir = os.path.join(root_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            
        self.db_path = os.path.join(data_dir, db_name)
        # Ruta crítica del archivo XML
        self.xml_path = os.path.join(data_dir, "usuarios.xml") 
        
        self.inicializar_base_datos()

    def inicializar_base_datos(self):
        """Crea las tablas (logs, usuarios, fotos) si no existen en SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Tabla para LOGS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                usuario TEXT,
                accion TEXT,
                detalle TEXT
            )
        ''')

        # 2. Tabla para USUARIOS 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL, 
                nombre TEXT,
                rol TEXT 
            )
        ''')
        
        # 3. Tabla para FOTOS de perfil 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER UNIQUE NOT NULL,
                fecha TEXT,
                foto_b64 TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def validar_credenciales(self, username, password):
        """
        Busca el usuario y valida la contraseña leyendo el archivo XML.
        Retorna un diccionario con los datos del usuario si es exitoso, o None.
        """
        if not os.path.exists(self.xml_path):
            print(f"❌ ERROR CRÍTICO: Archivo XML de usuarios NO ENCONTRADO en: {self.xml_path}")
            return None

        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            user_counter = 1 

            for user_element in root.findall('usuario'):
                
                xml_user = user_element.find('username').text.strip()
                xml_pass = user_element.find('password').text.strip()
                
                # CRÍTICO: Compara el XML en minúsculas con el input normalizado
                if xml_user.lower() == username and xml_pass == password:
                    
                    id_element = user_element.find('id') 
                    if id_element is not None and id_element.text is not None:
                         current_id = int(id_element.text.strip())
                    else:
                         current_id = user_counter 
                         
                    nombre = user_element.find('nombre').text.strip()
                    rol = user_element.find('rol').text.strip()

                    return {
                        'id': current_id, 
                        'username': xml_user, 
                        'nombre': nombre,
                        'rol': rol
                    }
                
                user_counter += 1 
            
            return None
            
        except ET.ParseError as e:
            print(f"ERROR: No se pudo parsear el archivo XML. Verifica el formato: {e}")
            return None
        except Exception as e:
            print(f"ERROR inesperado al leer el XML: {e}")
            return None

    def guardar_foto_perfil(self, user_id, foto_base64):
        """
        Guarda o actualiza la foto codificada en Base64 en la tabla de fotos de SQLite.
        """
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO fotos (usuario_id, fecha, foto_b64) VALUES (?, ?, ?)
                   ON CONFLICT(usuario_id) DO UPDATE SET
                   fecha=excluded.fecha, foto_b64=excluded.foto_b64""",
                (user_id, fecha, foto_base64)
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[DB] Error al guardar foto de perfil: {e}")
    
    def registrar_log(self, usuario, accion, detalle=""):
        """Guarda un evento en la tabla de logs de SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO logs (fecha, usuario, accion, detalle)
                VALUES (?, ?, ?, ?)
            ''', (fecha, usuario, accion, detalle))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB] Error al guardar log: {e}")
