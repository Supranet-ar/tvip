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
        self.ventanaPrincipal.base_datos.insertar_tarea(self.datos)
        self.close()
        self.ventanaPrincipal.show()

        # Programa la llamada a enviar_publicidad_a_habitaciones en el horario especificado
        tiempo_restante = fecha - datetime.datetime.now()
        if tiempo_restante.total_seconds() > 0:
            threading.Timer(tiempo_restante.total_seconds(), self.programar_publicidad).start()

            # Función para programar el envío de publicidad
    def programar_publicidad(self):
        self.ventanaPrincipal.enviar_publicidad_a_habitaciones(self.ventanaPrincipal.ip_activas, self.ventanaPrincipal.addon_id)
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
        self.addon_id = "script.hello.world"


        # se inicializa funciones para obtener los datos de las pantallas
        self.obtener_datos_habitaciones()
        self.cargar_datos_habitaciones()
        self.ping_and_verify()
        self.cargar_tareas_desde_bd()

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
        self.relojLabel.setStyleSheet("background-color: #0d192b; color: white;")

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.actualizarReloj)
        self.timer.start(1000)

        #self.timer_estado_menus = QtCore.QTimer(self) hasta solucionar ejec segundo plano
        #self.timer_estado_menus.timeout.connect(self.actualizar_estado_menus) hasta solucionar ejec segundo plano
        #self.timer_estado_menus.start(1000)  # Actualizar cada 5000 ms (5 segundos) hasta solucionar ejec segundo plano

        # Cada minuto, verifica las tareas programadas
        #self.timer_tareas = QtCore.QTimer(self)
        #self.timer_tareas.timeout.connect(self.verificar_tareas_programadas)
        #self.timer_tareas.start(10 * 1000)  # 60 * 1000 ms = 1 minuto

        self.cargar_datos_habitaciones()
        self.ping_and_verify()
        self.actualizar_estados_botones()  # Agrega esta línea para actualizar los botones al iniciar

    # Llamada al panel para agregar una nueva pantalla
    def ejecutarip(self):
        ventana.close()
        subprocess.run(['python', 'ip.py'])

# Llamada al panel de tareas
    def abrirSegundaVentana(self):
        self.segundaVentana = VentanaSecundaria(self)
        self.segundaVentana.guardarDatosSignal.connect(self.agregarElemento)
        self.segundaVentana.show()

    def cargar_tareas_desde_bd(self):
        tareas = self.base_datos.obtener_tareas()
        for tarea in tareas:
            self.listWidget.addItem(tarea)

    def agregarElemento(self, texto):
        self.listWidget.addItem(texto)

    def removerElemento(self, tarea):
        self.base_datos.eliminar_tarea(tarea)
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
        self.ip_number_mapping = {ip: numero for ip, numero in data}

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

        return self.ip_activas

        #aself.enviar_publicidad_a_habitaciones(ip_activas)

    def enviar_publicidad_a_habitaciones(self, ip_activas, addon_id):
        for ip in ip_activas:
            url = f'http://{ip}:8080/jsonrpc'
            payload = {
                "jsonrpc": "2.0",
                "method": "Addons.ExecuteAddon",
                "params": {
                    "addonid": addon_id
                },
                "id": 1
            }

            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                if response.status_code != 200:
                    print("Error en la respuesta:", response.text)
                print(f'Addon {addon_id} ejecutado en la habitación {ip}')
            except requests.exceptions.RequestException as e:
                print(f'Error al ejecutar el addon en la habitación {ip}: {str(e)}')


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

    def actualizar_estado_menus(self):
        ip_activas = []

        for ip in self.ip_list:
            if self.ping(ip):
                current_menu = self.obtener_menu_actual(ip)
                if current_menu:
                    print(f"El usuario en la habitación {ip} está en el menú: {current_menu}")
                else:
                    print(f"No se encontró la IP para la habitación {ip}")
                ip_activas.append(ip)

        #self.enviar_publicidad_a_habitaciones(ip_activas)
        self.actualizar_estados_botones()  # Llama a la función para actualizar los botones

    def actualizar_estados_botones(self):
        for ip, button in zip(self.ip_list, self.buttons):
            if self.ping(ip):
                current_menu = self.obtener_menu_actual(ip)
                if current_menu:
                    button.setStyleSheet("background-color: green")
                    numero_habitacion = self.ip_number_mapping.get(ip, "")
                    button.setText(f"Habitación {numero_habitacion}\nEstado: {current_menu}")
                else:
                    button.setStyleSheet("background-color: green")
                    button.setText(f"Habitación {self.ip_number_mapping.get(ip, '')}")
            else:
                button.setStyleSheet("background-color: red")
                button.setText(f"Habitación {self.ip_number_mapping.get(ip, '')}")

    def ejecutar_addon(self, ip, addon_id):
        url = f"http://{ip}:8080/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "Addons.ExecuteAddon",
            "params": {
                "addonid": addon_id
            },
            "id": 1
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f'Addon {addon_id} ejecutado en la habitación {ip}')
        except requests.exceptions.RequestException as e:
            print(f'Error al ejecutar el addon en la habitación {ip}: {str(e)}')

    def verificar_tareas_programadas(self):
        try:
            cursor = self.base_datos.conexion_db.cursor()

            # Suponiendo que tienes una tabla llamada 'tareas_programadas' con las columnas 'addon_id' y 'hora_ejecucion'
            cursor.execute("SELECT addon_id FROM tareas_programadas WHERE hora_ejecucion = NOW()")
            tareas = cursor.fetchall()

            for addon_id, in tareas:
                for ip in self.ip_activas:
                    self.ejecutar_addon(ip, addon_id)

        except mysql.connector.Error as error:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectarse a la base de datos:\n{error}")

        finally:
            cursor.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())