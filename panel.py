import sys
import webbrowser
import subprocess
import concurrent.futures
from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi
import json
import habitaciones

# Importar la clase BaseDeDatos
from base_de_datos import BaseDeDatos

# CREACION DE LA APLICACION
app = QtWidgets.QApplication(sys.argv)

# FUNCION ON_CLOSE PARA CERRAR ADECUADAMENTE CONEXION ABIERTA A LA BD
def on_close():
    if 'base_datos' in locals():
        base_datos.close_connection()

# DEFINICION DE LA CLASE PANELCONTROL
class PanelControl(QtWidgets.QDialog):
    def __init__(self, ip):
        super().__init__()
        loadUi("panel_control.ui", self)

        self.ip = ip

        self.btn_abrir_kodi.clicked.connect(self.abrir_interfaz_kodi)

    # FUNCION ABRIR_INTERFAZ_KODI
    def abrir_interfaz_kodi(self):
        url = f"http://{self.ip}:8080"
        webbrowser.open(url)

# DEFINCION DE LA CLASE MAINWINDOW, SUBCLASE QUE HEREDA CIERTAS CARACTERISTICAS DE HABITACIONES.MAINWINDOW
class MainWindow(habitaciones.MainWindow):  # Heredar de habitaciones.MainWindow
    def __init__(self):
        super().__init__()
        # Crear una instancia de la clase BaseDeDatos
        self.base_datos = BaseDeDatos()

        # CONEXION DE SEÑALES A LOS BOTONES DE LA VENTANA PRINCIPAL
        # Conectar la señal "clicked" de los botones en el QScrollArea para abrir la ventana de panel de control
        for button in self.scrollAreaWidgetContents.findChildren(QtWidgets.QPushButton):
            numero_habitacion = button.text()
            button.clicked.connect(lambda _, num=numero_habitacion: self.abrir_panel_control(num))

    # FUNCION ABRIR_PANEL_CONTROL
    def abrir_panel_control(self, numero_habitacion):
        try:
            cursor = self.base_datos.conexion_db.cursor()

            cursor.execute("SELECT Ip FROM habitaciones WHERE Numero=%s", (numero_habitacion,))
            ip = cursor.fetchone()

            if ip:
                self.panel_control = PanelControl(ip[0])
                self.panel_control.show()
            else:
                QtWidgets.QMessageBox.warning(self, "Advertencia", f"No se encontró la IP para la habitación {numero_habitacion}")

        except mysql.connector.Error as error:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al conectarse a la base de datos:\n{error}")

        finally:
            cursor.close()

    # FUNCION ENVIAR_PUBLICIDAD_A_HABITACIONES
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
                response = subprocess.run(
                    ['curl', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', f'{json.dumps(payload)}', url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                response_data = response.stdout.decode('utf-8')

                if response.returncode == 0 and "result" in response_data and "Notification" in response_data:
                    print(f'Mensaje de publicidad enviado a la habitación {ip}')
                else:
                    print(f'Error al enviar el mensaje de publicidad a la habitación {ip}: {response_data}')

            except Exception as e:
                print(f'Error al enviar el mensaje de publicidad a la habitación {ip}: {str(e)}')

    # FUNCION HACER PING Y ENVIAR MSJ
    def ping_and_send_message(self):
        ip_activas = []

        # Hacer ping a las habitaciones
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.ping, self.ip_list)

            for ip, button, result in zip(self.ip_list, self.buttons, results):
                if result:
                    ip_activas.append(ip)
                    # Cambiar el color del botón a verde si está activo
                    button.setStyleSheet("background-color: green")
                    print(f'La IP {ip} está activa.')
                else:
                    # Cambiar el color del botón a rojo si no está activo
                    button.setStyleSheet("background-color: red")
                    print(f'La IP {ip} no está activa.')

        # Enviar mensaje de publicidad a las habitaciones activas (Desactivado temporalmente)
        #self.enviar_publicidad_a_habitaciones(ip_activas)

# BLOQUE PRINCIPAL DEL PROGRAMA
if __name__ == "__main__":
    window = MainWindow()

    app.aboutToQuit.connect(on_close)

    window.show()

    # Ejecutar ping_and_send_message después de mostrar la ventana
    window.ping_and_send_message()

    sys.exit(app.exec_())
