import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
from base_de_datos import BaseDeDatos
from main import MainWindow


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()


        # Cargar la interfaz desde el archivo .ui
        uic.loadUi("interfaz/seleccion_server.ui", self)
        self.setWindowTitle("Seleccion de Servidor")

        # Conectar botones
        self.btn_local.clicked.connect(self.local_connection)
        self.btn_remote.clicked.connect(self.remote_connection)

    def connect_to_database(self, host, user, password, database):
        try:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if connection.is_connected():
                self.main_window.base_datos = BaseDeDatos(host, user, password, database)
                QMessageBox.information(self, "Info", "Conectado exitosamente!")

                self.main_window = MainWindow()  # instancia de la ventana del panel de control
                self.main_window.show()  # mostrar la ventana
                self.close()  # cerrar la ventana actual

                connection.close()


        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error: {err}")

    def local_connection(self):
        # Datos estándar para conexión local. Reemplaza si es necesario
        self.connect_to_database("localhost", "root", "1234", "tvip")

    def remote_connection(self):
        self.remote = RemoteApp(self)
        self.remote.show()


class RemoteApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Cargar la interfaz desde el archivo .ui
        uic.loadUi("interfaz/formularioDB.ui", self)
        self.setWindowTitle("Conexion Remota")

        # Conectar botón de envío
        self.btn_enviar.clicked.connect(self.on_submit)

    def on_submit(self):
        host = self.hostInput.text()
        user = self.userInput.text()
        password = self.passwordInput.text()
        database = self.databaseInput.text()
        self.parent().connect_to_database(host, user, password, database)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
