import sys
import webbrowser
import mysql.connector

class PanelControl:
    def __init__(self, ip):
        self.ip = ip

    def abrir_interfaz_kodi(self):
        url = f"http://{self.ip}:8080"
        webbrowser.open(url)

def abrir_interfaz_kodi(numero_habitacion):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='tvip'
        )

        cursor = connection.cursor()

        cursor.execute("SELECT Ip FROM habitaciones WHERE Numero=%s", (numero_habitacion,))
        ip = cursor.fetchone()

        if ip:
            panel_control = PanelControl(ip[0])
            panel_control.abrir_interfaz_kodi()
        else:
            print(f"No se encontró la IP para la habitación {numero_habitacion}")

    except mysql.connector.Error as error:
        print(f"Error al conectarse a la base de datos: {error}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    if len(sys.argv) != 2:
        print("Uso: python nombre_archivo.py [numero_habitacion]")
        sys.exit(1)

    numero_habitacion = sys.argv[1]
    abrir_interfaz_kodi(numero_habitacion)

if __name__ == "__main__":
    main()
