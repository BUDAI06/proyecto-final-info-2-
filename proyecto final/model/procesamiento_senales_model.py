import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.signal import savgol_filter, butter, lfilter
from io import BytesIO
import scipy.signal as signal


class ProcesadorSenalesModelo:

    FS = 1000  # Frecuencia de muestreo

    def __init__(self):
        self.data = None
        self.senal = None
        self.llaves = []
        self.ruta = ""

    # ============================================================
    #         MÉTODOS DE CARGA
    # ============================================================

    def cargar_archivo(self, ruta_completa):
        """Carga archivo MAT y obtiene sus llaves."""
        self.data = None
        self.senal = None
        self.llaves = []

        try:
            self.data = loadmat(ruta_completa, mat_dtype=True)
            self.llaves = [k for k in self.data.keys() if not k.startswith('__')]
            self.ruta = ruta_completa
            return self.llaves if self.llaves else None

        except Exception as e:
            print(f"Error al leer archivo MAT: {e}")
            return None

    def seleccionar_llave(self, llave_elegida):
        """Normaliza la señal a forma (Canales x Muestras)."""
        if self.data is None or llave_elegida not in self.llaves:
            return False

        senal = self.data[llave_elegida]

        # Normalizaciones
        if senal.ndim == 3:
            c, m, e = senal.shape
            senal = senal.reshape(c, m * e)

        if senal.ndim == 1:
            senal = senal.reshape(1, -1)

        if senal.ndim == 2 and senal.shape[0] > senal.shape[1] and senal.shape[1] < 100:
            senal = senal.T

        self.senal = senal.astype(float)

        return True

    def obtener_canal(self, i):
        if self.senal is None:
            return None
        try:
            return self.senal[i, :].astype(float)
        except IndexError:
            return None

    def info_senal(self):
        if self.senal is None or self.senal.shape[1] == 0:
            return "No hay señal cargada."
        n_muestras = self.senal.shape[1]
        n_canales = self.senal.shape[0]
        dur = n_muestras / self.FS
        return (
            f"Canales: {n_canales}\n"
            f"Muestras: {n_muestras}\n"
            f"Duración: {dur:.2f} s\n"
            f"F. Muestreo: {self.FS} Hz"
        )

    # ============================================================
    #       UTILIDAD: REDUCCIÓN DE PUNTOS PARA EVITAR BLOQUES
    # ============================================================

    def _reducir_muestras(self, y, max_points=6000):
        """Reduce la cantidad de puntos para evitar gráficos saturados o rellenos."""
        n = len(y)
        if n <= max_points:
            return y

        factor = max(1, n // max_points)
        return y[::factor]

    # ============================================================
    #                       FILTRO
    # ============================================================

    def filtrar(self, y, fmin, fmax, orden=5):
        if y is None or len(y) == 0:
            return None

        nyq = 0.5 * self.FS
        low = fmin / nyq
        high = fmax / nyq

        if low <= 0 or high >= 1 or low >= high:
            return None

        b, a = butter(orden, [low, high], btype='band')
        return lfilter(b, a, y)

    # ============================================================
    #              FUNCIÓN BASE PARA GENERAR IMAGENES
    # ============================================================

    def _generar_grafico_simple_bytes(self, plotting_func, titulo, xlabel, ylabel):

        plt.figure(figsize=(6, 3))

        plotting_func()

        plt.title(titulo, fontsize=12, fontweight='bold')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.grid(True, linestyle='--', color='lightgray', alpha=0.8)
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        return buf.read()

    # ============================================================
    #                       GRÁFICOS
    # ============================================================

    def plot_senal(self, y, titulo="Señal en el Tiempo"):
        if y is None:
            return None

        # ↓↓↓↓   Nueva mejora: evitar bloque negro   ↓↓↓↓
        y_red = self._reducir_muestras(y)
        t = np.arange(len(y_red)) / self.FS

        return self._generar_grafico_simple_bytes(
            lambda: plt.plot(t, y_red, linewidth=0.7, color='gray'),
            titulo=titulo,
            xlabel="Tiempo (s)",
            ylabel="Amplitud (µV)"
        )

    def plot_fft(self, y):
        if y is None or len(y) == 0:
            return None

        y_red = self._reducir_muestras(y)

        Y = np.fft.rfft(y_red)
        f = np.fft.rfftfreq(len(y_red), 1 / self.FS)

        return self._generar_grafico_simple_bytes(
            lambda: plt.plot(f, np.abs(Y), linewidth=0.9, color='orange'),
            titulo="Espectro de Frecuencia (FFT)",
            xlabel="Frecuencia (Hz)",
            ylabel="Amplitud"
        )

    def plot_segmento(self, canal, inicio_s, fin_s):
        if self.senal is None:
            return None

        num_muestras = self.senal.shape[1]
        inicio = int(inicio_s * self.FS)
        fin = int(fin_s * self.FS)

        if inicio < 0 or fin > num_muestras or inicio >= fin:
            return None

        segmento = self.senal[canal, inicio:fin]
        segmento = self._reducir_muestras(segmento)
        tiempo = np.arange(len(segmento)) / self.FS

        if len(segmento) > 51:
            try:
                segmento = savgol_filter(segmento, 51, 3)
            except:
                pass

        titulo = f"Segmento del Canal {canal+1}: {inicio_s:.3f}s – {fin_s:.3f}s"

        return self._generar_grafico_simple_bytes(
            lambda: plt.plot(tiempo, segmento, color='forestgreen', linewidth=0.8),
            titulo=titulo,
            xlabel="Tiempo (s)",
            ylabel="Amplitud (µV)"
        )

    def plot_contaminacion_comparativa(self, canal_idx, xmin_s, xmax_s, intensity=0.3):
        if self.senal is None:
            return None

        num_canales, num_muestras = self.senal.shape
        xmin = int(xmin_s * self.FS)
        xmax = int(xmax_s * self.FS)

        if canal_idx < 0 or canal_idx >= num_canales or xmin >= xmax:
            return None

        tiempo = np.arange(num_muestras) / self.FS
        canal_original = self.senal[canal_idx].copy()

        # Normalización
        amp_factor = 100 / np.max(np.abs(canal_original)) if np.max(np.abs(canal_original)) != 0 else 1
        canal_original *= amp_factor

        base_std = np.std(canal_original) if np.std(canal_original) > 0 else 1.0

        ruido = np.random.normal(0, base_std * intensity, xmax - xmin)
        canal_contaminado = canal_original.copy()
        canal_contaminado[xmin:xmax] += ruido

        # Suavizar
        suav = lambda x: np.convolve(x, np.ones(10) / 10, mode='same')
        canal_original_suave = suav(self._reducir_muestras(canal_original))
        canal_contaminado_suave = suav(self._reducir_muestras(canal_contaminado))
        tiempo_red = np.linspace(0, tiempo[-1], len(canal_original_suave))

        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
        fig.suptitle(f"Contaminación del Canal {canal_idx + 1}", fontsize=13, fontweight="bold")

        axes[0].plot(tiempo_red, canal_original_suave, color='blue', linewidth=0.8)
        axes[0].set_title("Original")

        axes[1].plot(tiempo_red, canal_contaminado_suave, color='red', linewidth=0.8)
        axes[1].axvspan(xmin_s, xmax_s, color='salmon', alpha=0.25)
        axes[1].set_title(f"Contaminado ({xmin_s}-{xmax_s} s)")

        for ax in axes:
            ax.set_xlabel("Tiempo (s)")
            ax.grid(True, linestyle='--', color='lightgray', alpha=0.8)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        plt.tight_layout(rect=[0, 0, 1, 0.9])

        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=100)
        plt.close(fig)
        buf.seek(0)
        return buf.read()
