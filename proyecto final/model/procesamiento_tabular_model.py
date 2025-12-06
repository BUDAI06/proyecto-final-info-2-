import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.pyplot as plt
class ProcesadorTabularModelo:
    def __init__(self):
        self.df = None

    def cargar_csv(self, ruta):
        try:
            self.df = pd.read_csv(ruta)
            return self.df
        except Exception:
            return None

    def estadisticas(self):
        if self.df is None:
            return "No hay datos cargados."
        return str(self.df.describe())

    def graficar(self, columna):
        if self.df is None:
            return None

        serie = self.df[columna]

        serie_num = pd.to_numeric(serie, errors="coerce").dropna()

        if serie_num.empty:
            raise ValueError("La columna no contiene datos numéricos válidos.")

        

        plt.figure()
        serie_num.plot(kind="hist", bins=20)
        plt.title(f"Histograma de {columna}")
        plt.xlabel(columna)
        plt.ylabel("Frecuencia")

        ruta_img = "grafica_temp.png"
        plt.savefig(ruta_img)
        plt.close()

        return ruta_img
