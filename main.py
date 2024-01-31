import json
import random
import sys
import time
import datetime
import threading
import subprocess
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

import mysql.connector
import requests
import webbrowser
from PyQt5.QtCore import QtMsgType, qInstallMessageHandler, QUrl, Qt, QSize, pyqtSlot
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QMainWindow, QInputDialog, QLineEdit, QDialog, QLabel, \
    QFormLayout, QDialogButtonBox, QLayout
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal

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



class WebViewWindow(QMainWindow):
    def __init__(self, parent=None):
        super(WebViewWindow, self).__init__(parent)
        self.webview = QWebEngineView(self)
        self.webview.load(QUrl("https://www.google.com"))
        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Establecer el tamaño de la ventana del WebView
        self.resize(1359, 770)  # Puedes ajustar estos valores según tus preferencias

    def close_webview(self):
        self.close()


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
        loadUi("interfaz/idiomas.ui", self)
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
        self.setWindowTitle("Programar tareas")
        self.ventanaPrincipal = ventanaPrincipal
        uic.loadUi("interfaz/Tareas_2ventana.ui", self)

        # Señal para conectar el botón "Guardar" con la función para guardar los datos y volver a la primera ventana
        self.botonGuardar.clicked.connect(self.guardarDatos)

        # Conectamos la selección de la opción en el QComboBox a la función opcion_seleccionada
        self.comboBox.currentIndexChanged.connect(self.opcion_seleccionada)

        # Variable de instancia para almacenar la fecha y hora programada
        self.fecha_hora_programada = None

        # Se crea un temporizador para actualizar la hora cada segundo
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
        self.fecha_hora_programada = fecha  # Almacena la fecha y hora programada
        self.guardarDatosSignal.emit(self.datos)
        self.ventanaPrincipal.ventana_bd.insertar_tarea(self.datos)
        self.close()
        self.ventanaPrincipal.show()

        # Programa la llamada a enviar_publicidad_a_habitaciones o enviar_video_a_habitaciones en el horario especificado
        tiempo_restante = fecha - datetime.datetime.now()
        if tiempo_restante.total_seconds() > 0:
            if self.comboBox.currentIndex() == 0:
                threading.Timer(tiempo_restante.total_seconds(), self.programar_publicidad).start()
            elif self.comboBox.currentIndex() == 1:
                threading.Timer(tiempo_restante.total_seconds(), self.programar_video).start()

    def programar_publicidad(self):
        self.ventanaPrincipal.enviar_publicidad_a_habitaciones(self.ventanaPrincipal.ip_activas)
        self.ventanaPrincipal.removerElemento(self.datos)



    def programar_video(self):
        self.ventanaPrincipal.enviar_video_a_habitaciones(self.ventanaPrincipal.ip_activas,self.ventanaPrincipal.lista_videos)
        self.ventanaPrincipal.removerElemento(self.datos)

    def actualizarHora(self):
        hora_actual = QtCore.QDateTime.currentDateTime()
        self.dateTimeEdit.setDateTime(hora_actual)
        self.timer.timeout.disconnect(self.actualizarHora)

    def opcion_seleccionada(self, index):
        if index == 0:  # "Enviar MSJ" seleccionado
            print("Opción seleccionada: Enviar MSJ")
            self.ventanaPrincipal.enviar_publicidad_a_habitaciones(self.ventanaPrincipal.ip_activas)
        elif index == 1:  # "Enviar Video de publicidad" seleccionado
            print("Opción seleccionada: Enviar Video de publicidad")
            fecha_programada = self.dateTimeEdit.dateTime().toPyDateTime()

            # Programar la llamada a enviar_video_a_habitaciones en el horario especificado
            tiempo_restante = fecha_programada - datetime.datetime.now()
            if tiempo_restante.total_seconds() > 0:
                threading.Timer(tiempo_restante.total_seconds(), self.programar_video).start()


# Clase principal
class MainWindow(QtWidgets.QMainWindow):
    estadoActualizadoSignal = pyqtSignal()

    habitaciones_ips = []

    def __init__(self):
        super().__init__()
        loadUi("interfaz/ventana_habitaciones.ui", self)
        self.setWindowTitle("Panel de control")
        self.setFixedSize(1360, 768)
        self.base_datos = BaseDeDatos()
        self.ventana_bd = BaseDeDatos()
        self.ventana_bd.close_connection()

        self.lista_videos = [
            "smb://Server:3434@192.168.100.50/Server/publicidad.mp4",
            "smb://Server:3434@192.168.100.50/Server/publicidad10.mp4",
            "smb://Server:3434@192.168.100.50/Server/publicidad5.mp4",
            "smb://Server:3434@192.168.100.50/Server/publicidad6.mp4",
            "smb://Server:3434@192.168.100.50/Server/publicidad7.mp4",
            "smb://Server:3434@192.168.100.50/Server/publicidad3.mp4"
        ]


        # Almacena las IP activas
        self.ip_activas = []
        self.addon_id = "script.hello.world"

        # Añade el atributo video_path
        self.video_path = 'smb://192.168.100.113/videos/publicidad.mp4'

        # se inicializa funciones para obtener los datos de las pantallas
        self.obtener_datos_habitaciones()
        self.cargar_datos_habitaciones()
        self.cargar_tareas_desde_bd()

        # CONEXION DE SEÑALES EN LA VENTANA PRINCIPAL
        for button in self.scrollAreaWidgetContents.findChildren(QtWidgets.QPushButton):
            button.setStyleSheet("color: white;")

        self.btn_agregar.clicked.connect(self.ejecutarip)
        self.btn_programar.clicked.connect(self.abrirSegundaVentana)
        self.salirButton.clicked.connect(self.cerrarVentana)

        # Conecta el botón "boton_puerto" a la función abrir_panel_puerto
        self.boton_puerto.clicked.connect(self.abrir_panel_puerto)

        # conectar el boton con la funcion mostrar_webview
        self.Button_3.clicked.connect(self.mostrar_webview)

        self.webview = None  # Inicialmente, no hay WebView

        self.relojLabel = QtWidgets.QLabel(self)
        self.relojLabel.setGeometry(1130, 90, 150, 30)
        font = QtGui.QFont("Arial", 25, QtGui.QFont.Bold)
        self.relojLabel.setFont(font)
        self.relojLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.relojLabel.setStyleSheet("background-color: #00000000; color: white;")

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

        # Conectar la señal a la función de actualización de la interfaz
        #self.estadoActualizadoSignal.connect(self.actualizar_estado_boton)

        # Conectar el botón "btnConfigurarConexion" a la función configurar_conexion
        #self.btnConfigurarConexion.clicked.connect(self.configurar_conexion)

        #self.cargar_datos_habitaciones()
        #self.ping_and_verify()
        #self.actualizar_estados_botones()  # Agrega esta línea para actualizar los botones al iniciar

    def ejecutarip(self):
       # ventana.close()
        subprocess.run(['python', 'ip.py'])

    """def configurar_conexion(self):
        dialog = ConfigurarConexionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            host, user, password, database = dialog.obtener_datos_conexion()

            # Guardar los nuevos datos en el archivo de configuración
            config_data = {
                "DB_HOST": host,
                "DB_USER": user,
                "DB_PASSWORD": password,
                "DB_DATABASE": database
            }
            with open("config.json", "w") as file:
                json.dump(config_data, file)"""

    def abrirSegundaVentana(self):
            self.segundaVentana = VentanaSecundaria(self)
            self.segundaVentana.guardarDatosSignal.connect(self.agregarElemento)
            self.segundaVentana.show()

    def cargar_tareas_desde_bd(self):
        try:
            tareas = self.ventana_bd.obtener_tareas()

            if tareas is not None:
                for tarea in tareas:
                    # Convierte la tupla a una cadena de texto antes de agregarla
                    tarea_str = " ".join(map(str, tarea))
                    self.listWidget.addItem(tarea_str)
            else:
                print("No se pudieron obtener tareas desde la base de datos.")

        except mysql.connector.Error as error:
            print(f"Error al cargar tareas desde la base de datos: {error}")

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

    def mostrar_webview(self):
        webview_window = WebViewWindow(self)
        webview_window.show()

    def volver_a_principal(self):

        if self.webview:
            self.webview.deleteLater()  # Liberar recursos del WebView
            self.webview = None  # Restablecer a None
            self.hide()  # Ocultar la ventana actual
            # Abrir la ventana principal
            ventana_principal = MainWindow()
            ventana_principal.show()

    def actualizarReloj(self):
        tiempo_actual = QtCore.QTime.currentTime()
        tiempo_formateado = tiempo_actual.toString("hh:mm:ss")
        self.relojLabel.setText(tiempo_formateado)

    def abrir_panel_control(self, id_habitacion):
        cursor = None
        try:
            cursor = self.base_datos.conexion_db.cursor()

            # Modificar la consulta para obtener el número de la habitación junto con la IP
            cursor.execute("SELECT Ip, numero FROM habitaciones WHERE id_habitacion=%s", (id_habitacion,))
            resultado = cursor.fetchone()

            if resultado:
                ip, numero_habitacion = resultado

                if self.ping(ip):
                    print(f"IP encontrada para la habitación con id {id_habitacion}: {ip}")
                    try:
                        self.panel_control = PanelControl(ip, numero_habitacion, self)
                        self.panel_control.show()
                    except Exception as e:
                        print("Error al inicializar o mostrar PanelControl:", str(e))
                else:
                    # Mostrar advertencia con el número de la habitación si la IP no está disponible
                    QtWidgets.QMessageBox.warning(self, "Advertencia", f"La IP para la habitación {numero_habitacion} no está disponible.")
            else:
                print("La IP no está activa.")
        except mysql.connector.Error as error:
            print("Error en la consulta a la base de datos:", str(error))
        finally:
            if cursor:
                cursor.close()

    def obtener_datos_habitaciones(self):
        try:
            cursor = self.ventana_bd.conexion_db.cursor()

            # Asegurarse de que solo se obtengan habitaciones con IPs válidas
            query = "SELECT ip, numero FROM habitaciones WHERE ip IS NOT NULL AND ip <> ''"
            cursor.execute(query)
            self.habitaciones = cursor.fetchall()

            # Almacena las IPs en el array global habitaciones_ips
            global habitaciones_ips
            habitaciones_ips = [ip for ip, _ in self.habitaciones]

            cursor.close()

            return self.habitaciones

        except mysql.connector.Error as error:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos: {error}")

        return None

    def cargar_datos_habitaciones(self):
        # Elimina cualquier diseño existente de scrollAreaWidgetContents
        for layout in self.scrollAreaWidgetContents.findChildren(QLayout):
            layout.deleteLater()

        # Inicializa el diseño vertical para los botones
        layout = QVBoxLayout(self.scrollAreaWidgetContents)

        # Inicializa todos los botones como ocultos
        for i in range(1, 101):  # Rango de botones, asumiendo que tenemos 100 botones como máximo
            btn = getattr(self, f"btn{i}", None)
            if btn:
                btn.hide()
                try:
                    # Intenta desconectar cualquier conexión previa
                    btn.clicked.disconnect()
                except TypeError:
                    pass  # Ignora la excepción si no hay conexión previa

                btn.clicked.connect(lambda checked=False, num=i: self.abrir_panel_control(num))

                layout.addWidget(btn)
                layout.setAlignment(Qt.AlignTop)

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

    def cargar_imagen(self, filename, width=117, height=88):
        pixmap = QPixmap(filename)
        return QIcon(pixmap.scaled(width, height, aspectRatioMode=Qt.KeepAspectRatio))

    def ping_and_verify(self):
        self.ip_activas = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.ping, self.ip_list)

            for ip, button, result in zip(self.ip_list, self.buttons, results):
                if result:
                    self.ip_activas.append(ip)
                    pixmap = self.cargar_imagen('assets/boton on.png').pixmap(QSize(117, 88))
                    button.setIcon(QIcon(pixmap))
                    button.setIconSize(pixmap.size())
                    #print(f'La IP {ip} está activa.')
                else:
                    if ip in self.ip_activas:
                        self.ip_activas.remove(ip)
                    pixmap = self.cargar_imagen('assets/boton off.png').pixmap(QSize(117, 88))
                    button.setIcon(QIcon(pixmap))
                    button.setIconSize(pixmap.size())
                    #print(f'La IP {ip} no está activa.')

        return self.ip_activas

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

    def enviar_video_a_habitaciones(self, ip_activas, lista_videos):
        for video_url in lista_videos:
            for ip in ip_activas:
                url = f'http://{ip}:8080/jsonrpc'
                payload = {
                    "jsonrpc": "2.0",
                    "method": "Player.Open",
                    "params": {
                        "item": {"file": video_url}
                    },
                    "id": 1
                }

                try:
                    response = requests.post(url, json=payload, auth=(KODI_USERNAME, KODI_PASSWORD))
                    response.raise_for_status()
                    print(f'Video reproducido en la habitación {ip}')
                except requests.exceptions.RequestException as e:
                    print(f'Error al reproducir el video en la habitación {ip}: {str(e)}')
                    if hasattr(e, 'response') and e.response is not None:
                        print(f'Status Code: {e.response.status_code}')
                        print(f'Response Content: {e.response.text}')

                # Esperar 30 segundos antes de enviar el siguiente video
                time.sleep(20)

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
            response = requests.post(url, json=payload, auth=(KODI_USERNAME, KODI_PASSWORD))
            response.raise_for_status()
            data = response.json()
            current_window = data["result"]["currentwindow"]["label"]
            return current_window

        except requests.exceptions.RequestException as e:
           # print(f'Error al obtener el menú actual de la habitación {ip}: {str(e)}')
            return None

        except json.JSONDecodeError as e:
            print(f'Error al decodificar la respuesta JSON para la habitación {ip}: {str(e)}')
            return None

    def obtener_menu_actual_para_todas_las_ips(self):
        with ThreadPoolExecutor(max_workers=len(self.ip_list)) as executor:
            futures = {executor.submit(self.obtener_menu_actual, ip): ip for ip in self.ip_list}

            for future in concurrent.futures.as_completed(futures):
                ip = futures[future]
                try:
                    result = future.result()
                    # Haz algo con el resultado, por ejemplo, almacenarlo en una estructura de datos compartida
                    print(f'Menú actual para la habitación {ip}: {result}')
                except Exception as e:
                    print(f'Error al obtener el menú actual para la habitación {ip}: {str(e)}')

    def actualizar_estado_boton(self, ip):
        try:
           # print(f"Debug: Actualizando estado del botón para la IP {ip}")

            current_menu = self.obtener_menu_actual(ip)
            button = self.buttons[self.ip_list.index(ip)]

            if self.ping(ip):
                if ip in self.ip_activas:
                    pixmap = self.cargar_imagen('assets/boton on.png').pixmap(QSize(123, 93))
                else:
                    self.ip_activas.append(ip)
                    pixmap = self.cargar_imagen('assets/boton on.png').pixmap(QSize(123, 93))

                estado_texto = f"Habitación {self.ip_number_mapping.get(ip, '')}\n {current_menu}"
            else:
                if ip in self.ip_activas:
                    self.ip_activas.remove(ip)
                pixmap = self.cargar_imagen('assets/boton off.png').pixmap(QSize(123, 93))
                estado_texto = f"Habitación {self.ip_number_mapping.get(ip, '')}\n Sin conexión"

            button.setIcon(QIcon(pixmap))

            # Crear un objeto QPixmap para el pintado
            painted_pixmap = QPixmap(pixmap)

            # Dibujar texto sobre la imagen
            painter = QPainter(painted_pixmap)
            painter.setFont(QFont("Arial", 8))
            painter.setPen(QColor("white"))  # Configurar el color de la fuente
            # Centrar el texto
            text_rect = painted_pixmap.rect()
            painter.drawText(text_rect, Qt.AlignCenter, estado_texto)
            painter.end()

            # Establecer la imagen pintada como icono del botón
            button.setIcon(QIcon(painted_pixmap))

            # Forzar una actualización del diseño
            button.updateGeometry()

        except Exception as e:
            print(f"Error en la actualización del estado del botón para la IP {ip}: {e}")

    def actualizar_estados_botones_thread(self):
        while True:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(self.actualizar_estado_boton, ip): ip for ip in self.ip_list}

                # Esperar a que se completen todas las actualizaciones antes de continuar
                concurrent.futures.wait(futures)

            # Emitir la señal cuando la actualización esté completa
            self.estadoActualizadoSignal.emit()
            time.sleep(2)


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
    ventana.cargar_datos_habitaciones()
    ventana.ping_and_verify()
    sys.exit(app.exec_())