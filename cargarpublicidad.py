import sys
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
import shutil

class FileTransferApp(QDialog):
    def __init__(self):
        super(FileTransferApp, self).__init__()
        loadUi("interfaz/publicidad.ui", self)

        self.btn_examinar.clicked.connect(self.browse_file)
        self.btn_transferir.clicked.connect(self.transfer_file)

        # Eliminamos la conexión con el botón de destino
        # self.btn_destino.clicked.connect(self.browse_destination)

        # Configuramos la dirección estática
        self.static_destination_folder = r"\\192.168.100.50\Server"

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar video", "", "Archivos de video (*.mp4)")
        self.lineEdit.setText(file_path)

    def transfer_file(self):
        source_file = self.lineEdit.text()
        destination_folder = self.static_destination_folder  # Utilizamos la dirección estática

        if source_file and destination_folder:
            try:
                shutil.copy(source_file, destination_folder)
                QMessageBox.information(self, "Éxito", "Archivo transferido exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al transferir el archivo: {str(e)}")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un archivo antes de transferir.")

def main():
    app = QApplication(sys.argv)
    window = FileTransferApp()
    window.show()
    window.setFixedSize(400, 145)
    window.setWindowTitle("Cargar Publicidad")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
