import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QDateTimeEdit, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDateTime


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ejemplo de ventana")
        loadUi("interfaz/Tareas_2ventana.ui", self)

        # Obtener la fecha y hora actual
        current_datetime = QDateTime.currentDateTime()

        # Configurar el QDateTimeEdit para mostrar la hora actual
        self.dateTimeEdit.setDateTime(current_datetime)

        # Conectar el botón con la función para programar la tarea
        self.botonGuardar.clicked.connect(self.programar_tarea)

    def programar_tarea(self):
        # Obtener la fecha y hora seleccionada por el usuario
        selected_datetime = self.dateTimeEdit.dateTime()

        # Realizar la lógica de programación de la tarea aquí
        # Por ejemplo, podrías imprimir la fecha y hora seleccionada
        print("Tarea programada para:", selected_datetime.toString())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana = VentanaPrincipal()
    ventana.show()

    sys.exit(app.exec_())
