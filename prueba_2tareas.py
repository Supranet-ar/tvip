import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ejemplo de ventana")
        loadUi("ventana_habitaciones.ui", self)

        # Conectar el botón "Guardar" con la función para abrir la segunda ventana
        self.btn_programar.clicked.connect(self.abrirSegundaVentana)

    def abrirSegundaVentana(self):
        self.segundaVentana = VentanaSecundaria(self)
        self.segundaVentana.guardarDatosSignal.connect(self.agregarElemento)
        self.segundaVentana.show()

    def agregarElemento(self, texto):
        item = QListWidgetItem(texto)
        self.listWidget.addItem(item)


class VentanaSecundaria(QMainWindow):
    guardarDatosSignal = pyqtSignal(str)

    def __init__(self, ventanaPrincipal):
        super().__init__()
        self.setWindowTitle("Segunda Ventana")
        self.ventanaPrincipal = ventanaPrincipal
        loadUi("Tareas_2ventana.ui", self)

        # Conectar el botón "Guardar" con la función para guardar los datos y volver a la primera ventana
        self.botonGuardar.clicked.connect(self.guardarDatos)

    def guardarDatos(self):
        texto = self.comboBox.currentText()  # Obtener el texto seleccionado del QComboBox
        fecha = self.dateTimeEdit.dateTime().toString("dd/MM/yyyy hh:mm:ss")  # Obtener la fecha y hora como texto
        datos = f"Tarea: {texto}, Fecha: {fecha}"
        self.guardarDatosSignal.emit(datos)
        self.close()
        self.ventanaPrincipal.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
