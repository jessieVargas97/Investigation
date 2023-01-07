import mysql.connector
from mysql.connector import MySQLConnection, Error

#check for dictionarioes values

def configuration():
    config = {
        'user':'root',
        'password':'h8bmbfar',
        'host':'200.10.150.149',
        'database':'wificrowdspy'
    }



# try:
#     connection = mysql.connector.connect(user='root', password = 'h8bmbfar', database='wificrowdspy', host = "200.10.150.149" )
# except mysql.connector.Error as err:
#     print(err)
# finally:
#     connection.close()

# cnx = mysql.connector.connect(user='root', password = 'h8bmbfar', host = "200.10.150.149", database='wificrowdspy')
# cnx.close()

try:
      dbconfig = configuration()
      conn = MySQLConnection(**dbconfig)
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM info_horst;")
except Error as e:
    print(e)
finally:
    cursor.close()
    conn.close()