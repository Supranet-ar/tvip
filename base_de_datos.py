import json

import mysql.connector


# Base de datos local
import mysql.connector

class BaseDeDatos:
    def __init__(self, config_file="config.json"):
        self.connection = None
        self.config_file = config_file
        self.load_config()
        self.conexion_db = self.conectar_db()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                config_data = json.load(file)
                self.DB_HOST = config_data.get("DB_HOST", "")
                self.DB_USER = config_data.get("DB_USER", "")
                self.DB_PASSWORD = config_data.get("DB_PASSWORD", "")
                self.DB_DATABASE = config_data.get("DB_DATABASE", "")
        except FileNotFoundError:
            print(f"Archivo de configuración '{self.config_file}' no encontrado.")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el archivo de configuración '{self.config_file}': {e}")

    def conectar_db(self):
        try:
            conexion_db = mysql.connector.connect(
                host=self.DB_HOST,
                user=self.DB_USER,
                password=self.DB_PASSWORD,
                database=self.DB_DATABASE
            )
            print("Conexión a la base de datos exitosa.")
            return conexion_db
        except mysql.connector.Error as error:
            print(f"Error al conectar con la base de datos: {error}")
            return None

    def close_connection(self):
        if self.connection:
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

    def insertar_tarea(self, tarea):
        try:
            cursor = self.conexion_db.cursor()

            insert_query = "INSERT INTO tareas (descripcion) VALUES (%s)"
            cursor.execute(insert_query, (tarea,))
            self.conexion_db.commit()
            print("Tarea guardada en la base de datos")
            return True
        except mysql.connector.Error as error:
            print(f"Error al insertar tarea en la base de datos: {error}")
            return False

    def eliminar_tarea(self, tarea):
        try:
            cursor = self.conexion_db.cursor()

            delete_query = "DELETE FROM tareas WHERE descripcion = %s"
            cursor.execute(delete_query, (tarea,))
            self.conexion_db.commit()
            print("Tarea eliminada en la base de datos")
            return True
        except mysql.connector.Error as error:
            print(f"Error al eliminar tarea de la base de datos: {error}")
        finally:
            return False

    def obtener_tareas(self):
        try:
            cursor = self.conexion_db.cursor()
            cursor.execute("SELECT * FROM tareas")
            tareas = cursor.fetchall()
            cursor.close()
            return tareas

        except mysql.connector.Error as error:
            print(f"Error al obtener tareas desde la base de datos: {error}")
            return []  # Devuelve una lista vacía en caso de error