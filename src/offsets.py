import numpy as np
import psycopg2

from postgis.psycopg import register
from config import *

########
# CUSTOM PARAMS
step = 10

ts_i = 1570665600
ts_f = 1570667000 # 1570752000

array_size = int((23*60+20)/step) #int(24*60*60/step)
########

conn = psycopg2.connect(database=DB_NAME, user=USER_NAME)
register(conn)
cursor = conn.cursor()

cursor.execute('select distinct taxi from tracks order by 1')
results = cursor.fetchall()

taxis_x = {}
taxis_y = {}

for row in results:
    taxi = int(row[0])
    taxis_x[taxi] = np.zeros(array_size)
    taxis_y[taxi] = np.zeros(array_size)

for i in range(ts_i, ts_f, step):
    cur_ts = str(i)
    cursor.execute(
        f"select taxi, st_pointn(proj_track, {cur_ts}-ts) from tracks where "
        f"ts < {cur_ts} and ts + st_numpoints(proj_track) > {cur_ts}"
    )
    results = cursor.fetchall()
    for row in results:
        taxi = int(row[0])
        x, y = row[1].coords
        taxis_x[taxi][int((i-ts_i)/10)] = x
        taxis_y[taxi][int((i-ts_i)/10)] = y

offsets = []

for i in range(array_size):
    l = []
    for j in taxis_x:
        l.append([taxis_x[j][i], taxis_y[j][i]])
    offsets.append(l)

with open('offsets.csv','w') as fp:
    for i in offsets:
        print(f"{i[0][0]} {i[0][1]}", end='', file=fp)
        for j in range(1, len(i)):
            print(f",{i[j][0]} {i[j][1]}", end='', file=fp)
        print("", file=fp)
