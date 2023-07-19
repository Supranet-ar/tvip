import sys

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi


class VentanaSecundaria(QMainWindow):
    guardarDatosSignal = pyqtSignal(str)
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Segunda Ventana")
        loadUi("Tareas_2ventana.ui", self)

        # Conectar el botón "Guardar" con la función para guardar los datos y cerrar la ventana
        self.botonGuardar.clicked.connect(self.guardarDatos)

    def guardarDatos(self):
        texto = self.comboBox.currentText()  # Obtener el texto seleccionado del QComboBox
        fecha = self.dateTimeEdit.dateTime().toString("dd/MM/yyyy hh:mm:ss")  # Obtener la fecha y hora como texto
        datos = f"Tarea: {texto}, Fecha: {fecha}"
        self.guardarDatosSignal.emit(datos)
        self.closed.emit()
        self.close()


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana Principal")
        self.listWidget = QListWidget(self)
        self.setCentralWidget(self.listWidget)

        # Crear una instancia de la ventana secundaria y conectar las señales
        self.ventana_secundaria = VentanaSecundaria()
        self.ventana_secundaria.guardarDatosSignal.connect(self.agregarElemento)
        self.ventana_secundaria.closed.connect(self.show)

        # Conectar el botón "Abrir Ventana Secundaria" con la función para mostrar la ventana secundaria
        self.btn_programar.clicked.connect(self.mostrarVentanaSecundaria)

    def mostrarVentanaSecundaria(self):
        self.hide()
        self.ventana_secundaria.show()

    def agregarElemento(self, texto):
        item = QListWidgetItem(texto)
        self.listWidget.addItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_principal = VentanaPrincipal()

    # Cargar el archivo .py de habitaciones
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("ventana_principal", ventana_principal)
    engine.load("habitaciones.py")

    sys.exit(app.exec_())
