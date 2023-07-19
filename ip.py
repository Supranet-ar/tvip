from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.uic import loadUi
import mysql.connector
import sys
import subprocess

def regresar():
    # Cierra la ventana actual
    window.close()

    # Ejecuta el archivo Python deseado
    subprocess.run(["python", "habitaciones.py"])

def insertar_ip():
    # Obtiene la IP ingresada en el QLineEdit
    ip = ui.lineEdit.text()

    # Verifica que la IP tenga 4 octetos separados por puntos
    octetos = ip.split('.')
    if len(octetos) != 4:
        QMessageBox.warning(window, "Error", "La IP debe tener 4 octetos separados por puntos.")
        return

    # Verifica que cada octeto sea un número entre 1 y 254
    for octeto in octetos:
        try:
            octeto_num = int(octeto)
            if octeto_num < 1 or octeto_num > 254:
                raise ValueError
        except ValueError:
            QMessageBox.warning(window, "Error", "Los octetos de la IP deben ser números entre 1 y 254.")
            return

    # Obtiene el número de habitación ingresado en el QLineEdit
    habitacion = ui.lineEdit_2.text()

    # Conecta con la base de datos
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="tvip"
        )
        cursor = connection.cursor()

        # Inserta la IP y el número de habitación en la tabla correspondiente
        query = "INSERT INTO habitaciones (ip, numero) VALUES (%s, %s)"
        values = (ip, habitacion)
        cursor.execute(query, values)
        connection.commit()

        # Muestra un mensaje de éxito
        QMessageBox.information(window, "Éxito", "La IP y el número de habitación se han agregado correctamente.")

        # Actualiza el QTableWidget con las IPs y números de habitación almacenados en la base de datos
        actualizar_tablewidget(cursor)

    except mysql.connector.Error as error:
        # Muestra un mensaje de error en caso de fallo en la conexión o la consulta
        QMessageBox.critical(window, "Error", f"Error al conectar con la base de datos: {error}")

    finally:
        # Cierra la conexión
        if connection.is_connected():
            cursor.close()
            connection.close()

def eliminar_ip():
    # Obtiene la fila seleccionada en el QTableWidget
    selected_row = ui.tableWidget.currentRow()

    if selected_row >= 0:
        # Obtiene la IP de la fila seleccionada
        ip = ui.tableWidget.item(selected_row, 0).text()

        # Conecta con la base de datos
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="tvip"
            )
            cursor = connection.cursor()

            # Elimina la IP de la base de datos
            query = "DELETE FROM habitaciones WHERE Ip = %s"
            values = (ip,)
            cursor.execute(query, values)
            connection.commit()

            # Muestra un mensaje de éxito
            QMessageBox.information(window, "Éxito", "La IP y el número de habitación se han eliminado correctamente.")

            # Actualiza el QTableWidget con las IPs y números de habitación almacenados en la base de datos
            actualizar_tablewidget(cursor)

        except mysql.connector.Error as error:
            # Muestra un mensaje de error en caso de fallo en la conexión o la consulta
            QMessageBox.critical(window, "Error", f"Error al conectar con la base de datos: {error}")

        finally:
            # Cierra la conexión
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        QMessageBox.warning(window, "Advertencia", "Selecciona una IP para eliminar.")

def editar_ip():
    # Obtiene la fila seleccionada en el QTableWidget
    selected_row = ui.tableWidget.currentRow()

    if selected_row >= 0:
        # Obtiene la IP y el número de habitación de la fila seleccionada
        ip = ui.tableWidget.item(selected_row, 0).text()
        habitacion = ui.tableWidget.item(selected_row, 1).text()

        # Establece los valores en los lineEdit correspondientes
        ui.lineEdit.setText(ip)
        ui.lineEdit_2.setText(habitacion)

def guardar_cambios():
    # Obtiene la fila seleccionada en el QTableWidget
    selected_row = ui.tableWidget.currentRow()

    if selected_row >= 0:
        # Obtiene la nueva IP y el nuevo número de habitación ingresados en los lineEdit
        nueva_ip = ui.lineEdit.text()
        nueva_habitacion = ui.lineEdit_2.text()

        # Conecta con la base de datos
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="tvip"
            )
            cursor = connection.cursor()

            # Actualiza la fila correspondiente en la base de datos con los nuevos valores
            query = "UPDATE habitaciones SET ip = %s, numero = %s WHERE ip = %s"
            values = (nueva_ip, nueva_habitacion, ui.tableWidget.item(selected_row, 0).text())
            cursor.execute(query, values)
            connection.commit()

            # Muestra un mensaje de éxito
            QMessageBox.information(window, "Éxito", "Los cambios se han guardado correctamente.")

            # Actualiza el QTableWidget con las IPs y números de habitación almacenados en la base de datos
            actualizar_tablewidget(cursor)

        except mysql.connector.Error as error:
            # Muestra un mensaje de error en caso de fallo en la conexión o la consulta
            QMessageBox.critical(window, "Error", f"Error al conectar con la base de datos: {error}")

        finally:
            # Cierra la conexión
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        QMessageBox.warning(window)


def actualizar_tablewidget(cursor):
    # Ejecuta la consulta para obtener todas las IPs y números de habitación almacenados
    query = "SELECT Ip, numero FROM habitaciones"
    cursor.execute(query)
    data = cursor.fetchall()

    # Limpia el contenido actual del QTableWidget
    ui.tableWidget.clearContents()
    ui.tableWidget.setRowCount(len(data))

    # Agrega las IPs y números de habitación al QTableWidget
    for row, (ip, habitacion) in enumerate(data):
        item_ip = QTableWidgetItem(ip)
        item_habitacion = QTableWidgetItem(str(habitacion))
        ui.tableWidget.setItem(row, 0, item_ip)
        ui.tableWidget.setItem(row, 1, item_habitacion)

# Crea una instancia de QApplication
app = QApplication(sys.argv)

# Carga el archivo .ui
ui = loadUi("ventana_ip.ui")

# Conecta el botón "AGREGAR" con la función insertar_ip
ui.btn_agregarbd.clicked.connect(insertar_ip)

# Conecta el botón "ELIMINAR" con la función eliminar_ip
ui.btn_limpiar.clicked.connect(eliminar_ip)

# Conecta el botón "REGRESAR" con la función regresar
ui.btn_regresar.clicked.connect(regresar)

# Conecta el QTableWidget con la función editar_ip cuando se haga clic en una celda
ui.tableWidget.cellClicked.connect(editar_ip)

# Conecta el botón "Guardar Cambios" con la función guardar_cambios
ui.btn_guardar.clicked.connect(guardar_cambios)

# Crea una ventana principal y establece la interfaz como su contenido
window = QMainWindow()
window.setCentralWidget(ui)

# Conecta con la base de datos y actualiza el QTableWidget
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="tvip"
    )
    cursor = connection.cursor()

    # Actualiza el QTableWidget con las IPs y números de habitación almacenados en la base de datos
    actualizar_tablewidget(cursor)

except mysql.connector.Error as error:
    # Muestra un mensaje de error en caso de fallo en la conexión o la consulta
    QMessageBox.critical(window, "Error", f"Error al conectar con la base de datos: {error}")

finally:
    # Cierra la conexión
    if connection.is_connected():
        cursor.close()
        connection.close()

# Establece el tamaño fijo de la ventana
window.setFixedSize(827, 553)

# Muestra la ventana
window.show()

# Inicia el bucle de eventos de la aplicación
sys.exit(app.exec_())
