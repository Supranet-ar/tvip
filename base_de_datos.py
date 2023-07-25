import mysql.connector

class BaseDeDatos:
    def __init__(self):
        self.connection = None
        self.DB_HOST = 'localhost'
        self.DB_USER = 'root'
        self.DB_PASSWORD = '1234'
        self.DB_DATABASE = 'tvip'
        self.conexion_db = self.conectar_db()

    def conectar_db(self):
        try:
            conn = mysql.connector.connect(
                host=self.DB_HOST,
                user=self.DB_USER,
                password=self.DB_PASSWORD,
                database=self.DB_DATABASE
            )
            print("Conexión a la base de datos establecida.")
            return conn
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")
            return None

    def close_connection(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            print("Conexión cerrada.")

    def obtener_datos(self):
        if self.conexion_db:
            cursor = self.conexion_db.cursor()
            cursor.execute("SELECT Ip, numero FROM habitaciones")
            datos = cursor.fetchall()
            cursor.close()
            return datos
        else:
            return None

    def eliminar_ip(self, ip):
        try:
            cursor = self.conexion_db.cursor()
            query = "DELETE FROM habitaciones WHERE Ip = %s"
            values = (ip,)
            cursor.execute(query, values)
            self.conexion_db.commit()
            return True
        except mysql.connector.Error as error:
            print(f"Error al eliminar de la base de datos: {error}")
            return False

    def insertar_ip(self, ip, numero):
        try:
            cursor = self.conexion_db.cursor()
            query = "INSERT INTO habitaciones (Ip, numero) VALUES (%s, %s)"
            values = (ip, numero)
            cursor.execute(query, values)
            self.conexion_db.commit()
            return True
        except mysql.connector.Error as error:
            print(f"Error al insertar en la base de datos: {error}")
            return False

    def actualizar_ip(self, ip_actual, nueva_ip, nuevo_numero):
        try:
            cursor = self.conexion_db.cursor()
            query = "UPDATE habitaciones SET Ip = %s, numero = %s WHERE Ip = %s"
            values = (nueva_ip, nuevo_numero, ip_actual)
            cursor.execute(query, values)
            self.conexion_db.commit()
            return True
        except mysql.connector.Error as error:
            print(f"Error al actualizar en la base de datos: {error}")
            return False
