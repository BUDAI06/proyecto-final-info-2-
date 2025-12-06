from model.procesamiento_senales_model import ProcesadorSenalesModelo
from PyQt5.QtWidgets import QFileDialog

class SenalesController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorSenalesModelo()

        self.vista.btn_cargar.clicked.connect(self.cargar_senal)
        self.vista.btn_fft.clicked.connect(self.aplicar_fft)
        self.vista.btn_filtrar.clicked.connect(self.aplicar_filtro)

    def cargar_senal(self):
        ruta, _ = QFileDialog.getOpenFileName(
            None,
            "Cargar señal",
            "",
            "CSV (*.csv);;TXT (*.txt);;Todos (*.*)"
        )
        if not ruta:
            return

        data = self.modelo.cargar_senal(ruta)
        if data is None:
            return

        # Actualizar combobox canales
        self.vista.cb_canal.clear()
        for i in range(self.modelo.n_canales):
            self.vista.cb_canal.addItem(f"Canal {i+1}")

        # Mostrar gráfica cruda
        img = self.modelo.plot_senal(self.modelo.obtener_canal(0))
        self.vista.mostrar_senal(img)

        self.vista.mostrar_info(self.modelo.info_senal())

    def aplicar_fft(self):
        canal = self.vista.cb_canal.currentIndex()
        datos = self.modelo.obtener_canal(canal)
        img = self.modelo.plot_fft(datos)
        self.vista.mostrar_fft(img)

    def aplicar_filtro(self):
        canal = self.vista.cb_canal.currentIndex()
        datos = self.modelo.obtener_canal(canal)
        filtrada = self.modelo.filtrar(datos, 1.0, 40.0)  # ejemplo: 1–40 Hz
        img = self.modelo.plot_senal(filtrada)
        self.vista.mostrar_senal(img)
