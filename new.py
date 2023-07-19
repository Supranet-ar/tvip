import jsonrpc_requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cambiar Idioma de Kodi")
        self.setGeometry(100, 100, 300, 200)

        self.language_label = QLabel("Selecciona un idioma:", self)
        self.language_label.setGeometry(20, 20, 200, 30)

        self.language_combo = QComboBox(self)
        self.language_combo.setGeometry(20, 60, 200, 30)
        self.language_combo.addItem("English")
        self.language_combo.addItem("Spanish")
        # Agrega más idiomas según sea necesario
        self.language_combo.activated.connect(self.change_language)

        self.kodi = jsonrpc_requests.Server("http://localhost:8080/jsonrpc")  # Cambia la URL si Kodi utiliza un puerto o ruta diferente

    def change_language(self, index):
        selected_language = self.language_combo.itemText(index)

        if selected_language == "English":
            language_code = "en"
        elif selected_language == "Spanish":
            language_code = "es"
        # Agrega más idiomas y códigos según sea necesario

        # Cambia el idioma en Kodi
        self.set_kodi_language(language_code)

    def set_kodi_language(self, language_code):
        try:
            params = {
                "jsonrpc": "2.0",
                "method": "Settings.SetSettingValue",
                "params": {
                    "setting": "locale.language",
                    "value": language_code
                },
                "id": 1
            }
            response = self.kodi.send_request(params)
            if "error" in response:
                print("Error al cambiar el idioma en Kodi:", response["error"])
            else:
                print("Idioma cambiado exitosamente en Kodi")
        except jsonrpc_requests.TransportError as e:
            print("Error al comunicarse con Kodi:", e)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()