from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('ventana_habitaciones.ui', self)

        # Conectar el botón o evento con el método para abrir el cuadro de diálogo
        self.btn_programar.clicked.connect(self.openDialog)

    def openDialog(self):
        dialog = Dialog(self)
        # Conectar la señal "accepted" del cuadro de diálogo con la función updateListView
        dialog.guardarButton.connect(self.updateListView)
        dialog.exec_()

    def updateListView(self):
        # Aquí puedes escribir el código para actualizar el ListView con los datos del cuadro de diálogo
        combo_text = self.dialog.comboBox.currentText()
        datetime = self.dialog.dateTimeEdit.dateTime().toString(Qt.ISODate)
        # Actualizar el ListView con los datos obtenidos
        # ...


# Crear una instancia de la aplicación
app = QtWidgets.QApplication(sys.argv)

# Crear una instancia de la ventana principal
window = MiVentana()

# Mostrar la ventana
window.show()

# Iniciar el bucle principal de la aplicación
sys.exit(app.exec_())
