import sys
import webbrowser
import subprocess
import concurrent.futures
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.uic import loadUi
import requests
import mysql.connector
from base_de_datos import BaseDeDatos
import threading
import datetime

# Panel de control avanzado
class PanelControl(QtWidgets.QDialog):
    def __init__(self, ip, numero_habitacion, parent=None):
        super().__init__(parent)
        loadUi("interfaz/panel_control.ui", self)
        self.ip = ip
        self.setWindowTitle(f"Habitación {numero_habitacion}")
        self.btn_abrir_kodi.clicked.connect(self.abrir_interfaz_kodi)
        self.btn_estado.clicked.connect(self.mostrar_menu_actual)

    def mostrar_menu_actual(self): #metodo para mostrar menu actual del usuario
            current_menu = self.parent().obtener_menu_actual(self.ip)
            if current_menu:
                QtWidgets.QMessageBox.information(self, "Informacion",
                                                  f"El usuario esta en el menu: {current_menu}")
            else:
                QtWidgets.QMessageBox.warning(self, "Advertencia",
                                              f"No se encontro la IP para la habitacion {self.ip}")
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

        # Señal para conectar el botón "Guardar" con la función para guardar los datos y volver a la primera ventana
        self.botonGuardar.clicked.connect(self.guardarDatos)

        # se crea un temporizador para actualizar la hora cada segundo
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.actualizarHora)
        self.timer.start(1000)  # Actualizar cada 1000 ms (1 segundo)

    # Función para guardar la tarea
    def guardarDatos(self):
        texto = self.comboBox.currentText()
        fecha = self.dateTimeEdit.dateTime().toPyDateTime()
        hora = fecha.hour
        minutos = fecha.minute
        segundos = fecha.second
        self.datos = f"Tarea: {texto}, Hora: {hora:02d}:{minutos:02d}:{segundos:02d}"
        self.guardarDatosSignal.emit(self.datos)
        self.close()
        self.ventanaPrincipal.show()

        # Programa la llamada a enviar_publicidad_a_habitaciones en el horario especificado
        tiempo_restante = fecha - datetime.datetime.now()
        if tiempo_restante.total_seconds() > 0:
            threading.Timer(tiempo_restante.total_seconds(), self.programar_publicidad).start()

    # Función para programar el envío de publicidad
    def programar_publicidad(self):
        self.ventanaPrincipal.enviar_publicidad_a_habitaciones(self.ventanaPrincipal.ip_activas)
        self.ventanaPrincipal.removerElemento(self.datos)

    # función para actualizar la hora en el QDateTimeEdit
    def actualizarHora(self):
        hora_actual = QtCore.QDateTime.currentDateTime()
        self.dateTimeEdit.setDateTime(hora_actual)
        self.timer.timeout.disconnect(self.actualizarHora)

# Clase principal
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("interfaz/ventana_habitaciones.ui", self)
        self.setWindowTitle("Panel de control")
        self.setFixedSize(793, 543)

        # se crea una instancia de la clase BaseDeDatos
        self.base_datos = BaseDeDatos()

        # Almacena las IP activas
        self.ip_activas = []

        # se inicializa funciones para obtener los datos de las pantallas
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

    def removerElemento(self, tarea):
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            if item.text() == tarea:
                self.listWidget.takeItem(index)
                break

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
                self.panel_control = PanelControl(ip[0], numero_habitacion, self)
                self.panel_control.show()

                self.enviar_publicidad_a_habitaciones([ip[0]])

            else:
                QtWidgets.QMessageBox.warning(self, "Advertencia",
                                              f"No se encontró la IP para la habitación {numero_habitacion}")

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

            # Asegurarse de que solo se obtengan habitaciones con IPs válidas
            query = "SELECT ip, numero FROM habitaciones WHERE ip IS NOT NULL AND ip <> ''"
            cursor.execute(query)
            data = cursor.fetchall()

            cursor.close()
            connection.close()

            return data

        except mysql.connector.Error as error:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {error}")

        return []


    def cargar_datos_habitaciones(self):
        # Inicializa todos los botones como ocultos
        for i in range(1, 101):  #Rango de botones,asumiendo que tenemos 100 botones como máximo
            btn = getattr(self, f"btn{i}", None)
            if btn:
                btn.hide()

        data = self.obtener_datos_habitaciones()
        self.ip_list = [ip for ip, _ in data]
        self.buttons = [getattr(self, f"btn{i+1}") for i in range(len(data))]

        # Muestra solo los botones con IPs válidas
        for btn in self.buttons:
            btn.show()


    def ping(self, ip, timeout=1):
        try:
            url = f'http://{ip}:8080/'
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def ping_and_verify(self):
        self.ip_activas = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.ping, self.ip_list)

            for ip, button, result in zip(self.ip_list, self.buttons, results):
                if result:
                    self.ip_activas.append(ip)
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


    #funcion para obtener el menu actual del usuario
    def obtener_menu_actual(self, ip):
        url = f"http://{ip}:8080/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "GUI.GetProperties",
            "params": {
                "properties": ["currentwindow"]
            },
            "id": 1
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            current_window = data["result"]["currentwindow"]["label"]
            return current_window
        except requests.exceptions.RequestException as e:
            print(f'Error al obtener el menú actual de la habitación {ip}: {str(e)}')
            return None

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())