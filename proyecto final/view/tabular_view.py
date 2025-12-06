from PyQt5.QtWidgets import QPushButton, QLabel, QTableWidget, QComboBox, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np

class TabularView:
    def __init__(self, main_window):
        self.ui = main_window

        self.btn_cargar = self.ui.findChild(QPushButton, "btn_cargar_csv")
        self.btn_estadisticas = self.ui.findChild(QPushButton, "btn_estadisticas")
        self.btn_grafica = self.ui.findChild(QPushButton, "btn_grafica_columna")

        self.cb_columnas = self.ui.findChild(QComboBox, "cb_columnas")
        
        self.tabla = self.ui.findChild(QTableWidget, "tabla_datos")
        self.lbl_grafica = self.ui.findChild(QLabel, "lbl_grafica")
        self.lbl_info = self.ui.findChild(QLabel, "lbl_info_tabular")

    def mostrar_grafica(self, img_np):
        if self.lbl_grafica is None:
            return

        h, w, c = img_np.shape
        bytes_line = 3 * w
        qimg = QImage(img_np.data, w, h, bytes_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(self.lbl_grafica.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_grafica.setPixmap(pix)

    def mostrar_info(self, texto):
        if self.lbl_info:
            self.lbl_info.setText(texto)

    def cargar_tabla(self, df):
        if self.tabla is None:
            return

        self.tabla.clear()
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(df.columns)

        for i in range(len(df)):
            for j in range(len(df.columns)):
                self.tabla.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))