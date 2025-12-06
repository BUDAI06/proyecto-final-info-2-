import sqlite3
import os
from datetime import datetime

class BaseDatosModel:
    def __init__(self, db_name="historial_medico.db"):
        # Crear la base de datos en la carpeta 'data' si es posible, o en la raíz
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir) # Subir al root
        
        data_dir = os.path.join(root_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            
        self.db_path = os.path.join(data_dir, db_name)
        self.inicializar_base_datos()

    def inicializar_base_datos(self):
        """Crea la tabla si no existe."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla para registrar quién entra y qué hace
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                usuario TEXT,
                accion TEXT,
                detalle TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def registrar_log(self, usuario, accion, detalle=""):
        """Guarda un evento en la base de datos."""
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
            print(f"[DB] Log guardado: {usuario} - {accion}")
        except Exception as e:
            print(f"[DB] Error al guardar log: {e}")
