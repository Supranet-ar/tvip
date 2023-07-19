import sys
from PyQt5 import QtWidgets, uic

# Carga la interfaz de archivo.ui creado en Qt Designer
app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("ventana_loginerror.ui")

# Personaliza la interfaz y agrega funcionalidad si es necesario
# Por ejemplo, puedes acceder a los elementos de la interfaz con sus nombres de objeto:
#window.button.clicked.connect(lambda: print("¡Hiciste clic en el botón!"))

# Muestra la interfaz
window.show()
sys.exit(app.exec_())
