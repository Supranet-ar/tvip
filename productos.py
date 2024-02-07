import os
import shutil
import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QTableWidgetItem, QMessageBox, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QDialogButtonBox, QDialog

class ImageInputDialog(QDialog):
    def __init__(self, parent=None):
        super(ImageInputDialog, self).__init__(parent)
        self.setWindowTitle("Ingresar Datos del Producto")
        self.layout = QVBoxLayout(self)

        self.label_precio = QLabel("Precio:", self)
        self.lineEdit_precio = QLineEdit(self)
        self.layout.addWidget(self.label_precio)
        self.layout.addWidget(self.lineEdit_precio)

        self.label_descripcion = QLabel("Descripción:", self)
        self.lineEdit_descripcion = QLineEdit(self)
        self.layout.addWidget(self.label_descripcion)
        self.layout.addWidget(self.lineEdit_descripcion)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("interfaz/cargar_product.ui", self)
        self.pushButton.clicked.connect(self.seleccionar_imagen)
        self.imagen_label = QLabel(self)
        self.imagen_label.setGeometry(400, 130, 500, 200)
        self.imagen_label.setScaledContents(True)

        self.tableWidget.setColumnWidth(0, 180)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 200)
        self.tableWidget.setColumnWidth(3, 300)
        self.tableWidget.setColumnWidth(4, 100)
        self.tableWidget.setColumnWidth(5, 100)  # Nueva columna para el precio
        self.tableWidget.setColumnWidth(6, 100)  # Nueva columna para la descripción
        self.tableWidget.verticalHeader().setVisible(False)
        self.db_connection = mysql.connector.connect(
            host="192.168.100.117",
            user="tvip",
            password="3434",
            database="tvip"
        )

        self.actualizar_tableWidget()
        self.tableWidget.cellClicked.connect(self.cell_clicked)

    def seleccionar_imagen(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "",
                                                  "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.gif)",
                                                  options=options)
        if filename:
            input_dialog = ImageInputDialog(self)
            if input_dialog.exec_() == QDialog.Accepted:
                try:
                    precio = float(input_dialog.lineEdit_precio.text())
                except ValueError:
                    QMessageBox.critical(self, "Error", "Ingrese un precio válido.")
                    return
                descripcion = input_dialog.lineEdit_descripcion.text()

                pixmap = QPixmap(filename)
                self.imagen_label.setPixmap(pixmap)
                self.imagen_label.show()

                nombre_archivo = filename.split("/")[-1]
                ruta_archivo = filename

                try:
                    cursor = self.db_connection.cursor()
                    insert_query = "INSERT INTO productos (product_name, image_url, precio, status, descripcion) VALUES (%s, %s, %s, %s, %s)"
                    data = (nombre_archivo, ruta_archivo, precio, "activo", descripcion)
                    cursor.execute(insert_query, data)
                    self.db_connection.commit()
                    cursor.close()
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Error", f"Error al insertar el producto en la base de datos: {err}")

                self.actualizar_tableWidget()

    def actualizar_tableWidget(self):
        cursor = self.db_connection.cursor()
        select_query = "SELECT * FROM productos"
        cursor.execute(select_query)
        productos = cursor.fetchall()
        self.tableWidget.setRowCount(0)

        for producto in productos:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            for column, data in enumerate(producto):
                if column == 3:
                    continue  # Saltar la columna 3 (URL de la imagen)
                if column == 4:
                    column += 2  # Mover el precio y la descripción dos columnas a la derecha
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_position, column, item)

            # Agregar miniaturas de las imágenes en la última columna
            miniatura_label = QLabel()
            miniatura_label.setScaledContents(True)
            url_imagen = producto[2]  # Obtenemos la URL de la imagen directamente de la consulta
            pixmap = QPixmap(url_imagen)
            altura_deseada = 150  # Ajusta la altura deseada
            pixmap = pixmap.scaledToHeight(altura_deseada)
            miniatura_label.setPixmap(pixmap)
            self.tableWidget.setCellWidget(row_position, 3, miniatura_label)
            self.tableWidget.setRowHeight(row_position, altura_deseada)

            # Crear botón con estado activo
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(0)

            button_spacer1 = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
            button_layout.addItem(button_spacer1)
            carpeta_origen = r"\\192.168.100.50\Server\IMG_PRODUCTOS"
            button = QPushButton("Activo" if os.path.exists(os.path.join(carpeta_origen, producto[1])) else "Inactivo",
                                 self)
            button.setMaximumSize(100, 50)
            if button.text() == "Inactivo":
                button.setStyleSheet("background-color: red; color: white;")
            else:
                button.setStyleSheet("background-color: rgb(12, 81, 73); color: white;")
            button.setCheckable(True)
            button_layout.addWidget(button)

            button_spacer2 = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
            button_layout.addItem(button_spacer2)

            button.clicked.connect(lambda _, row=row_position, btn=button: self.toggle_estado(row, btn))
            self.tableWidget.setCellWidget(row_position, 4, QWidget(self))
            self.tableWidget.cellWidget(row_position, 4).setLayout(button_layout)

    def cell_clicked(self, row, column):
        if column == 1:  # Se hizo clic en la columna 1
            self.eliminar_producto(row, column)
        elif column == 3:  # Se hizo clic en la columna 3
            url_imagen = self.tableWidget.item(row, 2).text()
            pixmap = QPixmap(url_imagen)
            self.mostrar_imagen(pixmap)

    def eliminar_producto(self, row, column):
        respuesta = QMessageBox.question(self, 'Eliminar producto',
                                         '¿Estás seguro de que quieres eliminar este producto?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            id_producto = self.tableWidget.item(row, 0).text()
            cursor = self.db_connection.cursor()
            delete_query = "DELETE FROM productos WHERE id = %s"
            cursor.execute(delete_query, (id_producto,))
            self.db_connection.commit()
            cursor.close()
            self.actualizar_tableWidget()

    def toggle_estado(self, row, button):
        url_imagen = self.tableWidget.item(row, 2).text()
        nombre_archivo = os.path.basename(url_imagen)
        carpeta_origen = r"\\192.168.100.50\Server\IMG_PRODUCTOS"
        carpeta_destino = r"\\192.168.100.50\Server\IMG_PRODC_INACTIVOS"

        if os.path.exists(os.path.join(carpeta_origen, nombre_archivo)):
            shutil.move(os.path.join(carpeta_origen, nombre_archivo), carpeta_destino)
            nueva_url = os.path.join(carpeta_destino, nombre_archivo)
            QMessageBox.information(self, "Éxito", "Imagen movida exitosamente a la nueva carpeta.")
        elif os.path.exists(os.path.join(carpeta_destino, nombre_archivo)):
            shutil.move(os.path.join(carpeta_destino, nombre_archivo), carpeta_origen)
            nueva_url = os.path.join(carpeta_origen, nombre_archivo)
            QMessageBox.information(self, "Éxito", "Imagen movida exitosamente a la carpeta original.")

        # Actualizar la base de datos para reflejar el cambio de estado y de URL de la imagen
        id_producto = self.tableWidget.item(row, 0).text()
        cursor = self.db_connection.cursor()
        update_query = "UPDATE productos SET status = %s, image_url = %s WHERE id = %s"
        cursor.execute(update_query, ("activo" if button.text() == "Activo" else "inactivo", nueva_url, id_producto))
        self.db_connection.commit()
        cursor.close()
        self.actualizar_tableWidget()

        # Actualizar el texto del botón
        button.setText("Activo" if os.path.exists(os.path.join(carpeta_origen, nombre_archivo)) else "Inactivo")

    def mostrar_imagen(self, pixmap):
        self.imagen_label.setPixmap(pixmap)
        self.imagen_label.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
