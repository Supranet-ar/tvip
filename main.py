import json
import sys
import time
import datetime
import threading
import subprocess
import concurrent.futures
import mysql.connector
import requests
import webbrowser
from PyQt5.QtCore import QtMsgType, qInstallMessageHandler
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.uic import loadUi
from base_de_datos import BaseDeDatos

#Funcion para capturar errores
def log_handler(mode, context, message):
    sys.stderr.write("%s: %s\n" % (mode, message))

qInstallMessageHandler(log_handler)

KODI_USERNAME = "Supra"
KODI_PASSWORD = "3434"

# Variable global para almacenar el puerto configurado
puerto_configurado = 8080  # Puerto predeterminado
class PanelPuerto(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("interfaz/panel_puerto.ui", self)
        self.setWindowTitle("Configurar Puerto")

        # Conecta el botón "btnEjecutarPuerto" a la función cambiar_puerto
        self.btnEjecutarPuerto.clicked.connect(self.cambiar_puerto)

        # Muestra el puerto existente en el QLabel
        self.labelPuertoExistente.setText(f"Puerto Existente: {puerto_configurado}")

    def cambiar_puerto(self):
        global puerto_configurado  # Accede a la variable global puerto_configurado
        nuevo_puerto = self.lineEditPuerto.text()

        try:
            nuevo_puerto = int(nuevo_puerto)  # Convierte el valor a un número entero
            if 1024 <= nuevo_puerto <= 65535:
                puerto_configurado = nuevo_puerto
                print(f"Nuevo puerto configurado: {puerto_configurado}")
            else:
                QtWidgets.QMessageBox.warning(self, "Advertencia", "El puerto debe estar en el rango 1024-65535.")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Advertencia", "Ingrese un número de puerto válido.")

class VentanaIdiomas(QtWidgets.QDialog):
    idioma_seleccionado = QtCore.pyqtSignal(str)
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'KodiJsonClient'
    }

    LANGUAGE_MAP = {
        "INGLES": "resource.language.en_gb",
        "ESPAÑOL": "resource.language.es_es",
        "FRANCES": "resource.language.fr_fr",
        "ALEMAN": "resource.language.de_de",
        "CHINO": "resource.language.zh_cn",
    }
    def __init__(self, ip, parent=None):
        super(VentanaIdiomas, self).__init__(parent)
        loadUi("interfaz/idiomas.ui", self)  # Asegúrate de usar la ruta correcta al archivo .ui
        self.ip = ip

        # Conectar el botón btn_ok a su slot correspondiente
        self.btn_ok.clicked.connect(self.guardar_seleccion)
        self.VentanaIdiomas = None

    def guardar_seleccion(self):
        try:
            if self.radio_ing.isChecked():
                seleccion = "INGLES"
            elif self.radio_esp.isChecked():
                seleccion = "ESPAÑOL"
            elif self.radio_fran.isChecked():
                seleccion = "FRANCES"
            elif self.radio_alem.isChecked():
                seleccion = "ALEMAN"
            elif self.radio_chin.isChecked():
                seleccion = "CHINO"
            else:
                print("No se ha seleccionado ningún idioma.")
                return

            # Cambiar el idioma en Kodi
            self.change_language(seleccion)

            # Cerrar la ventana después de guardar la selección
            self.close()

        except Exception as e:
            print(f"Error en guardar_seleccion: {e}")

    def change_language(self, language):
        if language not in self.LANGUAGE_MAP:
            print(f"Error: '{language}' no está soportado.")
            return

        kodi_url = f'http://{self.ip}:8080/jsonrpc'

        data = {
            "jsonrpc": "2.0",
            "method": "Settings.SetSettingValue",
            "params": {
                "setting": "locale.language",
                "value": self.LANGUAGE_MAP[language]
            },
            "id": 1
        }

        time.sleep(0.5)
        response = requests.post(kodi_url, headers=self.headers, data=json.dumps(data), auth=(KODI_USERNAME, KODI_PASSWORD))
        response_json = response.json()

        if 'result' in response_json and response_json['result'] == True:
            print(f"Idioma cambiado a {language} exitosamente!")
        else:
            print(f"Error cambiando el idioma a {language}:", response_json)


# Panel de control avanzado
class PanelControl(QtWidgets.QDialog):
    def __init__(self, ip, numero_habitacion, parent=None):
        super().__init__(parent)
        loadUi("interfaz/panel_control.ui", self)
        self.ip = ip
        self.setWindowTitle(f"Habitación {numero_habitacion}")
        self.btn_abrir_kodi.clicked.connect(self.abrir_interfaz_kodi)
        self.btn_estado.clicked.connect(self.mostrar_menu_actual)
        self.btn_idioma.clicked.connect(self.mostrar_ventana_idioma)
        self.perfil_actual = "normal"
        self.btn_perfil.clicked.connect(self.cargar_perfil_action)
        self.perfil_actual = self.obtener_perfil_actual()

    def mostrar_ventana_idioma(self):
        try:
            self.VentanaIdiomas = VentanaIdiomas(self.ip, self)  # Aquí pasamos la dirección IP
            self.VentanaIdiomas.show()
        except Exception as e:
            print(f"Error al inicializar o mostrar VentanaIdiomas: {e}")

    def mostrar_menu_actual(self):
        current_menu = self.parent().obtener_menu_actual(self.ip)
        if current_menu:
            QtWidgets.QMessageBox.information(self, "Informacion",
                                              f"El usuario está en el menú: {current_menu}")
        else:
            QtWidgets.QMessageBox.warning(self, "Advertencia",
                                          f"No se encontró la IP para la habitación {self.ip}")

    def abrir_interfaz_kodi(self):
        global puerto_configurado  # Accede a la variable global puerto_configurado
        url = f"http://{self.ip}:{puerto_configurado}"  # Utiliza el puerto configurado
        webbrowser.open(url)

    def cambiar_idioma(self, idioma):
        self.change_language(idioma)

    def cargar_perfil_action(self):
        if self.perfil_actual == "normal":
            self.cargar_perfil("premium")
            self.perfil_actual = "premium"
            self.btn_perfil.setText("Cambiar a perfil normal")  # Cambia el texto del botón
        else:
            self.cargar_perfil("normal")
            self.perfil_actual = "normal"
            self.btn_perfil.setText("Cambiar a perfil premium")

    def cargar_perfil(self, profile_name, prompt=False):
        url = f"http://{self.ip}:8080/jsonrpc"

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'KodiJsonClient'
        }

        data = {
            "jsonrpc": "2.0",
            "method": "Profiles.LoadProfile",
            "params": {
                "profile": profile_name,
                "prompt": prompt
            },
            "id": 1
        }

        try:
            response = requests.post(url, headers=headers, json=data, auth=(KODI_USERNAME, KODI_PASSWORD))
            response_json = response.json()

            if 'result' in response_json and response_json['result'] == "OK":
                print(f"Perfil {profile_name} cargado exitosamente en Kodi!")
            else:
                print(f"Error al cargar el perfil {profile_name} en Kodi:", response_json)
        except Exception as e:
            print(f"Error al intentar cargar el perfil en Kodi: {e}")

    def obtener_perfil_actual(self):
        url = f"http://{self.ip}:8080/jsonrpc"

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'KodiJsonClient'
        }

        data = {
            "jsonrpc": "2.0",
            "method": "Profiles.GetCurrentProfile",
            "id": 1
        }

        try:
            response = requests.post(url, headers=headers, json=data,auth=(KODI_USERNAME, KODI_PASSWORD))
            response_json = response.json()

            if 'result' in response_json:
                return response_json['result']['label']
            else:
                print(f"Error al obtener el perfil actual en Kodi:", response_json)
                return None
        except Exception as e:
            print(f"Error al intentar obtener el perfil actual en Kodi: {e}")
            return None


# Ventana de tareas
class VentanaSecundaria(QtWidgets.QMainWindow):
    guardarDatosSignal = QtCore.pyqtSignal(str)  # Definición de la señal
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

    def programar_publicidad(self):
        self.ventanaPrincipal.enviar_publicidad_a_habitaciones(self.ventanaPrincipal.ip_activas,self.ventanaPrincipal.addon_id)
        self.ventanaPrincipal.removerElemento(self.datos)

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
        self.cargar_tareas_desde_bd()

        # CONEXION DE SEÑALES EN LA VENTANA PRINCIPAL
        for button in self.scrollAreaWidgetContents.findChildren(QtWidgets.QPushButton):
            numero_habitacion = button.text()
            button.clicked.connect(lambda _, num=numero_habitacion: self.abrir_panel_control(num))

        self.btn_agregar.clicked.connect(self.ejecutarip)
        self.btn_programar.clicked.connect(self.abrirSegundaVentana)
        self.salirButton.clicked.connect(self.cerrarVentana)

        # Conecta el botón "boton_puerto" a la función abrir_panel_puerto
        self.boton_puerto.clicked.connect(self.abrir_panel_puerto)

        self.relojLabel = QtWidgets.QLabel(self)
        self.relojLabel.setGeometry(10, 10, 150, 30)
        font = QtGui.QFont("Arial", 25, QtGui.QFont.Bold)
        self.relojLabel.setFont(font)
        self.relojLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.relojLabel.setStyleSheet("background-color: #0d192b; color: white;")

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.actualizarReloj)
        self.timer.start(1000)

        self.ip_list = []
        self.buttons = []
        self.ip_number_mapping = {}

        # Inicia el hilo de actualización
        self.actualizacion_hilo = threading.Thread(target=self.actualizar_estados_botones_thread)
        self.actualizacion_hilo.daemon = True  # Hilo como demonio para que termine cuando el programa principal termine
        self.actualizacion_hilo.start()

        self.cargar_datos_habitaciones()
        self.ping_and_verify()
        self.actualizar_estados_botones()  # Agrega esta línea para actualizar los botones al iniciar

    def ejecutarip(self):
        ventana.close()
        subprocess.run(['python', 'ip.py'])

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

    def abrir_panel_puerto(self):
        panel_puerto_window = PanelPuerto()
        panel_puerto_window.exec_()

    def actualizarReloj(self):
        tiempo_actual = QtCore.QTime.currentTime()
        tiempo_formateado = tiempo_actual.toString("hh:mm:ss")
        self.relojLabel.setText(tiempo_formateado)

    def abrir_panel_control(self, numero_habitacion):
        cursor = None
        try:
            print("Intentando conectar a la base de datos...")
            cursor = self.base_datos.conexion_db.cursor()
            print("Conexión establecida. Ejecutando consulta...")

            cursor.execute("SELECT Ip FROM habitaciones WHERE Numero=%s", (numero_habitacion,))
            ip = cursor.fetchone()

            if ip:
                print(f"IP encontrada para la habitación {numero_habitacion}: {ip[0]}")
                try:
                    self.panel_control = PanelControl(ip[0], numero_habitacion, self)
                    self.panel_control.show()
                except Exception as e:
                    print("Error al inicializar o mostrar PanelControl:", str(e))

                #self.enviar_publicidad_a_habitaciones([ip[0]], self.addon_id)


            else:
                print(f"No se encontró IP para la habitación {numero_habitacion}")
                QtWidgets.QMessageBox.warning(self, "Advertencia",
                                              f"No se encontró la IP para la habitación {numero_habitacion}")

        except mysql.connector.Error as error:
            print(f"Error al conectarse a la base de datos: {error}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectarse a la base de datos:\n{error}")

        finally:
            print("Cerrando cursor...")
            if cursor:
                cursor.close()
            print("Cursor cerrado.")

    def obtener_datos_habitaciones(self):
        try:
            cursor = self.base_datos.conexion_db.cursor()

            # Asegurarse de que solo se obtengan habitaciones con IPs válidas
            query = "SELECT ip, numero FROM habitaciones WHERE ip IS NOT NULL AND ip <> ''"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()

            return data

        except mysql.connector.Error as error:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {error}")

        return []

    def cargar_datos_habitaciones(self):
        # Inicializa todos los botones como ocultos
        for i in range(1, 101):  # Rango de botones,asumiendo que tenemos 100 botones como máximo
            btn = getattr(self, f"btn{i}", None)
            if btn:
                btn.hide()

        data = self.obtener_datos_habitaciones()
        self.ip_list = [ip for ip, _ in data]
        self.buttons = [getattr(self, f"btn{i + 1}") for i in range(len(data))]
        self.ip_number_mapping = {ip: numero for ip, numero in data}

        # Muestra solo los botones con IPs válidas
        for btn in self.buttons:
            btn.show()

    def ping(self, ip, timeout=1):
        try:
            url = f'http://{ip}:8080/'
            time.sleep(0.5)
            response = requests.get(url, timeout=timeout, auth=(KODI_USERNAME, KODI_PASSWORD))
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
                time.sleep(0.5)
                response = requests.post(url, json=payload, auth=(KODI_USERNAME, KODI_PASSWORD))
                response.raise_for_status()
                if response.status_code != 200:
                    print("Error en la respuesta:", response.text)
                print(f'Addon {addon_id} ejecutado en la habitación {ip}')
            except requests.exceptions.RequestException as e:
                print(f'Error al ejecutar el addon en la habitación {ip}: {str(e)}')

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
            time.sleep(0.5)
            response = requests.post(url, json=payload, auth=(KODI_USERNAME, KODI_PASSWORD))
            response.raise_for_status()
            data = response.json()
            current_window = data["result"]["currentwindow"]["label"]
            return current_window
        except requests.exceptions.RequestException as e:
            print(f'Error al obtener el menú actual de la habitación {ip}: {str(e)}')
            return None

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
                pass

    def actualizar_estados_botones_thread(self):
        while True:
            self.actualizar_estados_botones()
            time.sleep(5)  # Espera 5 segundos antes de la próxima ejecución

    def iniciar_actualizacion_estado_menus(self):
        print("Iniciando actualización de estados de menús en segundo plano...")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.actualizar_estado_menus)
        print("Actualización de estados de menús en segundo plano iniciada.")

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
            time.sleep(0.5)
            response = requests.post(url, json=payload, auth=(KODI_USERNAME, KODI_PASSWORD))
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