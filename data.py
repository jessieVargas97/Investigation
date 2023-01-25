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
import datetime
# import DBconnection
#----------------------------------------------------------#
# dispositivos = []
# fichero = open("values.txt")
# lines = fichero.readlines()
# for l in lines:
#     dispositivos.append(l[0]) #revisar estructura archivo

#-------------------------------------------------#

#Connection to DB

# valuesList = [] # almacena macs per query

global valuesHorst
global valorAP

# # filewrite = open("values.txt","w")
# try:
# 	conexion = pymysql.connect(host='200.10.150.149',
#                              user='root',
#                              password='h8bmbfar',
#                              db='wificrowdspy')
# 	try:
# 		with conexion.cursor() as cursor:
# 			# En este caso no necesitamos limpiar ningún dato
            
# 			cursor.execute("SELECT mac, id_router, hora, avg(rssi) FROM info_horst  where hora= (select max(hora) from info_horst) group by id_router, mac , hora;")
            
# 			# Con fetchall traemos todas las filas
# 			valuesHorst = cursor.fetchall()
            
# 			cursor.execute("SELECT id_router,pos_x,pos_y from info_router;")
#             # valorAP = cursor.fetchall()

            

# 	finally:
# 		conexion.close()
        
	
# except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
# 	print("Ocurrió un error al conectar: ", e)

#values to use
# macPerQ = []
# idRouterPerQ = []
# hourDatePerQ = []
# rssivalPerQ = []

# if(len(valuesHorst)>1):
#     for i in range(len(valuesHorst)):
#         macPerQ.append(valuesHorst[i][0])
#         idRouterPerQ.append(valuesHorst[i][1])
#         hourDatePerQ.append(valuesHorst[i][2])
#         rssivalPerQ.append(valuesHorst[i][2])
# else:
#     macact = valuesHorst[0][0]
#     idRouter = valuesHorst[0][1]
#     hourDate = valuesHorst[0][2]
#     rssival = valuesHorst[0][3]


#val pos 
# if(valorAP[0] == 101):
#     x1 = valorAP[1]
#     y1 = valorAP[2]
# elif(valorAP[0] == 202):
#     x2 = valorAP[1]
#     y2 = valorAP[2]
# else:
#     x3 = valorAP[1]
#     y3 = valorAP[2]
#--------------------------INFO APS------------------------------#

Ap1_credentials = {
    'ip': "192.168.65.10", 
    'device_type': "autodetect",
    'username': "root",
    'password': "utpU3oxLrb2F"
}

Ap2_credentials = {
    'ip': "192.168.65.9", 
    'device_type': "autodetect",
    'username': "root",
    'password': "utpU3oxLrb2F"
}

Ap3_credentials = {
    'ip': "192.168.65.8", 
    'device_type': "autodetect",
    'username': "root",
    'password': "utpU3oxLrb2F"
}
mac_assoc = []
def obtenerMAC(Ap_credentials,cm):
    try:
        #change long act macs
        connect = nk.ConnectHandler(**Ap_credentials)
        # Ap_data = connect.send_command("iwinfo wlan1-1 assoc") 
        Ap_data = connect.send_command(cm) #valida cada interfaz activa en los routers    
        # lista_MAC = Ap_data.splitlines()[0:2:1]
        lista_MAC = Ap_data.splitlines() #prueba
        for i in range(len(lista_MAC)):
            listaprueba=lista_MAC[0].split(' ')[0:i+5:1]
            mac_assoc.append(listaprueba[0])    
        # listaprueba=lista_MAC[0].split(' ')
        # mac_assoc.append(listaprueba[0])
        # mac_assoc.append(" 1C:CC:D6:45:D0:B7")
        #validar si mac ya exsite en el listado
    except Exception as ex:
        print(ex)
    return mac_assoc

obtenerMAC(Ap3_credentials,"iwinfo wlan1-1 assoc")
# obtenerMAC(Ap1_credentials,"iwinfo wlan1-1 assoc")
# obtenerMAC(Ap2_credentials,"iwinfo wlan1-1 assoc")
try:
    conn = pymysql.connect(host="200.10.150.149",
                            user="root",
                            password="h8bmbfar",
                            db = "wificrowdspy")
    with conn.cursor() as cursor:
        for mac in mac_assoc:
            dataDate = datetime.datetime.now().time()
            horaVal = dataDate.strftime('%H:%M:%S')
            print(type(horaVal))
            cursor.execute("SELECT mac, id_router,hora ,avg(rssi) FROM info_horst WHERE mac = %s",(mac))
            # cursor.execute("SELECT mac, id_router,hora ,avg(rssi) FROM info_horst WHERE mac = %s or hora = %s",(mac,horaVal))
            valuesHorst = cursor.fetchall()
            cursor.execute("SELECT id_router,pos_x,pos_y from info_router;")
            valorAP = cursor.fetchall()
except(pymysql.err.OperationalError,pymysql.err.InternalError) as e:
    print(e)

finally:
    conn.commit()
    conn.close()

# values to use
macPerQ = []
idRouterPerQ = []
hourDatePerQ = []
rssivalPerQ = []

if(len(valuesHorst)>1):
    for i in range(len(valuesHorst)):
        macPerQ.append(valuesHorst[i][0])
        idRouterPerQ.append(valuesHorst[i][1])
        hourDatePerQ.append(valuesHorst[i][2])
        rssivalPerQ.append(valuesHorst[i][2])
else:
    macact = valuesHorst[0][0]
    idRouter = valuesHorst[0][1]
    hourDate = valuesHorst[0][2]
    rssival = valuesHorst[0][3]

#val pos 
if(valorAP[0] == 101):
    x1 = valorAP[1]
    y1 = valorAP[2]
elif(valorAP[0] == 202):
    x2 = valorAP[1]
    y2 = valorAP[2]
else:
    x3 = valorAP[1]
    y3 = valorAP[2]
#----------------------------VALIDAR MACs----------------------------#

# for mac in mac_assoc:
#     for macq in macPerQ:
#         if mac == macq:
#             print("Values")

#----------------------------POSICIONAMIENTO----------------------------#
# x1 = 4.80
# y1 = -3.65
# x2 = -4.80
# y2 = 3.65
# x3 = 4.80
# y3 = 3.65

x, y = var('x y')

rssi0 = 30 
d0 = 0.5

n = 1 #ant 2
wl = 2

lista_valores_rss = [50,37,41.6] #agregar multi values

#TRILATERACION
# ##modificar 
# rssiT1 = (lista_valores_rss[0]-rssi0-wl)/(10*n)
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
