from heapq import merge
from turtle import title
import netmiko as nk
import time
import numpy as np
# from numpy.linalg.norm import norma
from numpy.lib.type_check import real
import math
from sympy import *
# from sympy import var, solve
from datetime import datetime
import os 
import mysql.connector
from mysql.connector import MySQLConnection, Error
import pymysql
import datetime
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
# import DBconnection
import threading
import time
from math import dist

#--------------------------INFO APS------------------------------#
#renombrar Ap1:8 Ap2:9 Ap3:10
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
        connect = nk.ConnectHandler(**Ap_credentials)
        # Ap_data = connect.send_command("iwinfo wlan1-1 assoc") 
        Ap_data = connect.send_command(cm) #valida cada interfaz activa en los routers    
        # lista_MAC = Ap_data.splitlines()[0:2:1]
        lista_MAC = Ap_data.splitlines() 
        for i in range(len(lista_MAC)):
            # listaprueba=lista_MAC[0].split(' ')[0:i+5:1] #ant
            listaprueba=lista_MAC[i].split(' ')
            if len(listaprueba[0]) == 17:
                mac_assoc.append(listaprueba[0])
            
    except Exception as ex:
        print(ex)
    return mac_assoc

# t1 = threading.Thread(target=obtenerMAC) #to validate thread
#change it all per threading start 
obtenerMAC(Ap3_credentials,"iwinfo wlan1-1 assoc") #no need an arg per comand 
# R2 = obtenerMAC(Ap1_credentials,"iwinfo wlan1-1 assoc")
# R3 = obtenerMAC(Ap2_credentials,"iwinfo wlan1-1 assoc")

#validation per macs 

valuesHorst = []
valorAP = []

try:
    conn = pymysql.connect(host="200.10.150.147", #se cambió la BD
                            user="test",
                            password="H8bmbfar!",
                            db = "wificrowdspy")
    
    # dataDate = datetime.now() #objetos se trabajan en en tipo date
            
    # limitSupF = dataDate.strftime("%Y-%m-%d %H:%M:%S")
    # limteInf = dataDate - relativedelta(minutes=50) #se modifiocó por un margen de 10 minutos
    # limteInfF = limteInf.strftime("%Y-%m-%d %H:%M:%S")

    with conn.cursor() as cursor:
        for mac in mac_assoc:
            dataDate = datetime.now() #objetos se trabajan en en tipo date
            
            limitSupF = dataDate.strftime("%Y-%m-%d %H:%M:%S")
            limteInf = dataDate - relativedelta(minutes=50) #se modifiocó por un margen de 10 minutos
            limteInfF = limteInf.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = '5A:B3:F5:94:66:10' and fecha between '2023-02-8 15:33:00' and '2023-02-8 16:03:00' group by id_router order by id_router;")
            # cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = %s and fecha between %s and %s group by id_router order by id_router;",(mac,limteInfF,limitSupF))
            result = cursor.fetchall()
            valuesHorst.append(result)
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
rssivalPerQ = []

#obtengo la mac 
for fila in valuesHorst:
    for elemento in fila:
        rssivalPerQ.append(elemento[1])
        
#val pos change struct
for pos in valorAP:
    if(pos[0] == 101):
        x1 = pos[1]
        y1 = pos[2]
    elif(pos[0] == 202):
        x2 = pos[1]
        y2 = pos[2]
    else:
        x3 = pos[1]
        y3 = pos[2]

#----------------------------POSICIONAMIENTO----------------------------#

x, y = symbols("x y")
# x = Symbol('x')
# y = Symbol('y')

rssi0 = -41.70 #indoors model 40 test 30
d0 = 1 #ant 0.5

n = 1.54 #ant 2 later 4 
wl = 2 #ant 2

#TRILATERACION

rssiT1 = (rssi0-rssivalPerQ[0]+wl)/(10*n) #get values per query result same order?
d1 = 10**(rssiT1)*d0 
rssiT2 = (rssi0-rssivalPerQ[1]+wl)/(10*n)
d2 = 10**(rssiT2)*d0
rssiT3 = (rssi0-rssivalPerQ[2]+wl)/(10*n)
d3 = 10**(rssiT3)*d0

#test values
# d1 = 9.775
# d2 = 2.58
# d3 = 4.16

# f1 = Eq((x-x1)**2 + (y-y1)**2 - d1**2)#ant
f1 = Eq((((x-x1)**2) + ((y-y1)**2)) , (d1**2))
f2 = Eq((((x-x2)**2) + ((y-y2)**2)) , (d2**2))
f3 = Eq((((x-x3)**2) + ((y-y3)**2)) , (d3**2))

# solution = solve((f1,f2,f3),(x,y)) #revisar valor de solucion cruces
sol1 = solve((f1,f2),(x,y))
sol2 = solve((f1,f3),(x,y))
sol3 = solve((f2,f3),(x,y)) #no need

#Validar que la solucion es del sistema
list_posSol = []

#funct?
# sol1C = list(sol1)
def solSE(solution):
    lista = list(solution)
    for i in range(len(lista)):
    # for s in lista:
        if(str(i).__contains__("I") or str(i).__contains__("e")): #does not remove 2 pairs
            lista.remove(i)
            i = i - 1
    # valSearched = "I"
    # lista = filter(lambda val: valSearched in val,solution)
    return lista

#revisar
sol1C = solSE(sol1)
list_posSol.append(sol1C) #revisar
sol2C = solSE(sol2)
list_posSol.append(sol2C)
sol3C = solSE(sol3)
list_posSol.append(sol3C)
    
#test this out -> 1 pair
# SolSist = 0
# for sol in sol1C:
#     for r in sol2C:
#         if(sol in r):
#             list_posSol.append(sol)

#no lo utilizo 
# def generarVectorName(listaNameVectores):
#     listaNameVectores = []
#     for i in range(0,list_posSol):
#         listaNameVectores.append("vect"+str(i))  #cuantos retornos tengo??
    

# def generarVector(x, y):
#         name = (x,y) #retorna una tupla??
    # return name

#Validar dentro dimensiones 
listVectores = []
limSupX = 4.7
limInfX = -4.7
limSupY = 3.5 
limInfY = -3.5
for secc in list_posSol:
    coord = str(secc).split(',')
    for sol in sol1C:
        for r in sol2C:
            solstr = str(sol).split(',') #revisar
            rsstr = str(r).split(',')
            detValX = solstr[0] - rsstr[0]
            detValY = solstr[1] - rsstr[1]
            if(detValX < 0.5 and detValY < 0.5):
                # valPromX = (solstr[0] - rsstr[0])/2 #verificar si no funcion
                valPromX = np.mean(solstr[0], rsstr[0])
                valPromY = np.mean(solstr[1], rsstr[1])
                if(valPromX > limSupX or valPromX < limInfX and valPromY > limSupY or valPromY < limInfY):
                    valuetoVector = (valPromX,valPromY)
                    listVectores.append(valuetoVector) #tiene sentido??

                     

#----------------------------Distanciamiento----------------------------#

#Defino cant vectores de acuerdo MACs 
# for i in range(0,list_posSol):
#     "vect"+str(i)
#determinar proceso de segundo ubicacion 
#se determina cant de vectores segun cantidad de macs

# dist(a,b)
resultadoDistancia = []
for i in range(len(listVectores)):
    for j in range(len(listVectores)-1):
        resultadoDistancia.append(listVectores[i],listVectores[j])

#agg DB result

