import sys
from PyQt5 import QtWidgets
import ventana_login
import ventana_login_exito
import ventana_login_error

# Crea una instancia de la aplicación
app = QtWidgets.QApplication(sys.argv)

# Crea una instancia de la ventana de inicio de sesión
window = ventana_login.VentanaLogin()

# Función para verificar el usuario y la contraseña
def verificar_usuario():
    usuario = window.usuarioLineEdit.text()
    contrasena = window.contrasenaLineEdit.text()

    if usuario == "TVO10" and contrasena == "TVOCANAL":
        mostrar_interfaz_exito()
    else:
        mostrar_interfaz_error()

# Función para mostrar la interfaz de inicio de sesión exitoso
def mostrar_interfaz_exito():
    ventana_exito = ventana_login_exito.VentanaLoginExito()  # Crea una instancia de la ventana de éxito
    ventana_exito.show()  # Muestra la ventana de éxito
    window.close()  # Cierra la ventana de inicio de sesión

# Función para mostrar la interfaz de inicio de sesión con error
def mostrar_interfaz_error():
    ventana_error = ventana_login_error.VentanaLoginError()  # Crea una instancia de la ventana de error
    ventana_error.show()  # Muestra la ventana de error
    window.close()  # Cierra la ventana de inicio de sesión

# Conecta la función verificar_usuario al botón de inicio de sesión
window.iniciarSesionButton.clicked.connect(verificar_usuario)

# Muestra la ventana de inicio de sesión
window.show()

# Inicia el bucle de eventos de la aplicación
sys.exit(app.exec_())
