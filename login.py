import sys
from PyQt5 import QtWidgets, uic
import subprocess


# Carga la interfaz de archivo.ui creado en Qt Designer
app = QtWidgets.QApplication(sys.argv)
window = uic.loadUi("interfaz/ventana_login.ui")

# Carga la interfaz de login exitoso y login error
ventana_exito = uic.loadUi("interfaz/ventana_login_exito.ui")
ventana_error = uic.loadUi("interfaz/ventana_login_error.ui")

# Función para verificar el usuario y la contraseña
def verificar_usuario():
    usuario = window.usuarioLineEdit.text()
    contrasena = window.contrasenaLineEdit.text()

    if usuario == "tvip" and contrasena == "1234":
        mostrar_interfaz_exito()
    else:
        mostrar_interfaz_error()

# Función para mostrar la interfaz de login exitoso
def mostrar_interfaz_exito():
    ventana_exito.show()  # Muestra la interfaz de login exitoso
    window.close()  # Cierra la interfaz de login principal

# Función para mostrar la interfaz de login error
def mostrar_interfaz_error():
    ventana_error.show()  # Muestra la interfaz de login error
    window.close()  # Cierra la interfaz de login principal

# Función para mostrar la interfaz de login
def mostrar_interfaz_login():
    ventana_error.close()  # Cierra la interfaz de login error
    window.show()  # Muestra la interfaz de login principal

# Función para cerrar la ventana
def cerrar():
    window.close()
    ventana_exito.close()
    ventana_error.close()

    # Función para abrir el archivo "panel.py"
def abrir_habitaciones():
        ventana_exito.close()
        subprocess.run(["python", "main.py"])

# Conecta la función verificar_usuario al botón de inicio de sesión
window.iniciarSesionButton.clicked.connect(verificar_usuario)

# Conecta la función cerrar_ventana al botón de salir
window.salirButton.clicked.connect(cerrar)

# Conecta la función cerrar_ventana_exito al botón "Salir" de la ventana de éxito
ventana_exito.salirButton.clicked.connect(cerrar)

# Conecta la función cerrar_ventana_error al botón "Salir" de la ventana de error
ventana_error.salirButton.clicked.connect(cerrar)

# Conecta la función mostrar_interfaz_login al botón "Intentar nuevamente" de la ventana de error
ventana_error.intentarNuevamenteButton.clicked.connect(mostrar_interfaz_login)

# Conecta la función abrir_habitaciones al botón "OK" de la ventana de éxito
ventana_exito.okButton.clicked.connect(abrir_habitaciones)

# Muestra la interfaz de login principal
window.show()
sys.exit(app.exec_())

# Muestra la interfaz
window.show()
sys.exit(app.exec_())