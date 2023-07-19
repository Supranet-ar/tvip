import ping3
import concurrent.futures
import requests
import threading
import socket
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ventana_habitaciones.ui", self)  # Reemplaza "tu_archivo.ui" con la ruta de tu archivo .ui
        self.show()

        self.ip_list = ['192.168.100.126', '192.168.100.131', '192.168.0.3', '192.168.0.4', '192.168.0.5']
        self.buttons = [self.btn1, self.btn2, self.btn3]  # Reemplaza con los objectNames de tus botones

        self.pool = concurrent.futures.ThreadPoolExecutor()

        self.ping_and_verify()

    def ping_and_verify(self):
        ip_activas = []
        futures = []

        for ip, button in zip(self.ip_list, self.buttons):
            future = self.pool.submit(self.ping_and_verify_single, ip)
            future.ip = ip
            future.button = button
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            ip = future.ip
            button = future.button
            result = future.result()

            if result is not None:
                ip_activas.append(ip)
                button.setStyleSheet("background-color: green")
                print(f'La IP {ip} está activa.')
            else:
                button.setStyleSheet("background-color: blue")
                print(f'No se pudo alcanzar la IP {ip} o no está activa.')

        self.enviar_publicidad_a_habitaciones(ip_activas)

    def ping_and_verify_single(self, ip):
        if ping3.ping(ip, timeout=0.01) is not None:
            try:
                with socket.create_connection((ip, 8080), timeout=0.01):
                    return ip
            except (socket.timeout, ConnectionRefusedError):
                return None
        return None

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

#if__continuación, puedes agregar el siguiente código para iniciar la aplicación Qt:

#```python
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()
