# controlador/tabular_controller.py
from PyQt5.QtWidgets import QFileDialog
from model.procesamiento_tabular_model import ProcesadorTabularModelo

class TabularController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorTabularModelo()

        self.vista.btn_cargar.clicked.connect(self.cargar_csv)
        self.vista.btn_estadisticas.clicked.connect(self.mostrar_estadisticas)
        self.vista.btn_grafica.clicked.connect(self.graficar_columna)

    def cargar_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(
            None,
            "Cargar CSV",
            "",
            "CSV (*.csv)"
        )

        if not ruta:
            return

        df = self.modelo.cargar_csv(ruta)
        if df is not None:
            self.vista.cargar_tabla(df)
            self.vista.cb_columnas.clear()
            self.vista.cb_columnas.addItems(df.columns)

    def mostrar_estadisticas(self):
        texto = self.modelo.estadisticas()
        self.vista.mostrar_info(texto)

    def graficar_columna(self):
        col = self.vista.cb_columnas.currentText()
        img = self.modelo.graficar(col)
        self.vista.mostrar_grafica(img)
