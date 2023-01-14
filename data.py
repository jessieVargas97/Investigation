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
import DBconnection
#----------------------------------------------------------#
# dispositivos = []
# fichero = open("values.txt")
# lines = fichero.readlines()
# for l in lines:
#     dispositivos.append(l[0]) #revisar estructura archivo

#-------------------------------------------------#

#Connection to DB

valuesList = [] # almacena macs per query

global valuesHorst
# filewrite = open("values.txt","w")
try:
	conexion = pymysql.connect(host='200.10.150.149',
                             user='root',
                             password='h8bmbfar',
                             db='wificrowdspy')
	try:
		with conexion.cursor() as cursor:
			# En este caso no necesitamos limpiar ningún dato
			cursor.execute("SELECT mac, id_router, hora, avg(rssi) FROM info_horst  where hora= (select max(hora) from info_horst) group by id_router, mac , hora;")
 
			# Con fetchall traemos todas las filas
			valuesHorst = cursor.fetchall()
            
			# for val in valuesHorst:
                #recorrer tupla per value
                # for i in range(len(val)):
				
                # valuesList.append(val)
            

            

	finally:
		conexion.close()
        
	
except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
	print("Ocurrió un error al conectar: ", e)

#values
macact = valuesHorst[0][0]
idRouter = valuesHorst[0][1]
hourDate = valuesHorst[0][2]
rssival = valuesHorst[0][3]


# filewrite.close() #revisar position




#--------------------------INFO APS------------------------------#

Ap1_credentials = { #-->change
    'ip': "192.168.65.10", 
    'device_type': "autodetect",
    'username': "root",
    'password': "utpU3oxLrb2F"
}

Ap2_credentials = { #-->change
    'ip': "192.168.65.9", 
    'device_type': "autodetect",
    'username': "root",
    'password': "utpU3oxLrb2F"
}

Ap3_credentials = { #-->change
    'ip': "192.168.65.8", 
    'device_type': "autodetect",
    'username': "root",
    'password': "utpU3oxLrb2F"
}

def obtenerMAC(Ap_credentials):
    mac_assoc = []
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

lista_valores_rss = [rssival,37,41.6] #query values

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
