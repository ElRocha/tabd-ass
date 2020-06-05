from config import DB_NAME, USER_NAME
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
import datetime
import csv
from postgis import Polygon, MultiPolygon
from postgis.psycopg import register
import random


def infected_luck() -> bool:
    return random.randint(0, 100) > 90


def get_first_infected() -> List[int]:
    sql = 'select distinct taxi,ts from tracks, cont_aad_caop2018 where st_contains(proj_boundary, st_startpoint(proj_track)) and concelho like \'LISBOA\' order by 2 limit 10'
    cursor_psql.execute(sql)
    lis_taxis = cursor_psql.fetchall()
    sql = 'select distinct taxi,ts from tracks, cont_aad_caop2018 where st_contains(proj_boundary, st_startpoint(proj_track)) and concelho like \'PORTO\' order by 2 limit 10'
    cursor_psql.execute(sql)
    por_taxis = cursor_psql.fetchall()
    return [lis_taxis[random.randint(0, 9)][0], por_taxis[random.randint(0, 9)][0]]


def animate(i: int):
    ax.set_title(datetime.datetime.utcfromtimestamp(ts_i+i*10))
    scat.set_offsets(offsets[i])


def linestring_to_points(line_string: str) -> List[List[float]]:
    total_points = []
    points = line_string[11:-1].split(',')
    for point in points:
        (x, y) = point.split()
        total_points.append([float(x), float(y)])
    return total_points


scale = 1/3000000
conn = psycopg2.connect(database=DB_NAME, user=USER_NAME)
register(conn)

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1

fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

cursor_psql = conn.cursor()
sql = "select distrito,st_union(proj_boundary) from cont_aad_caop2018 group by distrito"
cursor_psql.execute(sql)
results = cursor_psql.fetchall()
xs, ys = [], []
for row in results:
    geom = row[1]
    if type(geom) is MultiPolygon:
        for pol in geom:
            xys = pol[0].coords
            xs, ys = [], []
            for (x, y) in xys:
                xs.append(x)
                ys.append(y)
            ax.plot(xs, ys, color='black', lw='0.2')
    if type(geom) is Polygon:
        xys = geom[0].coords
        xs, ys = [], []
        for (x, y) in xys:
            xs.append(x)
            ys.append(y)
        ax.plot(xs, ys, color='black', lw='0.2')


sql = """select st_astext(proj_track),ts,taxi from tracks where taxi='20000333' order by ts"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()
# x, y = [], []
results = [[linestring_to_points(i[0]), i[1]] for i in results]
ts_i = results[0][1]
offsets = [[] for _ in results]
for i, row in enumerate(results):
    diff = row[1] - ts_i
    start_fillers = [[float(0), float(0)] for _ in range(diff)]
    offsets[i].append(start_fillers)
    offsets[i].append(row[0])

max_depth = len(max(offsets, key=lambda x: len(x)))
for i in offsets:
    diff = max_depth - len(i)
    end_fillers = [[float(0), float(0)] for _ in range(diff)]
    i.append(end_fillers)

offsets = list(map(list, zip(*offsets)))  # invert matrix

print(offsets[0][0])

x, y = [], []
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])

scat = ax.scatter(x, y, s=2, color='orange')
anim = FuncAnimation(
    fig, animate, interval=10, frames=len(offsets)-1, repeat=False)

plt.draw()
plt.show()
