from heapq import merge
from turtle import title
import netmiko as nk
import time

import DBconnection
import mysql.connector

import numpy as np
# from numpy.linalg.norm import norma
from numpy.lib.type_check import real
import math
from sympy import var, solve
from datetime import datetime
import os 

from mysql.connector import MySQLConnection, Error #revisar utilidad
DBconnection.configuration() ##checkout configuration

#----------------------------------------------------------#
#no necesario obtiene de DB
# Ap_credentials = {
#     'ip': "", 
#     'device_type': "autodetect",
#     'username': "root",
#     'password': "root"}

# verifica_Clientes_Conectados= lambda c_Conectados,ap_nombre : "No hay dispositivos conectados"+ap_nombre if c_Conectados[0]=='No' else "Los siguientes dispositivos se encuentran conectados en la red: " +ap_nombre +' '+ str(c_Conectados) 

#lectura archivo
dispositivos = []
fichero = open("values.txt")
lines = fichero.readlines()
for l in lines:
    dispositivos.append(l[0]) #revisar estructura archivo

#-------------------------------------------------#

try:
      dbconfig = DBconnection.configuration()
      conn = MySQLConnection(**dbconfig)
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM info_horst;")
except Error as e:
    print(e)
finally:
    cursor.close()
    conn.close()
# connection1 = nk.ConnectHandler(**Ap_credentials)
# Ap_data = connection1.send_command("") #cambair comando horst
# Ap_data_splitline = Ap_data.splitlines()[1:2:1]
# Ap_data_splitline2 = Ap_data.splitlines()[:1:1] #PARA SACAR EL NOMBRE DEL ACCESS POINT
# Ap_data_list=Ap_data_splitline[0].split()
# Ap_data_list2=Ap_data_splitline2[0].split()
# Ap_macaddress=Ap_data_list[-1]
# AP_name=Ap_data_list2[-1] #Se obtiene la MAC Address y el Nombre del access point

# clientes_Conectados=[]
# Ap_data = connection1.send_command("iwinfo wlan0 assoc")
# Ap_data_splitline = Ap_data.splitlines()
# for clientes in Ap_data_splitline:
#     clientes_Conectados.append(clientes.split()[0])
#     print("Se esta monitoreando el router con MAC Address "+Ap_macaddress + ' : '+ verifica_Clientes_Conectados(clientes_Conectados,AP_name))

#informacion desde la DB --> migrar
# doc_Ap_macaddress_ref = db.collection('mac_devices').document(Ap_macaddress)
# doc__Ap_macaddress_dataframe = doc_Ap_macaddress_ref.get()
# doc_coleccion=doc__Ap_macaddress_dataframe.to_dict()
# for conectado in clientes_Conectados:
#   lista_devices=doc_coleccion.get("devices")
#   for macmatch in lista_devices :
#     if conectado==macmatch:               
#       registration_token = doc_coleccion.get("token")
#       now = datetime.now()
#       #checkout DB STRUCTURE
#       datos = {
#                 "mac_device1": macmatch,
#                 "mac_ap":Ap_macaddress,
#                 "fecha": now,
#                 "token": registration_token
#                         }

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

lista_valores_rss = [37,37,41.6] #modifiocar los valores obteniodos de la peticion

#TRILATERACION
# ##modificar 
# rssiT1 = 
rssiT1 = (lista_valores_rss[0]-rssi0-wl)/(10*n) #modificar logaritmo
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
