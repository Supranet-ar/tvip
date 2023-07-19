from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PyQt5.uic import loadUi
import mysql.connector
import sys

app = QApplication(sys.argv)

# Carga la interfaz desde el archivo .ui
ui_file = "emergente_habitacion.ui"  # Reemplaza "nombre_de_tu_archivo.ui" con el nombre de tu archivo .ui
ui = loadUi(ui_file)

# Crea una ventana principal y establece la interfaz como su contenido
window = QMainWindow()
window.setCentralWidget(ui)

# Establece la resolución fija de la ventana
window.setFixedSize(400, 211)

# Variable para almacenar la instancia de la ventana emergente
ventana_emergente = None

# Conecta con la base de datos y obtén los valores de las habitaciones
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="tvip"
    )
    cursor = connection.cursor()

    # Ejecuta la consulta para obtener los valores de las habitaciones
    query = "SELECT numero, Ip FROM habitaciones"  # Modifica la consulta para seleccionar ambas columnas
    cursor.execute(query)
    values = cursor.fetchall()

    # Agrega los valores a la QListWidget
    for value in values:
        item = QListWidgetItem(f"Numero: {value[0]}, Ip: {value[1]}")  # Agrega ambas columnas al QListWidgetItem
        ui.listWidget.addItem(item)

except mysql.connector.Error as error:
    # Manejo de error en caso de fallo en la conexión o consulta
    print("Error al conectar con la base de datos:", error)

finally:
    # Cierra la conexión
    if connection.is_connected():
        cursor.close()
        connection.close()


# Función para abrir la ventana emergente con los datos de la habitación seleccionada
def abrir_nueva_interfaz(numero_habitacion):
    global ventana_emergente
    if ventana_emergente is None:
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="tvip"
            )
            cursor = connection.cursor()

            # Ejecuta la consulta para obtener los datos de la habitación específica
            query = f"SELECT numero, Ip FROM habitaciones WHERE numero = {numero_habitacion}"
            cursor.execute(query)
            values = cursor.fetchall()

            # Actualiza la interfaz emergente con los datos de la habitación específica
            ui.labelNumero.setText(f"Número de habitación: {values[0][0]}")
            ui.labelIP.setText(f"Dirección IP: {values[0][1]}")

            # Muestra la ventana emergente
            ventana_emergente.show()

        except mysql.connector.Error as error:
            # Manejo de error en caso de fallo en la conexión o consulta
            print("Error al conectar con la base de datos:", error)

        finally:
            # Cierra la conexión
            if connection.is_connected():
                cursor.close()
                connection.close()

    window.close()


# Conecta la señal del botón a la función abrir_nueva_interfaz
#ui.botonhab.clicked.connect(lambda: abrir_nueva_interfaz(int(ui.botonhab.text())))

# Muestra la ventana principal
window.show()

# Inicia el bucle de eventos de la aplicación
sys.exit(app.exec_())
