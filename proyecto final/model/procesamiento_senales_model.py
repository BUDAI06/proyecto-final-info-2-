import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

class ProcesadorSenalesModelo:
    def __init__(self):
        self.senal = None
        self.n_canales = 0
        self.fs = 250  # Frecuencia de muestreo por defecto (puedes modificar)

    def cargar_senal(self, ruta):
        try:
            datos = np.loadtxt(ruta, delimiter=",")
        except:
            try:
                datos = np.loadtxt(ruta)
            except:
                return None

        if len(datos.shape) == 1:
            datos = datos.reshape(1, -1)

        self.senal = datos
        self.n_canales = datos.shape[0]
        return datos

    def obtener_canal(self, i):
        return self.senal[i]

    def info_senal(self):
        dur = len(self.senal[0]) / self.fs
        return (f"Canales: {self.n_canales}\n"
                f"Muestras: {len(self.senal[0])}\n"
                f"Duración: {dur:.2f} s")

    def plot_senal(self, y):
        return self._plot_to_np(
            lambda: plt.plot(y, linewidth=1)
        )

    def plot_fft(self, y):
        Y = np.fft.rfft(y)
        f = np.fft.rfftfreq(len(y), 1/self.fs)
        return self._plot_to_np(
            lambda: plt.plot(f, np.abs(Y), linewidth=1)
        )

    def filtrar(self, y, fmin, fmax):
        Y = np.fft.rfft(y)
        f = np.fft.rfftfreq(len(y), 1/self.fs)
        mask = (f >= fmin) & (f <= fmax)
        Y_filt = Y * mask
        return np.fft.irfft(Y_filt)

    def _plot_to_np(self, plotting_func):
        plt.figure(figsize=(5,2))
        plotting_func()
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()

        buf.seek(0)
        img = plt.imread(buf)
        return img
