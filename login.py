import json
import subprocess
import sys
from multiprocessing.dummy import Process

from PyQt5 import QtWidgets, uic
import mysql.connector
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QDialog, QMessageBox, QVBoxLayout, QLabel, QPushButton
from mysql.connector import Error

# Agregar una nueva clase para el cuadro de diálogo de confirmación
class ConfirmacionModificacionDialog(QDialog):
    def __init__(self, parent=None):
        super(ConfirmacionModificacionDialog, self).__init__(parent)
        uic.loadUi('interfaz/validar.ui', self)  # Reemplaza 'confirmacion_modificacion.ui' con el nombre de tu archivo .ui

        # Conecta los botones a las funciones correspondientes
        self.aceptar_button.clicked.connect(self.accept)
        self.cancelar_button.clicked.connect(self.reject)

    def accept_and_close(self):
        self.accept()
        self.close()
class VentanaVerificarContrasena(QDialog):
    def __init__(self, parent=None):
        super(VentanaVerificarContrasena, self).__init__(parent)
        uic.loadUi('interfaz/verificar.ui', self)

        # Conecta la función verificar_contrasena al botón "Aceptar"
        self.accept_button.clicked.connect(self.verificar_contrasena)

        # Conecta la función cerrar al botón "Cancelar"
        self.cancel_button.clicked.connect(self.reject)

        # Campo de entrada de contraseña
        self.password_edit = self.findChild(QLineEdit, 'password_edit')

    def verificar_contrasena(self):
        # Lógica para verificar la contraseña (puedes personalizarla)
        contrasena_ingresada = self.password_edit.text()
        contrasena_correcta = contrasena_ingresada == 'tvip'

        if contrasena_correcta:
            self.accept()  # Acepta el diálogo y permite abrir la ventana principal
        else:
            QMessageBox.critical(self, "Error", "Contraseña incorrecta", QMessageBox.Ok)

class VentanaConfiguracion(QMainWindow):
    def __init__(self):
        super(VentanaConfiguracion, self).__init__()
        uic.loadUi('interfaz/formularioDBLucho.ui', self)

        # Conecta la función aceptar_configuracion al botón "Aceptar"
        self.accept_button.clicked.connect(self.aceptar_configuracion)

    def aceptar_configuracion(self):
        # Intenta establecer la conexión a la base de datos
        host = self.host_edit.text()
        usuario = self.usuario_edit.text()
        contrasena = self.contrasena_edit.text()
        nombre_bd = self.nombre_bd_edit.text()

        try:
            connection = mysql.connector.connect(
                host=host,
                user=usuario,
                password=contrasena,
                database=nombre_bd
            )

            if connection.is_connected():
                # Muestra un cuadro de diálogo para confirmar la modificación en la base de datos
                confirmacion_dialog = ConfirmacionModificacionDialog(self)
                if confirmacion_dialog.exec_() == QDialog.Accepted:
                    # Si el usuario acepta, continúa con la actualización de la configuración
                    print('Conexión exitosa a la base de datos!')
                    self.actualizar_configuracion_en_json(host, usuario, contrasena, nombre_bd)

                    # Cierra la ventana de configuración
                    self.close()
                else:
                    print('Modificación en la base de datos cancelada por el usuario.')

                # Cierra la conexión
                connection.close()
                print('Conexión cerrada.')

        except mysql.connector.Error as err:
            print(f'Error al conectarse a la base de datos: {err}')

    def actualizar_configuracion_en_json(self, host, usuario, contrasena, nombre_bd):
        try:
            # Leer la configuración actual desde el archivo JSON
            with open('config.json', 'r') as archivo_json:
                configuracion_actual = json.load(archivo_json)
                #print('Configuración actual antes de la actualización:', configuracion_actual)

            # Actualizar los datos en el diccionario
            configuracion_actual['DB_HOST'] = host
            configuracion_actual['DB_USER'] = usuario
            configuracion_actual['DB_PASSWORD'] = contrasena
            configuracion_actual['DB_DATABASE'] = nombre_bd

            #print('Configuración actualizada en el archivo config.json:', configuracion_actual)

            # Escribir los datos actualizados en el archivo JSON
            with open('config.json', 'w') as archivo_json:
                json.dump(configuracion_actual, archivo_json)

            print('Configuración actualizada en el archivo config.json.')

        except FileNotFoundError:
            print("El archivo de configuración no existe.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")

class VentanaLogin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Carga la interfaz de archivo.ui creado en Qt Designer
        self.window = uic.loadUi("interfaz/ventana_login.ui")

        # Carga la interfaz de login exitoso y login error
        self.ventana_exito = uic.loadUi("interfaz/ventana_login_exito.ui")
        self.ventana_error = uic.loadUi("interfaz/ventana_login_error.ui")

        # Variable para rastrear si la ventana de configuración está abierta
        self.ventana_config_abierta = False

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

        # Conecta el botón "config_server" a la función correspondiente
        self.window.config.clicked.connect(self.abrir_ventana_config)

        # Muestra la interfaz de login principal
        self.window.show()

    def abrir_ventana_config(self):
        try:
            # Verifica si la ventana ya está abierta
            if not self.ventana_config_abierta:
                # Crea una instancia de la ventana de verificación de contraseña
                ventana_verificar_contrasena = VentanaVerificarContrasena(self)

                # Abre la ventana de verificación de contraseña y verifica la contraseña
                if ventana_verificar_contrasena.exec_() == QDialog.Accepted:
                    # Si la contraseña es correcta, abre la ventana de configuración
                    self.ventana_config_abierta = True
                    self.ventana_config = VentanaConfiguracion()
                    self.ventana_config.show()

        except Exception as e:
            print(f"Error al abrir la ventana de configuración: {e}")

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
                host='192.168.100.117',
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
        print("Abriendo habitaciones...")

        try:
            # Utiliza multiprocessing.Process para ejecutar main.py en segundo plano
            main_process = Process(target=self.ejecutar_main_py)
            main_process.start()

            # Cierra la ventana actual
            print("Cerrando la ventana actual")
            self.window.close()
        except Exception as e:
            print(f"Error al abrir main.py: {e}")

    def ejecutar_main_py(self):
        try:
            subprocess.run(["python", "main.py"])
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar main.py: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ventana_login = VentanaLogin()
    sys.exit(app.exec_())
