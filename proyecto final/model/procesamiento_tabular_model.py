import pandas as pd
import numpy as np

class ProcesadorTabularModelo:
    def __init__(self):
        self.df = None

    def cargar_csv(self, ruta):
        try:
            # Intentamos leer con coma
            self.df = pd.read_csv(ruta)

            # 2. Si falló, probamos punto y coma
            if self.df.shape[1] < 2:
                self.df = pd.read_csv(ruta, sep=';')

            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    try:
                        serie_limpia = self.df[col].astype(str).str.replace(',', '.')
                        self.df[col] = pd.to_numeric(serie_limpia)
                    except:
                        pass 

            # Eliminar filas vacías
            self.df.dropna(inplace=True)
            return self.df

        except Exception as e:
            print(f"Error leyendo CSV: {e}")
            return None

    def obtener_columnas_numericas(self):
        """Devuelve SOLO las columnas que de verdad son números"""
        if self.df is not None:
            # Filtramos estrictamente columnas numéricas (float o int)
            return self.df.select_dtypes(include=[np.number]).columns.tolist()
        return []

    def calcular_estadisticas(self):
        """Retorna las estadísticas ordenadas"""
        if self.df is None: return "Sin datos."
        
        # Seleccionamos solo números
        df_num = self.df.select_dtypes(include=[np.number])
        if df_num.empty: return "No hay columnas numéricas."

        # Transponemos (.T) para que se vea: Edad | Media | Max... (Más ordenado)
        stats = df_num.describe().T.round(2)
        
        # Seleccionamos solo las columnas importantes para que no se vea desordenado
        if 'count' in stats.columns:
            stats = stats[['mean', 'min', 'max', 'std']] # Ocultamos el 'count' que te confundía
            stats.columns = ['Promedio', 'Min', 'Max', 'Desv.Std']
            
        return stats.to_string()