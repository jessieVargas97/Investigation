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
        Ap_data = connect.send_command(cm) #valida cada interfaz activa en los routers    
        lista_MAC = Ap_data.splitlines() 
        for i in range(len(lista_MAC)):
            listaprueba=lista_MAC[i].split(' ')
            if len(listaprueba[0]) == 17:
                mac_assoc.append(listaprueba[0])
            
    except Exception as ex:
        print(ex)
    return mac_assoc

obtenerMAC(Ap3_credentials,"iwinfo wlan1-1 assoc")

valuesHorst = []
valorAP = []

try:
    conn = pymysql.connect(host="200.10.150.147", #se cambió la BD
                            user="test",
                            password="H8bmbfar!",
                            db = "wificrowdspy")

    with conn.cursor() as cursor:
        # for mac in mac_assoc:
        #     dataDate = datetime.now()
        #     #time lapse check in realtime scenario
        #     limitSupF = dataDate.strftime("%Y-%m-%d %H:%M:%S")
        #     limteInf = dataDate - relativedelta(minutes=10) 
        #     limteInfF = limteInf.strftime("%Y-%m-%d %H:%M:%S")
        #     cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = '5A:B3:F5:94:66:10' and fecha between '2023-02-8 15:33:00' and '2023-02-8 16:03:00' group by id_router order by id_router;")
        #     # cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = %s and fecha between %s and %s group by id_router order by id_router;",(mac,limteInfF,limitSupF))
        #     result = cursor.fetchall()
        #     valuesHorst.append(result)
        #     cursor.execute("SELECT id_router,pos_x,pos_y from info_router;")
        #     valorAP = cursor.fetchall()
        
        cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = '5A:B3:F5:94:66:10' and fecha between '2023-02-8 15:30:00' and '2023-02-8 15:35:00' group by id_router order by id_router;")
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

#obtengo el valor de RSSI   
for fila in valuesHorst:
    # if len(fila) == 3:
    if len(fila) == 2 or len(fila) == 3:
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

rssi0 = -41.70 #indoors model 40 test 30
d0 = 1 #ant 0.5

n = 1.54 #ant 2 later 4 
wl = 2

#TRILATERACION

rssiT1 = (rssi0-rssivalPerQ[0]+wl)/(10*n) 
d1 = 10**(rssiT1)*d0 
rssiT2 = (rssi0-rssivalPerQ[1]+wl)/(10*n)
d2 = 10**(rssiT2)*d0
rssiT3 = (rssi0-rssivalPerQ[2]+wl)/(10*n)
d3 = 10**(rssiT3)*d0

f1 = Eq((((x-x1)**2) + ((y-y1)**2)) , (d1**2))
f2 = Eq((((x-x2)**2) + ((y-y2)**2)) , (d2**2))
f3 = Eq((((x-x3)**2) + ((y-y3)**2)) , (d3**2))

sol1 = solve((f1,f2),(x,y))
sol2 = solve((f1,f3),(x,y))
sol3 = solve((f2,f3),(x,y)) 


#test values
# d1 = 9.775
# d2 = 2.58
# d3 = 4.16

# solution = solve((f1,f2,f3),(x,y)) #revisar SE sol 

list_posSol = []

def solSE(solution):
    lista = list(solution)
    retorno = []
    for i in range(len(lista)):
        i = i - 1
        if(str(lista[i]).__contains__("I") or str(lista[i]).__contains__("e")):
            lista.remove(lista[i])
        else:
            retorno.append(lista[i])
    return retorno

sol1C = solSE(sol1)
list_posSol.append(sol1C) 
sol2C = solSE(sol2)
list_posSol.append(sol2C)
sol3C = solSE(sol3)
list_posSol.append(sol3C)
    
def parOrdenado(lista1,lista2,lista3):
    limSupX = 4.7
    limInfX = -4.7
    limSupY = 3.5 
    limInfY = -3.5
    listVectoresf = []
    #procesamiento previo par ordenado ahorro anidaciones?    
    if not lista1 or not lista2 and not lista1 or not lista3 and not lista2 or not lista3:
            #revisar logica validaciones NO TIENE
        for v in range(len(lista2)):
            for v1 in range(len(lista3)):
                # vstr = str(v).split(',')
                # v1str = str(v1).split(',')
                # detValX = v[0] - v1[0]
                # detValY = v[1] - v1[1]
                detValX = Float(lista2[v]) - Float(lista3[v1]) #
                #corregir esto
                detValY = lista2[v+1] - lista3[v1+1]
                if(detValX < 0.5 and detValY < 0.5):
                    valPromX = np.mean(v[0], v1[0])
                    valPromY = np.mean(v[1], v1[1])
                    if(valPromX > limSupX or valPromX < limInfX and valPromY > limSupY or valPromY < limInfY):
                        valuetoVector = (valPromX,valPromY)
                        listVectoresf.append(valuetoVector)
                    # print("Check here. COMPLETE")
    return listVectoresf
        

#Validar dentro dimensiones -> Implementar funcion parOrdenado
listVectores = []
# coordperLine = [] #necesario??
# limSupX = 4.7
# limInfX = -4.7
# limSupY = 3.5 
# limInfY = -3.5
# for secc in list_posSol:
#     if(len(secc) != 0):
#         coordperLine = str(secc).split(',')
#         # coord = coordperLine
#         for sol in sol1C:
#             for r in sol2C:
#                 solstr = str(sol).split(',')
#                 rsstr = str(r).split(',')
#                 detValX = solstr[0] - rsstr[0]
#                 detValY = solstr[1] - rsstr[1]
#                 if(detValX < 0.5 and detValY < 0.5):
#                     # valPromX = (solstr[0] - rsstr[0])/2 #verificar si no funcion
#                     valPromX = np.mean(solstr[0], rsstr[0])
#                     valPromY = np.mean(solstr[1], rsstr[1])
#                     if(valPromX > limSupX or valPromX < limInfX and valPromY > limSupY or valPromY < limInfY):
#                         valuetoVector = (valPromX,valPromY)
#                         listVectores.append(valuetoVector) #tiene sentido??

listVectores.append(parOrdenado(sol1C,sol2C,sol3C))              

#----------------------------Distanciamiento----------------------------#
#check other values 
resultadoDistancia = []
for i in range(len(listVectores)):
    for j in range(len(listVectores)-1):
        resultadoDistancia.append(listVectores[i],listVectores[j])


#----------------------------Actualizar BD por posiciones----------------------------#

#agg DB result
#how to identificate per user -> MAC?? (modify query)
#table_name and attributes
#relation with the other tables
