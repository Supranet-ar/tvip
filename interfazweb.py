import mysql.connector
import webbrowser

# Conectarse a la base de datos MySQL
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='tvip'
)
cursor = cnx.cursor()

# Leer las IPs de la tabla "tvip"
query = "SELECT Ip FROM habitaciones"
cursor.execute(query)
ips = cursor.fetchall()

# Abrir la interfaz web de Kodi para cada IP
for ip in ips:
    url = "http://" + ip[0] + ":8080"  # Puerto predeterminado de la interfaz web de Kodi
    webbrowser.open(url)

# Cerrar la conexión a la base de datos
cursor.close()
cnx.close()
