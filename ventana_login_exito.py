import sys
from PyQt5 import QtWidgets, uic

# Carga la interfaz de archivo.ui creado en Qt Designer
app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("ventana_login_exito.ui")

# Muestra la interfaz
window.show()
sys.exit(app.exec_())
