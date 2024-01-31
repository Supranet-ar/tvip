import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QLabel, QPushButton, QWidget
import mysql.connector

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Selección de Base de Datos")
        self.setGeometry(100, 100, 400, 200)

        # Crear widgets
        self.label = QLabel("Selecciona la base de datos:", self)
        self.database_combobox = QComboBox(self)
        self.database_combobox.addItem("Local")
        self.database_combobox.addItem("Remota")

        self.update_button = QPushButton("Actualizar Datos", self)
        self.update_button.clicked.connect(self.actualizar_datos)

        # Diseño de la interfaz
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.database_combobox)
        layout.addWidget(self.update_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        # Conexión a la base de datos
        self.connection = None
        self.cursor = None

    def conectar_base_datos(self, local=True):
        if local:
            self.connection = mysql.connector.connect(
                host="192.168.100.117",
                user="tvip",
                password="3434",
                database="tvip"
            )
        else:
            self.connection = mysql.connector.connect(
                host="",
                user="192.168.100.113",
                password="1234",
                database="tvip"
            )

        self.cursor = self.connection.cursor()

    def cerrar_conexion(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    def actualizar_datos(self):
        base_datos_local = self.database_combobox.currentText() == "Local"

        try:
            self.conectar_base_datos(local=base_datos_local)

            # Ejemplo de consulta: obtener todos los registros de la tabla 'habitaciones'
            query = "SELECT * FROM habitaciones"
            self.cursor.execute(query)
            habitaciones = self.cursor.fetchall()

            # Procesar los datos y mostrarlos en la interfaz
            for habitacion in habitaciones:
                print(f"Habitación {habitacion[0]} - IP: {habitacion[1]}")

            # Después de procesar los datos, cierra la conexión
            self.cerrar_conexion()

        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            # Maneja el error según sea necesario


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
