import mysql.connector
from mysql.connector import MySQLConnection, Error
import pymysql

try:
	conexion = pymysql.connect(host='200.10.150.149',
                             user='root',
                             password='h8bmbfar',
                             db='wificrowdspy')
	
except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
	print("Ocurrió un error al conectar: ", e)

finally:
	conexion.close()
	

#check for dictionarioes values

# config = {
#         'user':'root',
#         'password':'h8bmbfar',
#         'host':'200.10.150.149',
#         'database':'wificrowdspy'
# }

# try:
#     connection = mysql.connector.connect(user='root', password = 'h8bmbfar', database='wificrowdspy', host = "200.10.150.149" )
# except mysql.connector.Error as err:
#     print(err)
# finally:
#     connection.close()

# cnx = mysql.connector.connect(user='root', password = 'h8bmbfar', host = "200.10.150.149", database='wificrowdspy')
# cnx.close()

# try:
#       dbconfig = config
#       conn = MySQLConnection(**dbconfig)
#       cursor = conn.cursor()
#       cursor.execute("SELECT * FROM info_horst;")
# except Error as e:
#     print(e)
# finally:
#     cursor.close()
#     conn.close()