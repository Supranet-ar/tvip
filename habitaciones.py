#IMPORTACIONES#
import mysql.connector
import webbrowser
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, QTimer, QTime, Qt
from PyQt5.uic import loadUi
import sys
import os
import subprocess
import socket
import concurrent.futures

from PyQt5.uic.properties import QtWidgets


#Definición_de_la_clase_VentanaSecundaria#
class VentanaSecundaria(QMainWindow):
    guardarDatosSignal = pyqtSignal(str)

    def __init__(self, ventanaPrincipal):
        super().__init__()
        self.setWindowTitle("Segunda Ventana")
        self.ventanaPrincipal = ventanaPrincipal
        loadUi("Tareas_2ventana.ui", self)

        # Conectar el botón "Guardar" con la función para guardar los datos y volver a la primera ventana
        self.botonGuardar.clicked.connect(self.guardarDatos)

#FUNCION_GUARDARDATOS#
    def guardarDatos(self):
        texto = self.comboBox.currentText()  # Obtener el texto seleccionado del QComboBox
        fecha = self.dateTimeEdit.dateTime().toString("dd/MM/yyyy hh:mm:ss")  # Obtener la fecha y hora como texto
        datos = f"Tarea: {texto}, Fecha: {fecha}"
        self.guardarDatosSignal.emit(datos)
        self.close()
        self.ventanaPrincipal.show()

#DEFINCION DE LA CLASE MAINWINDOW#
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ventana_habitaciones.ui", self)

        # Establecer la resolución fija de la ventana
        self.setFixedSize(793, 543)

    #CONEXION DE SEÑALES EN LA VENTANA PRINCIPAL#
        # Conectar la señal "clicked" de los botones en el QScrollArea a la función para ejecutar "panel.py"
        #for button in self.scrollAreaWidgetContents.findChildren(QPushButton):
            #button.clicked.connect(self.ejecutarArchivo)

        # Conectar la señal del botón "Agregar" a una función que ejecuta el archivo "ip.py"
        self.btn_agregar.clicked.connect(self.ejecutarip)

        # Conectar la señal del botón "Programar" a una función que abre la segunda ventana
        self.btn_programar.clicked.connect(self.abrirSegundaVentana)

        # Conectar la señal del botón "SalirButton" a una función que cierra la ventana principal
        self.salirButton.clicked.connect(self.cerrarVentana)

    #CREACION DEL QLABEL PARA MOSTRAR EL RELOJ#
        self.relojLabel = QLabel(self)
        self.relojLabel.setGeometry(10, 10, 150, 30)  # Ajustar tamaño del QLabel
        font = QFont("Arial", 25, QFont.Bold)  # Ajustar el tamaño de la fuente
        self.relojLabel.setFont(font)
        self.relojLabel.setAlignment(Qt.AlignCenter)

        # Crear un temporizador para actualizar el reloj cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizarReloj)
        self.timer.start(1000)  # Actualizar cada 1000 ms (1 segundo)

        # Cargar los datos de las habitaciones desde la base de datos
        self.cargar_datos_habitaciones()

    #FUNCION EJECUTAR_ARCHIVO#
    def ejecutarArchivo(self):
        subprocess.Popen(['python', 'panel.py'])

    #FUNCION_EJECUTAR_IP#
    def ejecutarip(self):
        subprocess.Popen(['python', 'ip.py'])

    #FUNCION ABRIR_SEGUNDA_VENTANA#
    def abrirSegundaVentana(self):
        self.segundaVentana = VentanaSecundaria(self)
        self.segundaVentana.guardarDatosSignal.connect(self.agregarElemento)
        self.segundaVentana.show()

    #FUNCION_AGREGAR_ELEMENTO#
    def agregarElemento(self, texto):
        self.listWidget.addItem(texto)

    #FUNCION_CERRAR_VENTANA#
    def cerrarVentana(self):
        self.close()

    #FUNCION_ACTUALIZAR_RELOJ#
    def actualizarReloj(self):
        tiempo_actual = QTime.currentTime()
        tiempo_formateado = tiempo_actual.toString("hh:mm:ss")
        self.relojLabel.setText(tiempo_formateado)

    #FUNCION_OBTENER_DATOS_HABITACIONES#
    def obtener_datos_habitaciones(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="tvip"
            )
            cursor = connection.cursor()

            # Obtener las direcciones IP y los números de habitación de la base de datos
            query = "SELECT ip, numero FROM habitaciones"
            cursor.execute(query)
            data = cursor.fetchall()

            # Cerrar la conexión
            cursor.close()
            connection.close()

            return data

        except mysql.connector.Error as error:
            # Mostrar un mensaje de error en caso de fallo en la conexión o la consulta
            QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {error}")

        return []

    #FUNCION_CARGAR_DATOS_HABITACIONES#
    def cargar_datos_habitaciones(self):
        data = self.obtener_datos_habitaciones()

        self.ip_list = [ip for ip, _ in data]
        self.buttons = [getattr(self, f"btn{i+1}") for i in range(len(data))]


    #FUNCION PING#
    def ping(self, ip, timeout=1):
        try:
            url = f'http://{ip}:8080/'  # URL de la interfaz web de Kodi
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    #FUNCION PING_VERIFY#
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
                    button.setStyleSheet("background-color: blue")
                    print(f'La IP {ip} no está activa.')

        self.enviar_publicidad_a_habitaciones(ip_activas)

    #FUNCION_ENVIAR_PUBLICIDAD#
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
