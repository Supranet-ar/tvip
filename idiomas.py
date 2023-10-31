"""import sys
import requests
import json
from PyQt5 import QtWidgets, uic

# Cargar el archivo .ui generado por Qt Designer
qt_file = "interfaz/idiomas.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_file)

KODI_URL = 'http://192.168.100.127:8080/jsonrpc'
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

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Conectar la señal "clicked" del botón "ok" a la función de guardado y cierre
        self.ui.btn_ok.clicked.connect(self.guardar_seleccion)

    def change_language(self, language):
        if language not in LANGUAGE_MAP:
            print(f"Error: '{language}' no está soportado.")
            return

        data = {
            "jsonrpc": "2.0",
            "method": "Settings.SetSettingValue",
            "params": {
                "setting": "locale.language",
                "value": LANGUAGE_MAP[language]
            },
            "id": 1
        }

        response = requests.post(KODI_URL, headers=headers, data=json.dumps(data))
        response_json = response.json()

        if 'result' in response_json and response_json['result'] == True:
            print(f"Idioma cambiado a {language} exitosamente!")
        else:
            print(f"Error cambiando el idioma a {language}:", response_json)

    def guardar_seleccion(self):
        if self.ui.radio_ing.isChecked():
            seleccion = "INGLES"
        elif self.ui.radio_esp.isChecked():
            seleccion = "ESPAÑOL"
        elif self.ui.radio_fran.isChecked():
            seleccion = "FRANCES"
        elif self.ui.radio_alem.isChecked():
            seleccion = "ALEMAN"
        elif self.ui.radio_chin.isChecked():
            seleccion = "CHINO"
        else:
            print("No se ha seleccionado ningún idioma.")
            return

        # Cambiar el idioma en Kodi
        self.change_language(seleccion)

        # Cerrar la ventana después de guardar la selección
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())"""
