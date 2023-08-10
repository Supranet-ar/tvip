import sys
import webbrowser
import subprocess
import concurrent.futures
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.uic import loadUi
import requests
import mysql.connector
from base_de_datos import BaseDeDatos

# Panel de control avanzado
class PanelControl(QtWidgets.QDialog):
    def __init__(self, ip):
        super().__init__()
        loadUi("interfaz/panel_control.ui", self)
        self.ip = ip
        self.btn_abrir_kodi.clicked.connect(self.abrir_interfaz_kodi)

    # Interfaz web de Kodi
    def abrir_interfaz_kodi(self):
        url = f"http://{self.ip}:8080"
        webbrowser.open(url)

# Ventana de tareas
class VentanaSecundaria(QtWidgets.QMainWindow):
    guardarDatosSignal = QtCore.pyqtSignal(str)

    def __init__(self, ventanaPrincipal):
        super().__init__()
        self.setWindowTitle("Segunda Ventana")
        self.ventanaPrincipal = ventanaPrincipal
        loadUi("interfaz/Tareas_2ventana.ui", self)

        # Conectar el botón "Guardar" con la función para guardar los datos y volver a la primera ventana
        self.botonGuardar.clicked.connect(self.guardarDatos)

    # Función para guardar la tarea
    def guardarDatos(self):
        texto = self.comboBox.currentText()
        fecha = self.dateTimeEdit.dateTime().toString("dd/MM/yyyy hh:mm:ss")
        datos = f"Tarea: {texto}, Fecha: {fecha}"
        self.guardarDatosSignal.emit(datos)
        self.close()
        self.ventanaPrincipal.show()

# Clase principal
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("interfaz/ventana_habitaciones.ui", self)
        self.setWindowTitle("Panel de control")
        self.setFixedSize(793, 543)

        # Crear una instancia de la clase BaseDeDatos
        self.base_datos = BaseDeDatos()

        # Inicializar funciones para obtener los datos de las pantallas
        self.obtener_datos_habitaciones()
        self.cargar_datos_habitaciones()
        self.ping_and_verify()

        # CONEXION DE SEÑALES EN LA VENTANA PRINCIPAL
        for button in self.scrollAreaWidgetContents.findChildren(QtWidgets.QPushButton):
            numero_habitacion = button.text()
            button.clicked.connect(lambda _, num=numero_habitacion: self.abrir_panel_control(num))

        self.btn_agregar.clicked.connect(self.ejecutarip)
        self.btn_programar.clicked.connect(self.abrirSegundaVentana)
        self.salirButton.clicked.connect(self.cerrarVentana)

        self.relojLabel = QtWidgets.QLabel(self)
        self.relojLabel.setGeometry(10, 10, 150, 30)
        font = QtGui.QFont("Arial", 25, QtGui.QFont.Bold)
        self.relojLabel.setFont(font)
        self.relojLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.actualizarReloj)
        self.timer.start(1000)

# Llamada al panel para agregar una nueva pantalla
    def ejecutarip(self):
        subprocess.Popen(['python', 'ip.py'])

# Llamada al panel de tareas
    def abrirSegundaVentana(self):
        self.segundaVentana = VentanaSecundaria(self)
        self.segundaVentana.guardarDatosSignal.connect(self.agregarElemento)
        self.segundaVentana.show()

    def agregarElemento(self, texto):
        self.listWidget.addItem(texto)

    def cerrarVentana(self):
        self.close()

    def actualizarReloj(self):
        tiempo_actual = QtCore.QTime.currentTime()
        tiempo_formateado = tiempo_actual.toString("hh:mm:ss")
        self.relojLabel.setText(tiempo_formateado)

    def abrir_panel_control(self, numero_habitacion):
        try:
            cursor = self.base_datos.conexion_db.cursor()

            cursor.execute("SELECT Ip FROM habitaciones WHERE Numero=%s", (numero_habitacion,))
            ip = cursor.fetchone()

            if ip:
                self.panel_control = PanelControl(ip[0])
                self.panel_control.show()

                # Llamar a la función enviar_publicidad_a_habitaciones aquí
                self.enviar_publicidad_a_habitaciones([ip[0]])  # Enviar la IP como lista

            else:
                QtWidgets.QMessageBox.warning(self, "Advertencia", f"No se encontró la IP para la habitación {numero_habitacion}")

        except mysql.connector.Error as error:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectarse a la base de datos:\n{error}")

        finally:
            cursor.close()

    def obtener_datos_habitaciones(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="tvip"
            )
            cursor = connection.cursor()

            query = "SELECT ip, numero FROM habitaciones"
            cursor.execute(query)
            data = cursor.fetchall()

            cursor.close()
            connection.close()

            return data

        except mysql.connector.Error as error:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {error}")

        return []

    def cargar_datos_habitaciones(self):
        data = self.obtener_datos_habitaciones()
        self.ip_list = [ip for ip, _ in data]
        self.buttons = [getattr(self, f"btn{i+1}") for i in range(len(data))]

    def ping(self, ip, timeout=1):
        try:
            url = f'http://{ip}:8080/'
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def ping_and_verify(self):
        ip_activas = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.ping, self.ip_list)

            for ip, button, result in zip(self.ip_list, self.buttons, results):
                if result:
                    ip_activas.append(ip)
                    button.setStyleSheet("background-color: green")
                    print(f'La IP {ip} está activa.')
                else:
                    button.setStyleSheet("background-color: red")
                    print(f'La IP {ip} no está activa.')

        #self.enviar_publicidad_a_habitaciones(ip_activas)

    def enviar_publicidad_a_habitaciones(self, ip_activas):
        mensaje_publicidad = "¡Descuento especial por tiempo limitado! Visita nuestro sitio web."
        for ip in ip_activas:
            url = f'http://{ip}:8080/jsonrpc'
            payload = {
                "jsonrpc": "2.0",
                "method": "GUI.ShowNotification",
                "params": {
                    "title": "Publicidad",
                    "message": mensaje_publicidad
                },
                "id": 1
            }

            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                print(f'Mensaje de publicidad enviado a la habitación {ip}')
            except requests.exceptions.RequestException as e:
                print(f'Error al enviar el mensaje de publicidad a la habitación {ip}: {str(e)}')

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
