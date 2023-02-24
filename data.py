from heapq import merge
from turtle import title
import netmiko as nk
import time
import numpy as np
# from numpy.linalg.norm import norma
from numpy.lib.type_check import real
from numpy import matrix
from numpy import linalg
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
    'ip': "192.168.65.8", 
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
    'ip': "192.168.65.10", 
    'device_type': "autodetect",
    'username': "root",
    'password': "utpU3oxLrb2F"
}

valorAP = []

try:

    conn = pymysql.connect(host="200.10.150.147", #se cambió la BD
                            user="test",
                            password="H8bmbfar!",
                            db = "wificrowdspy")

    with conn.cursor() as cursor:
         cursor.execute("SELECT id_router,pos_x,pos_y from info_router;")
         valorAP = cursor.fetchall()

except(pymysql.err.OperationalError,pymysql.err.InternalError) as e:
    print(e)

finally:
    conn.commit()
    conn.close()
  
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
   
mac_assoc = []

dataDate = datetime.now()
#time lapse check in realtime scenario
limteSup = dataDate #- relativedelta(hours = 95)
limitSupF = limteSup.strftime("%Y-%m-%d %H:%M:%S")
limteInf = limteSup - relativedelta(seconds=20) 
limteInfF = limteInf.strftime("%Y-%m-%d %H:%M:%S")

def obtenerMAC():
    try:
        conn = pymysql.connect(host="200.10.150.147", #se cambió la BD
                            user="test",
                            password="H8bmbfar!",
                            db = "wificrowdspy")
        with conn.cursor() as cursor:
                   
                    # cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = '5A:B3:F5:94:66:10' and fecha between '2023-02-8 16:00:00' and '2023-02-8 16:03:00' group by id_router order by id_router;")
                    cursor.execute("SELECT mac FROM info_horst WHERE fecha between %s and %s group by mac having count(distinct id_router)>2;",(limteInfF,limitSupF))
                    result = cursor.fetchall()
                    for element in result:
                        mac_assoc.append(element[0])
                     
                    
    except(pymysql.err.OperationalError,pymysql.err.InternalError) as e:
        print(e)
    finally:
        conn.commit()
        conn.close()

    return mac_assoc

obtenerMAC()


valuesHorst = []
try:

    conn = pymysql.connect(host="200.10.150.147", #se cambió la BD
                            user="test",
                            password="H8bmbfar!",
                            db = "wificrowdspy")

    with conn.cursor() as cursor:
         for mac in mac_assoc:
            #  cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = %s and fecha between %s and %s group by id_router order by id_router;",(mac,limteInfF,limitSupF))
             cursor.execute("SELECT id_router, avg(rssi) FROM info_horst WHERE mac = '1c:cc:d6:45:d0:b7'and fecha between '2023-02-22 14:20:00' and '2023-02-22 14:20:20' group by id_router order by id_router;")
             result = cursor.fetchall()
             valuesHorst.append(result)
         
except(pymysql.err.OperationalError,pymysql.err.InternalError) as e:
    print(e)

finally:
    conn.commit()
    conn.close()

# values to use
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
        

#----------------------------POSICIONAMIENTO----------------------------#
posicion =[]
rssi0 = -41.70 #indoors model 40 test 30
d0 = 1 #ant 0.5
n = 1.66 #ant 2 later 4 
wl = 0
i=0

for mac in mac_assoc:
    x, y = symbols("x y")
#TRILATERACION
    rssiT1 = (rssi0-rssivalPerQ[i]+wl)/(10*n) 
    d1 = 10**(rssiT1)*d0 
    rssiT2 = (rssi0-rssivalPerQ[i+1]+wl)/(10*n)
    d2 = 10**(rssiT2)*d0
    rssiT3 = (rssi0-rssivalPerQ[i+2]+wl)/(10*n)
    d3 = 10**(rssiT3)*d0

#max y mins
    Xmax = min(x1 + d1, x2 + d2, x3 + d3)
    Xmin = max(x1 - d1, x2 - d2, x3 - d3)
    Ymax = min(y1 + d1, y2 + d2, y3 + d3)
    Ymin = max(y1 - d1, y2 - d2, y3 - d3)
    # Solucion Min-Max
    xest = (Xmin + Xmax)/2
    yest = (Ymin + Ymax)/2
    i=i+3
    D =matrix([[2*(x3 -x1),2*(y3 -y1)],[2*(x3 -x2),2*(y3 -y2)]])
    b= matrix([(d1**2-d3**2)-(x1**2-x3**2)-(y1**2-y3**2),(d2**2-d3**2)-(x2**2-x3**2)-(y2**2-y3**2)])
    
    pos_aprox=((D.T*D).I*D.T*b.T)
    #solucion LLS   
    xest2= pos_aprox.item(0)    
    yest2= pos_aprox.item(1) 
    #combino dos soluciones LLS y min-max 

    
    P = matrix([[Xmin,Ymin],[Xmin,Ymax], [Xmax,Ymax], [Xmax,Ymin]])
    R=matrix([[x1,y1],[x2,y2],[x3,y3]])
    weights =[]
    for element in P:
        dif_distance = 0
        for ele in R:
            d = sqrt(ele.item(0)**2 +ele.item(1))**2 
            #dif_distance = dif_distance +abs(sqrt((element.item(0) - ele.item(0))**2+ (element.item(1)- ele.item(1))**2)-d)
            dif_distance = dif_distance +(sqrt((element.item(0) - ele.item(0))**2+ (element.item(1)- ele.item(1))**2)-d)**2

        weights.append(1/dif_distance)
  
    xestmext = (matrix(weights)*P[:,0]).item(0)/sum(weights)
    yestmext = (matrix(weights)*P[:,1]).item(0)/sum(weights)
    
    xaprox = (xest+xestmext)/2
    yaprox = (yest+yestmext)/2
    
    posicion.append([mac,xaprox,yaprox, xest, yest, xest2, yest2,xestmext, yestmext])

#----------------------------Actualizar BD por posiciones actuales----------------------------#

#agg DB result
#how to identificate per user -> MAC?? (modify query)
#table_name and attributes
#relation with the other tables    
if len(posicion) >0:
    try:
        conn = pymysql.connect(host="200.10.150.147", #se cambió la BD
            user="test",
            password="H8bmbfar!",
            db = "wificrowdspy")

        with conn.cursor() as cursor:
            for element in posicion:
                cursor.execute("SELECT MAC from info_device where mac=%s;", (element[0]))
                result = cursor.fetchall()
                if len(result) ==  0: 
                    cursor.execute("INSERT INTO info_device (mac,pos_x,pos_y,date_modified) VALUES (%s,%s,%s,%s);", (element[0],element[1],element[2],limteSup))
                else:
                    cursor.execute("UPDATE info_device SET pos_x =%s, pos_y=%s, date_modified=%s where mac =%s;", (element[1],element[2],limteSup,element[0]))
                conn.commit()
    except(pymysql.err.OperationalError,pymysql.err.InternalError) as e:
        print(e)

    finally:
        conn.close()


#----------------------------Distanciamiento----------------------------#
#check other values 
#resultadoDistancia = []

    
         






