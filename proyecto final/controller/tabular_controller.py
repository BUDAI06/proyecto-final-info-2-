from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox, QVBoxLayout, QPushButton, QComboBox, QTableWidget, QWidget, QLabel, QDialog, QApplication, QInputDialog
from PyQt5.QtCore import Qt
from model.procesamiento_tabular_model import ProcesadorTabularModelo
from matplotlib.figure import Figure 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# --- CLASE PARA VENTANA FLOTANTE ---
class VentanaGrafica(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gráfico Generado")
        self.resize(600, 450)
        self.layout = QVBoxLayout(self)

class TabularController:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorTabularModelo()
        self.ventana_flotante = None 
        
        print("\n--- DIAGNÓSTICO DE INICIO ---")
        
        # 1. BUSCAR COMPONENTES
        self.btn_cargar = self.encontrar_boton("btn_cargar_csv", "Cargar")
        self.btn_estadisticas = self.encontrar_boton("btn_estadisticas", "Estadística")
        self.btn_grafica = self.encontrar_boton("btn_grafica_columna", "Grafic")
        
        self.cb_columnas = self.vista.findChild(QComboBox, "cb_columnas")
        if self.cb_columnas:
            print("Combo Box 'cb_columnas' ENCONTRADO.")
        else:
            print("ERROR: No se encontró el Combo Box 'cb_columnas'.")

        self.tabla = self.vista.findChild(QTableWidget, "table_datos") 

        # 2. CONEXIONES
        if self.btn_cargar: self.btn_cargar.clicked.connect(self.cargar_csv)
        if self.btn_estadisticas: self.btn_estadisticas.clicked.connect(self.mostrar_estadisticas)
        if self.btn_grafica: self.btn_grafica.clicked.connect(self.graficar_columna)
            
        # 3. PREPARAR GRÁFICA (OBJETO PURO)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas_incrustado = False
        
        if hasattr(self.vista, 'gridLayout_2'):
            try:
                self.vista.gridLayout_2.addWidget(self.canvas, 4, 1)
                self.canvas_incrustado = True
                print("Canvas incrustado en gridLayout_2")
                lbl = self.vista.findChild(QLabel, "lbl_grafica")
                if lbl: lbl.hide()
            except: pass
        
        if not self.canvas_incrustado:
            layout = self.vista.findChild(QVBoxLayout, "layout_grafica")
            if layout:
                layout.addWidget(self.canvas)
                self.canvas_incrustado = True

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
                
                # LLENADO DE COMBO BOX
                cols = self.modelo.obtener_columnas_numericas()
                if self.cb_columnas:
                    self.cb_columnas.clear()
                    self.cb_columnas.addItems(cols)
                    print(f"Combo Box llenado con: {cols}")
                else:
                    print("No hay Combo Box para llenar.")
                
                QMessageBox.information(self.vista, "Éxito", f"Datos cargados.\nColumnas disponibles: {cols}")
        except Exception as e:
            print(f"Error carga: {e}")

    def llenar_tabla(self, df):
        if not self.tabla: return
        self.tabla.clear()
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setRowCount(len(df.index))
        self.tabla.setHorizontalHeaderLabels(df.columns)
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                self.tabla.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

    def mostrar_estadisticas(self):
        if self.modelo.df is None: return
        stats = self.modelo.calcular_estadisticas()
        msg = QMessageBox(self.vista)
        msg.setWindowTitle("Estadísticas")
        msg.setTextFormat(Qt.RichText)
        msg.setText(f"<pre style='font-family: Courier New; font-size: 11pt'>{stats}</pre>")
        msg.exec_()

    def graficar_columna(self):
        print("\n>>> INICIO DE DIAGNÓSTICO DE GRAFICADO <<<")
        QApplication.processEvents()

        # 1. CHEQUEO DE DATOS
        if self.modelo.df is None: 
            print("Error: No hay datos cargados (df es None).")
            QMessageBox.warning(self.vista, "Error", "Carga un CSV primero.")
            return

        # 2. OBTENER COLUMNA (Plan A: Combo Box | Plan B: Preguntar)
        col = ""
        if self.cb_columnas and self.cb_columnas.count() > 0:
            col = self.cb_columnas.currentText()
            print(f"Columna seleccionada del Combo: '{col}'")
        
        # Si falla el combo, preguntamos al usuario (PLAN DE RESPALDO)
        if not col:
            print("Combo Box vacío o no encontrado. Preguntando al usuario...")
            cols_disponibles = self.modelo.obtener_columnas_numericas()
            if not cols_disponibles:
                QMessageBox.warning(self.vista, "Error", "No hay columnas numéricas en el archivo.")
                return
                
            item, ok = QInputDialog.getItem(self.vista, "Seleccionar Columna", 
                                          "Elige la variable a graficar:", cols_disponibles, 0, False)
            if ok and item:
                col = item
            else:
                return

        try:
            print(f"Dibujando histograma de: {col}")
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            datos = self.modelo.df[col]
            ax.hist(datos, bins=15, color='#3498db', edgecolor='black', alpha=0.7)
            ax.set_title(f"Distribución de {col}")
            ax.set_xlabel(col)
            ax.set_ylabel("Frecuencia")
            ax.grid(True, linestyle='--', alpha=0.5)
            
            self.canvas.draw()
            print("¡DIBUJO COMPLETADO EN MEMORIA!")

            # 4. VERIFICACIÓN VISUAL
            if not self.canvas_incrustado or self.canvas.width() < 10:
                print("Canvas oculto. Abriendo ventana flotante de emergencia.")
                self.abrir_ventana_flotante()
            else:
                print("Gráfica actualizada en interfaz principal.")

        except Exception as e:
            print(f"ERROR CRÍTICO AL GRAFICAR: {e}")
            QMessageBox.critical(self.vista, "Error", str(e))

    def abrir_ventana_flotante(self):
        if self.ventana_flotante is None:
            self.ventana_flotante = VentanaGrafica(self.vista)
            self.ventana_flotante.layout.addWidget(self.canvas)
        self.ventana_flotante.show()