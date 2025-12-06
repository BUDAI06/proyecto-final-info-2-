from PyQt5.QtWidgets import (QFileDialog, QTableWidgetItem, QMessageBox, QPushButton, 
                             QTableWidget, QLabel, QDialog, QApplication, 
                             QVBoxLayout, QInputDialog, QTextEdit)
from PyQt5.QtCore import Qt
from model.procesamiento_tabular_model import ProcesadorTabularModelo
from matplotlib.figure import Figure 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class TabularController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorTabularModelo()
        
        print("\n--- INICIANDO CONTROLADOR ---")

        # BUSCAR BOTONES
        self.btn_cargar = self.encontrar_boton("btn_cargar_csv", "Cargar")
        self.btn_estadisticas = self.encontrar_boton("btn_estadisticas", "Estadística")
        self.btn_grafica = self.encontrar_boton("btn_grafica_columna", "Grafic")
        
        # LA TABLA 
        self.tabla = self.vista.findChild(QTableWidget, "table_datos") 
        if self.tabla:
            print("Tabla encontrada.")
        else:
            print("ERROR: No se encontró 'table_datos'.")

        # ZONA DE ESTADÍSTICAS
        self.lbl_info = self.vista.findChild(QLabel, "lbl_info_tabular")
        self.txt_stats = QTextEdit()
        self.txt_stats.setReadOnly(True)
        self.txt_stats.setStyleSheet("""
            background-color: #1e1e1e; 
            color: #00ff00; 
            font-family: 'Courier New'; 
            font-size: 11pt; 
            border: 1px solid #333;
        """)

        if self.lbl_info:
            padre = self.lbl_info.parent()
            if padre and padre.layout():
                padre.layout().replaceWidget(self.lbl_info, self.txt_stats)
                self.lbl_info.hide()
        
        # ZONA DE GRÁFICA
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor='#2b2b2b')
        self.canvas = FigureCanvas(self.figure)
        self.canvas_incrustado = False

        self.lbl_grafica = self.vista.findChild(QLabel, "lbl_grafica")
        if self.lbl_grafica:
            padre_g = self.lbl_grafica.parent()
            if padre_g and padre_g.layout():
                padre_g.layout().replaceWidget(self.lbl_grafica, self.canvas)
                self.lbl_grafica.hide()
                self.canvas_incrustado = True
                print("Zona de gráfica preparada.")

        # CONEXIONES
        if self.btn_cargar: self.btn_cargar.clicked.connect(self.cargar_csv)
        if self.btn_estadisticas: self.btn_estadisticas.clicked.connect(self.mostrar_estadisticas)
        if self.btn_grafica: self.btn_grafica.clicked.connect(self.graficar_columna)

    def encontrar_boton(self, nombre_id, texto_parcial):
        btn = self.vista.findChild(QPushButton, nombre_id)
        if btn: return btn
        for b in self.vista.findChildren(QPushButton):
            if texto_parcial.lower() in b.text().lower(): return b
        return None

    def cargar_csv(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog 
            ruta, _ = QFileDialog.getOpenFileName(self.vista, "Cargar CSV", "", "CSV (*.csv)", options=options)
            
            if not ruta: return

            df = self.modelo.cargar_csv(ruta)
            if df is not None:
                self.llenar_tabla(df)
                msg = f"CARGA EXITOSA.\n----------------\nRegistros: {len(df)}\nColumnas: {len(df.columns)}\n\nListo para graficar."
                self.txt_stats.setText(msg)
                QMessageBox.information(self.vista, "Éxito", "Tabla cargada correctamente.")
        except Exception as e:
            print(f"Error: {e}")

    def llenar_tabla(self, df):
        if not self.tabla: return
        
        self.tabla.clear()
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setRowCount(len(df.index))
        self.tabla.setHorizontalHeaderLabels(df.columns)
        
        # Llenado optimizado
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                self.tabla.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

    def mostrar_estadisticas(self):
        if self.modelo.df is None: 
            self.txt_stats.setText("ERROR: Carga un archivo primero.")
            return
        stats = self.modelo.calcular_estadisticas()
        self.txt_stats.setText("--- ESTADÍSTICAS DEL DATASET ---\n\n" + stats)

    def graficar_columna(self):
        QApplication.processEvents()
        if self.modelo.df is None: 
            QMessageBox.warning(self.vista, "Error", "Carga datos primero.")
            return

        cols = self.modelo.obtener_columnas_numericas()
        if not cols:
            QMessageBox.warning(self.vista, "Error", "El archivo no tiene columnas numéricas.")
            return
            
        col, ok = QInputDialog.getItem(self.vista, "Graficar", "Selecciona la variable:", cols, 0, False)
        
        if ok and col:
            try:
                self.figure.clear()
                
                # Colores
                colores = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f1c40f']
                color_barra = colores[len(col) % len(colores)]
                
                ax = self.figure.add_subplot(111, facecolor='#363636')
                datos = self.modelo.df[col]
                
                ax.hist(datos, bins=15, color=color_barra, edgecolor='white', alpha=0.8)
                
                # Estilo Dark Mode
                ax.set_title(f"Distribución: {col}", color='white', fontsize=12, fontweight='bold')
                ax.set_xlabel(col, color='white')
                ax.set_ylabel("Frecuencia", color='white')
                ax.tick_params(colors='white')
                for spine in ax.spines.values(): spine.set_edgecolor('white')
                ax.grid(True, linestyle='--', alpha=0.3, color='white')
                
                self.figure.tight_layout()
                self.canvas.draw()
                
                self.txt_stats.append(f"\nGráfica generada para: {col}")

                # Ventana flotante de emergencia si no se pudo incrustar
                if not self.canvas_incrustado:
                    self.ventana = QDialog(self.vista)
                    self.ventana.setStyleSheet("background-color: #2b2b2b;")
                    lay = QVBoxLayout(self.ventana)
                    lay.addWidget(self.canvas)
                    self.ventana.show()

            except Exception as e:
                self.txt_stats.setText(f"Error graficando: {str(e)}")
