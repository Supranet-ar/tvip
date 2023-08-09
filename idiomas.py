import sys
from PyQt5 import QtWidgets, uic

# Cargar el archivo .ui generado por Qt Designer
qt_file = "interfaz/idiomas.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_file)

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Conectar la señal "clicked" del botón "ok" a la función de guardado y cierre
        self.ui.btn_ok.clicked.connect(self.guardar_seleccion)

    def guardar_seleccion(self):
        # Obtener la selección realizada
        seleccion = self.ui.combo_idiomas.currentText()

        # Realizar acciones de guardado aquí
        # Por ejemplo, imprimir la selección
        print("Selección guardada:", seleccion)

        # Cerrar la ventana después de guardar la selección
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
