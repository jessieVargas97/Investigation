from heapq import merge
from turtle import title
import netmiko as nk
import time
import numpy as np
# from numpy.linalg.norm import norma
from numpy.lib.type_check import real
import math
from sympy import var, solve
from datetime import datetime
import os 
import mysql.connector
from mysql.connector import MySQLConnection, Error
import pymysql

#----------------------------------------------------------#
# dispositivos = []
# fichero = open("values.txt")
# lines = fichero.readlines()
# for l in lines:
#     dispositivos.append(l[0]) #revisar estructura archivo

#-------------------------------------------------#

#Connection to DB
#method1
# config = {
#         'user':'root',
#         'password':'h8bmbfar',
#         'host':'200.10.150.149',
#         'database':'wificrowdspy'
# }

valuesList = [] # almacena macs per query

# try:
#       dbconfig = config
#       conn = MySQLConnection(**dbconfig)
#       cursor = conn.cursor()
#       cursor.execute("SELECT id_router,fecha,hora,mac,rssi FROM info_horst ORDER BY hora desc;") #check query
#       queryResults = cursor.fetchmany() #-> datatype returned
#       #store data
#       fileWrite = open("values.txt","+w") 
#       for value in queryResults:
#         fileWrite.write("value")
    
#       #posicion 
#       cursor.execute("SELECT id_router,pos_x,pos_y from info_router;")
#       datosRouters = cursor.fetchall() #--> value per router 
#       fileWrite = open("values.txt","+w") #-> change tx
#       #consultar o almacenar??
    

# except Error as e:
#     print(e)
# finally:
#     cursor.close()
#     conn.close()

#consider 5 min delay

#method2
filewrite = open("values.txt","+w")
try:
	conexion = pymysql.connect(host='200.10.150.149',
                             user='root',
                             password='h8bmbfar',
                             db='wificrowdspy')
	try:
		with conexion.cursor() as cursor:
			# En este caso no necesitamos limpiar ningún dato
			cursor.execute("SELECT id_router,fecha,hora,mac,rssi FROM info_horst ORDER BY hora desc;")
 
			# Con fetchall traemos todas las filas
			valuesHorst = cursor.fetchall()
            
			for val in valuesHorst:
				filewrite.write("".join(val))
                valuesList.append(val)

            

	finally:
		conexion.close()
        
	
except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
	print("Ocurrió un error al conectar: ", e)
filewrite.close() #revisar position
    

#--------------------------INFO APS------------------------------#

Ap1_credentials = { #-->change
    'ip': "", 
    'device_type': "autodetect",
    'username': "root",
    'password': "root"
}

Ap2_credentials = { #-->change
    'ip': "", 
    'device_type': "autodetect",
    'username': "root",
    'password': "root"
}

Ap3_credentials = { #-->change
    'ip': "", 
    'device_type': "autodetect",
    'username': "root",
    'password': "root"
}

def obtenerMAC(Ap_credentials):
    mac_assoc = []
    for mac in values:
        Ap_credentials["mac"]=mac
        try:
            connect = nk.ConnectHandler(**Ap_credentials)
            Ap_data = connect.send_command("iwinfo wlan0 assoc") #revsar interfaz 
            lista_MAC = Ap_data.splitlines()[1:2:1] #check match index per value
            Ap_data_list = lista_MAC[0].split
            mac_assoc.append(Ap_data_list[-1])
        except Exception as ex:
            print(ex)
    return mac_assoc

#----------------------------POSICIONAMIENTO----------------------------#
x1 = 4.80
y1 = -3.65
x2 = -4.80
y2 = 3.65
x3 = 4.80
y3 = 3.65

x, y = var('x y')

rssi0 = 30 
d0 = 0.5

n = 1 #ant 2
wl = 2

lista_valores_rss = [37,37,41.6] #query values

#TRILATERACION
# ##modificar 
# rssiT1 = 
rssiT1 = (lista_valores_rss[0]-rssi0-wl)/(10*n) 
d1 = 10**(rssiT1)*d0
rssiT2 = (lista_valores_rss[1]-rssi0-wl)/(10*n)
d2 = 10**(rssiT2)*d0
rssiT3 = (lista_valores_rss[2]-rssi0-wl)/(10*n)
d3 = 10**(rssiT3)*d0

f1 = (x-x1)**2 + (y-y1)**2 - d1**2
f2 = (x-x2)**2 + (y-y2)**2 - d2**2
f3 = (x-x3)**2 + (y-y3)**2 - d3**2

solution = solve((f1,f2,f3),(x,y)) #revisar valor de solucion cruces

if(("I" in str(solution[0][0])) or ("I" in str(solution[0][1]))):
    cx = str(solution[0][0])[0:-2]
    cx= float(cx)
    cy = float(solution[0][1])
    coorx = round(cx, 2)
    coory = round(cy, 2)
    print(cx)
else: 
                cx = float(solution[0][0])
                cy = float(solution[0][1])
                coorx = round(cx, 2)
                coory = round(cy, 2)

#Actualizando Posicion en la base de datos
datos2={
                "PosicionX": coorx,
                "PosicionY": coory,
            }
print("Coordenadas : ("+coorx+","+coory+")")

#----------------------------Distanciamiento----------------------------#

#define dos vectores
a = np.array ([2, 6, 7, 7, 5, 13, 14, 17, 11, 8])
b = np.array ([3, 5, 5, 3, 7, 12, 13, 19, 22, 7])

#calcular la distancia euclidiana entre los dos vectores 
# norma(ab)

# if __name__ == 'main':
