from model.procesamiento_senales_model import ProcesadorSenalesModelo
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLineEdit # QLineEdit si añades campos de entrada
from PyQt5.QtCore import Qt

class SenalesController:
    
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProcesadorSenalesModelo()

        # 🚨 Conexiones de Botones y ComboBox 🚨
        
        # Carga
        if hasattr(self.vista, 'btn_cargar'): 
            self.vista.btn_cargar.clicked.connect(self.cargar_senal)
        
        # Procesamiento
        if hasattr(self.vista, 'btn_fft'):
            self.vista.btn_fft.clicked.connect(self.aplicar_fft)
        if hasattr(self.vista, 'btn_filtrar'):
            self.vista.btn_filtrar.clicked.connect(self.aplicar_filtro)
            
        # Segmento y Contaminación (Asume que añadirás botones para esto)
        # if hasattr(self.vista, 'btn_segmento'):
        #     self.vista.btn_segmento.clicked.connect(self.aplicar_segmento)
        # if hasattr(self.vista, 'btn_contaminar'):
        #     self.vista.btn_contaminar.clicked.connect(self.aplicar_contaminacion)
        
        # Selector de Canal
        if hasattr(self.vista, 'cb_canal'):
            self.vista.cb_canal.currentIndexChanged.connect(self.actualizar_grafica_canal)


    ## --- Lógica de Carga y Selección ---

    def cargar_senal(self):
        """
        Abre el diálogo de archivo, carga el archivo .mat, y selecciona la primera llave.
        """
        ruta, _ = QFileDialog.getOpenFileName(
            None,
            "Cargar señal de MATLAB",
            "",
            "MATLAB (*.mat);;Todos (*.*)"
        )
        if not ruta:
            return

        # 1. Cargar el archivo y obtener las llaves (variables)
        llaves_disponibles = self.modelo.cargar_archivo(ruta)
        
        if llaves_disponibles is None:
            QMessageBox.critical(
                None, 
                "Error de Carga", 
                "No se pudo cargar la señal o el archivo no tiene el formato .mat esperado."
            )
            return

        # 2. Seleccionar automáticamente la primera llave
        if llaves_disponibles:
            llave_seleccionada = llaves_disponibles[0]
            
            if self.modelo.seleccionar_llave(llave_seleccionada):
                 self._actualizar_ui_post_seleccion()
            else:
                 QMessageBox.critical(None, "Error de Selección", f"La variable '{llave_seleccionada}' no pudo ser procesada.")
        else:
             QMessageBox.warning(None, "Advertencia", "No se encontraron variables de señal válidas.")


    def _actualizar_ui_post_seleccion(self):
        """Actualiza ComboBox, Info y la gráfica de la señal cruda después de la carga."""
        
        # 1. Actualizar combobox canales
        if hasattr(self.vista, 'cb_canal'):
            self.vista.cb_canal.clear()
            for i in range(self.modelo.senal.shape[0]):
                self.vista.cb_canal.addItem(f"Canal {i+1}")

        # 2. Mostrar gráfica cruda del canal 0 (por defecto)
        datos_canal_0 = self.modelo.obtener_canal(0)
        if datos_canal_0 is not None:
            img_bytes = self.modelo.plot_senal(datos_canal_0)
            self.vista.mostrar_senal(img_bytes)

        # 3. Mostrar información
        self.vista.mostrar_info(self.modelo.info_senal())

    
    def actualizar_grafica_canal(self, index):
        """Muestra la señal cruda cuando se cambia la selección del canal en cb_canal."""
        if self.modelo.senal is None or index < 0: return
            
        datos = self.modelo.obtener_canal(index)
        if datos is not None:
            img_bytes = self.modelo.plot_senal(datos)
            self.vista.mostrar_senal(img_bytes)


    ## --- Lógica de Procesamiento ---

    def _obtener_datos_canal_actual(self):
        """Función auxiliar para obtener los datos del canal seleccionado."""
        if self.modelo.senal is None:
            QMessageBox.warning(None, "Advertencia", "Debe cargar una señal primero.")
            return None
        
        canal_idx = self.vista.cb_canal.currentIndex()
        return self.modelo.obtener_canal(canal_idx)

    def aplicar_fft(self):
        """Calcula y muestra la FFT del canal seleccionado en lbl_fft."""
        datos = self._obtener_datos_canal_actual()
        if datos is None: return
        
        img_bytes = self.modelo.plot_fft(datos)
        self.vista.mostrar_fft(img_bytes) 


    def aplicar_filtro(self):
        """Aplica un filtro Pasa Banda (1-40 Hz) y muestra el resultado en lbl_senal_cruda."""
        datos = self._obtener_datos_canal_actual()
        if datos is None: return
        
        # 🚨 Parámetros de filtro de ejemplo: 1 Hz a 40 Hz
        filtrada = self.modelo.filtrar(datos, 1.0, 40.0) 
        
        if filtrada is not None:
            # Reutiliza plot_senal para mostrar el resultado filtrado
            img_bytes = self.modelo.plot_senal(filtrada, titulo="Señal Filtrada (1-40 Hz)")
            self.vista.mostrar_senal(img_bytes) 
        else:
            QMessageBox.warning(None, "Error de Filtrado", "La señal no pudo ser filtrada o el rango es inválido.")
            
    # --- Ejemplos para funciones avanzadas ---
    
    def aplicar_segmento(self):
        """
        Ejemplo: Muestra un segmento de 5 a 10 segundos. 
        (Necesitas campos de entrada en la UI para ser interactivo)
        """
        datos = self._obtener_datos_canal_actual()
        if datos is None: return

        # Parámetros de ejemplo
        canal = self.vista.cb_canal.currentIndex()
        inicio_s = 5.0
        fin_s = 10.0
        
        img_bytes = self.modelo.plot_segmento(canal, inicio_s, fin_s)
        if img_bytes:
            self.vista.mostrar_senal(img_bytes) 
        else:
            QMessageBox.warning(None, "Error", "Fallo al graficar el segmento.")

    def aplicar_contaminacion(self):
        """
        Ejemplo: Muestra la contaminación comparativa.
        (Necesitas botones o campos de entrada para disparar esto)
        """
        datos = self._obtener_datos_canal_actual()
        if datos is None: return

        # Parámetros de ejemplo
        canal = self.vista.cb_canal.currentIndex()
        xmin_s = 60.0 # Inicio de la contaminación
        xmax_s = 80.0 # Fin de la contaminación
        
        # El modelo devuelve el gráfico de doble panel como un solo PNG
        img_bytes = self.modelo.plot_contaminacion_comparativa(canal, xmin_s, xmax_s)
        if img_bytes:
            self.vista.mostrar_senal(img_bytes) # Muestra el gráfico comparativo en lbl_senal_cruda
        else:
             QMessageBox.warning(None, "Error", "Fallo al generar el gráfico de contaminación.")
