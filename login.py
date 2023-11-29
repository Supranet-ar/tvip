import subprocess
import sys
from PyQt5 import QtWidgets, uic
import mysql.connector
from mysql.connector import Error

class VentanaLogin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Carga la interfaz de archivo.ui creado en Qt Designer
        self.window = uic.loadUi("interfaz/ventana_login.ui")

        # Carga la interfaz de login exitoso y login error
        self.ventana_exito = uic.loadUi("interfaz/ventana_login_exito.ui")
        self.ventana_error = uic.loadUi("interfaz/ventana_login_error.ui")

        # Conecta la función verificar_usuario al botón de inicio de sesión
        self.window.iniciarSesionButton.clicked.connect(self.verificar_usuario)

        # Conecta la función cerrar_ventana_exito al botón "Salir" de la ventana de éxito
        self.ventana_exito.salirButton.clicked.connect(self.cerrar)

        # Conecta la función cerrar_ventana_error al botón "Salir" de la ventana de error
        self.ventana_error.salirButton.clicked.connect(self.cerrar)

        # Conecta la función mostrar_interfaz_login al botón "Intentar nuevamente" de la ventana de error
        self.ventana_error.intentarNuevamenteButton.clicked.connect(self.mostrar_interfaz_login)

        # Conecta la función abrir_habitaciones al botón "OK" de la ventana de éxito
        self.ventana_exito.okButton.clicked.connect(self.abrir_habitaciones)

        # Muestra la interfaz de login principal
        self.window.show()

    def verificar_usuario(self):
        print("Verificando usuario...")
        usuario = self.window.Username2.text()
        contrasena = self.window.Pasword.text()

        print(f"Usuario ingresado: {usuario}")
        print(f"Contraseña ingresada: {contrasena}")

        if self.validar_credenciales(usuario, contrasena):
            print("Inicio de sesión exitoso!")
            self.abrir_habitaciones()
        else:
            print("Inicio de sesión fallido.")
            self.mostrar_interfaz_error()

    def validar_credenciales(self, usuario, contrasena):
        try:
            # Conectar a la base de datos MySQL
            connection = mysql.connector.connect(
                host='192.168.100.90',
                database='tvip',
                user='tvip',
                password='3434'
            )

            # Crear un cursor para ejecutar consultas
            cursor = connection.cursor()

            # Consulta para verificar las credenciales
            query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (usuario, contrasena))

            # Obtener el resultado de la consulta
            result = cursor.fetchone()

            # Cerrar el cursor y la conexión
            cursor.close()
            connection.close()

            # Verificar si se encontraron credenciales válidas
            return result is not None

        except Error as e:
            print("Error al conectar a la base de datos:", e)
            return False

    def mostrar_interfaz_exito(self):
        self.ventana_exito.show()  # Muestra la interfaz de login exitoso
        self.window.close()  # Cierra la interfaz de login principal

    def mostrar_interfaz_error(self):
        self.ventana_error.show()  # Muestra la interfaz de login error
        self.window.close()  # Cierra la interfaz de login principal

    def mostrar_interfaz_login(self):
        self.ventana_error.close()  # Cierra la interfaz de login error
        self.window.show()  # Muestra la interfaz de login principal

    def cerrar(self):
        self.window.close()
        self.ventana_exito.close()
        self.ventana_error.close()

    def abrir_habitaciones(self):
        subprocess.run(["python", "main.py"])

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ventana_login = VentanaLogin()
    sys.exit(app.exec_())
