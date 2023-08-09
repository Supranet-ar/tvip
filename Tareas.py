import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.uic import loadUi


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ejemplo de ventana")

        # Cargar la interfaz de Qt Designer desde el archivo .ui
        loadUi("interfaz/Tareas_2ventana.ui", self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana = VentanaPrincipal()
    ventana.show()

    sys.exit(app.exec_())

    # Cargar la interfaz de usuario
    # loadUi("ventana_habitaciones.ui", self)

    # Eliminar la conexión del botón "Programar Tarea"
    # self.btn_programar.clicked.disconnect()

    # Conectar el botón "Abrir Ventana" con la función para abrir la segunda ventana
    # self.btn_programar.clicked.connect(self.abrirSegundaVentana)