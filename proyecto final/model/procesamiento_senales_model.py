import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.signal import savgol_filter, butter, lfilter
from io import BytesIO
import os 
import scipy.signal as signal 
# from .archivo_mat import ArchivoMAT  # <--- Descomentar si usas la clase ArchivoMAT para otras tareas

class ProcesadorSenalesModelo:
    
    FS = 1000  # Frecuencia de muestreo por defecto
    
    def __init__(self):
        """Inicializa las variables del modelo."""
        self.data = None
        self.senal = None
        self.llaves = []
        self.ruta = ""

    # ----------------------------------------------------------------------
    #                     MÉTODOS DE CARGA Y GESTIÓN
    # ----------------------------------------------------------------------

    def cargar_archivo(self, ruta_completa):
        """Carga el archivo MAT."""
        self.data = None
        self.senal = None
        self.llaves = []
        
        try:
            self.data = loadmat(ruta_completa, mat_dtype=True)
            self.llaves = [k for k in self.data.keys() if not k.startswith('__')]
            self.ruta = ruta_completa
            return self.llaves if self.llaves else None
        except Exception as e:
            print(f"Error al intentar leer el archivo MAT: {e}") 
            return None

    def seleccionar_llave(self, llave_elegida):
        """Selecciona la señal y normaliza su forma a (Canales x Muestras)."""
        if self.data is None or llave_elegida not in self.llaves: return False
            
        senal = self.data[llave_elegida]
        
        # Lógica de Normalización de Forma (Mantenida)
        if senal.ndim == 3:
            c, m, e = senal.shape
            senal = senal.reshape(c, m * e)
        if senal.ndim == 1: senal = senal.reshape(1, -1)
        if senal.ndim == 2 and senal.shape[0] > senal.shape[1] and senal.shape[1] < 100:
            senal = senal.T
            
        self.senal = senal
        return True
        
    def obtener_canal(self, i):
        """Retorna los datos de un canal específico."""
        if self.senal is None: return None
        try: return self.senal[i, :].astype(float)
        except IndexError: return None
        
    def info_senal(self):
        """Genera una cadena de texto con información básica de la señal."""
        if self.senal is None or self.senal.shape[1] == 0: return "No hay señal cargada."
        n_muestras = self.senal.shape[1]
        n_canales = self.senal.shape[0]
        dur = n_muestras / self.FS
        return (f"Canales: {n_canales}\nMuestras: {n_muestras}\n"
                f"Duración: {dur:.2f} s\nF. Muestreo: {self.FS} Hz")

    # ----------------------------------------------------------------------
    #                     MÉTODOS DE PROCESAMIENTO
    # ----------------------------------------------------------------------

    def filtrar(self, y, fmin, fmax, orden=5):
        """Aplica un filtro Butterworth Pasa Banda."""
        if y is None or len(y) == 0: return None
        nyq = 0.5 * self.FS; low = fmin / nyq; high = fmax / nyq
        
        if low <= 0 or high >= 1 or low >= high: return None
             
        b, a = butter(orden, [low, high], btype='band')
        return lfilter(b, a, y)


    # ----------------------------------------------------------------------
    #               MÉTODOS DE GRÁFICOS (APLICANDO ESTILO SOLICITADO)
    # ----------------------------------------------------------------------

    def _generar_grafico_simple_bytes(self, plotting_func, titulo, xlabel, ylabel):
        """
        Función auxiliar para gráficos de un solo panel, aplicando el estilo solicitado
        (Rejilla punteada gris, sin bordes superiores/derechos, color de línea, etc.).
        """
        plt.figure(figsize=(6, 3)) 
        
        plotting_func() # Ejecuta la función de ploteo específica
        
        # --- Aplicación de Estilos de la Imagen (Consistente) ---
        plt.title(titulo, fontsize=12, fontweight='bold')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        # Cuadrícula: Punteada, color gris claro
        plt.grid(True, linestyle='--', color='lightgray', alpha=0.8) 
        
        # Eliminar los bordes del gráfico superior y derecho
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        return buf.read()
        
    # --- GRÁFICO 1: SEÑAL EN DOMINIO DEL TIEMPO (Estilo solicitado) ---

    def plot_senal(self, y, titulo="Señal en Dominio del Tiempo"):
        """
        Retorna la gráfica de tiempo en bytes PNG con el estilo solicitado.
        """
        if y is None: return None
        t = np.arange(len(y)) / self.FS 
        
        # Color azul vibrante ('#1E90FF') y linewidth 1.5 para el estilo solicitado
        return self._generar_grafico_simple_bytes(
            lambda: plt.plot(t, y, linewidth=1.5, color='#1E90FF'), 
            titulo=titulo, 
            xlabel="Tiempo (s)", 
            ylabel="Amplitud (µV)"
        )

    # --- GRÁFICO 2: FFT (Usa el mismo estilo de rejilla y bordes) ---

    def plot_fft(self, y):
        """Retorna la gráfica FFT en bytes PNG."""
        if y is None or len(y) == 0: return None
        Y = np.fft.rfft(y); f = np.fft.rfftfreq(len(y), 1/self.FS)
        
        return self._generar_grafico_simple_bytes(
            lambda: plt.plot(f, np.abs(Y), linewidth=1, color='orange'), 
            titulo="Espectro de Frecuencia (FFT)", 
            xlabel="Frecuencia (Hz)", 
            ylabel="Amplitud"
        )
        
    # --- GRÁFICO 3: SEGMENTO (Puede usar el estilo limpio 'ECG' si lo prefieres, o el simple) ---

    def plot_segmento(self, canal, inicio_s, fin_s):
        """Retorna el gráfico de un segmento específico."""
        if self.senal is None: return None
        
        senal = self.senal
        num_muestras = senal.shape[1]
        inicio = int(inicio_s * self.FS); fin = int(fin_s * self.FS)

        if inicio < 0 or fin > num_muestras or inicio >= fin or canal < 0 or canal >= senal.shape[0]:
            return None

        segmento_canal = senal[canal, inicio:fin]
        tiempo_segmento = np.arange(inicio, fin) / self.FS
        
        segmento_suave = segmento_canal
        if len(segmento_canal) > 51:
             try: segmento_suave = savgol_filter(segmento_canal, 51, 3)
             except: pass

        titulo = f"Segmento del Canal {canal + 1}: {inicio_s:.3f}s – {fin_s:.3f}s"

        return self._generar_grafico_simple_bytes(
            lambda: plt.plot(tiempo_segmento, segmento_suave, color='forestgreen', linewidth=1.2),
            titulo=titulo, 
            xlabel="Tiempo (s)", 
            ylabel="Amplitud (µV)"
        )

    # --- GRÁFICO 4: COMPARATIVO DE CONTAMINACIÓN (Requiere manejo multi-panel manual) ---
    
    def plot_contaminacion_comparativa(self, canal_idx, xmin_s, xmax_s, intensity=0.3):
        """
        Retorna el gráfico de contaminación COMPARATIVO (doble panel) como bytes PNG.
        """
        if self.senal is None: return None
        num_canales, num_muestras = self.senal.shape
        xmin = int(round(xmin_s * self.FS)); xmax = int(round(xmax_s * self.FS))
        xmin = max(0, xmin); xmax = min(num_muestras, xmax)
        if canal_idx < 0 or canal_idx >= num_canales or xmin >= xmax: return None
        
        # --- Cálculo de la Contaminación ---
        tiempo = np.arange(num_muestras) / self.FS
        canal_original = self.senal[canal_idx, :].astype(float)
        amp_factor = 100 / np.max(np.abs(canal_original)) if np.max(np.abs(canal_original)) != 0 else 1
        canal_original *= amp_factor
        base_std = np.std(canal_original) if np.std(canal_original) > 0 else 1.0
        ruido = np.random.normal(0, base_std * intensity, xmax - xmin)
        canal_contaminado = canal_original.copy()
        canal_contaminado[xmin:xmax] += ruido
        canal_original_suave = np.convolve(canal_original, np.ones(10)/10, mode='same')
        canal_contaminado_suave = np.convolve(canal_contaminado, np.ones(10)/10, mode='same')
        
        # --- Generación de Gráfico Multi-Panel (Específico) ---
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
        fig.suptitle(f"Contaminación del Canal {canal_idx + 1}", fontsize=13, fontweight='bold')

        # Plot 1: Original
        axes[0].plot(tiempo, canal_original_suave, color='blue', linewidth=1)
        axes[0].set_title("Original")
        axes[0].set_ylabel("Amplitud (µV)")

        # Plot 2: Contaminado
        axes[1].plot(tiempo, canal_contaminado_suave, color='red', linewidth=1)
        axes[1].axvspan(xmin_s, xmax_s, color='salmon', alpha=0.25, label='Ruido')
        axes[1].set_title(f"Contaminado ({xmin_s:.0f}-{xmax_s:.0f} s)")

        # Estilos Comunes (Aplicando el estilo solicitado: rejilla punteada, sin bordes)
        for ax in axes:
            ax.set_xlabel("Tiempo (s)")
            ax.grid(True, linestyle='--', color='lightgray', alpha=0.8) 
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            
        plt.tight_layout(rect=[0, 0, 1, 0.9])
        
        buf = BytesIO(); fig.savefig(buf, format="png", dpi=100); plt.close(fig)
        buf.seek(0); return buf.read()
