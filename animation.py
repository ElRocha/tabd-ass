import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from random import random, randrange
from matplotlib.animation import FuncAnimation
from datetime import datetime as dt
import csv
from postgis import Polygon, MultiPolygon
from postgis.psycopg import register

from config import *

def eucl_dist(x1, y1, x2, y2):
    return math.sqrt( (x2-x1)**2 + (y2-y1)**2 )

def test_infection(rate):
    return random() < (rate/100)

ts_i = 1570665601
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

offsets = []
with open('offsets.csv','r') as fp:
    reader = csv.reader(fp)
    i = 0
    for row in reader:
        l = []
        for j in row:
            x,y = j.split()
            x = float(x)
            y= float(y)
            l.append([x,y])
        offsets.append(l)

x, y = [], []
for i in offsets[0]:
    x.append(i[0])
    y.append(i[1])

scat = ax.scatter(x, y, s=2, color='green')
step = 10

n_taxis     = len(offsets[0])
infected    = set()
susceptible = set([t for t in range(n_taxis)])
color       = ['green' for _ in range(n_taxis)]
proximity = {t: {} for t in range(n_taxis)}

# 1 Porto and Lisbon taxi as infected
infected.add(16)
susceptible.remove(16)
infected.add(1163)
susceptible.remove(1163)

def animate(i):
    global infected
    global susceptible
    global color
    global proximity

    # check each taxi neighbourhood
    for taxi in infected:
        for taxi2 in susceptible:
            xy1 = [float(x) for x in offsets[i][taxi]]
            xy2 = [float(x) for x in offsets[i][taxi2]]
            d = eucl_dist(xy1[0], xy1[1], xy2[0], xy2[1])

            if taxi2 in proximity[taxi]:
                if d < 50:
                    proximity[taxi][taxi2] += 1
                else:
                    proximity[taxi][taxi2] = 0
            elif d < 50:
                proximity[taxi][taxi2] = 1
            else:
                proximity[taxi][taxi2] = 0

    # check new infections
    inf_rate = math.ceil(60/step)

    new_infections = set()
    for taxi in infected:
        for taxi2 in susceptible:
            inf_prob = math.floor(proximity[taxi][taxi2] / inf_rate) * 10
            inf_prob = min( [100, inf_prob] )

            if test_infection(inf_prob):
                new_infections.add(taxi2)

    infected    = infected | new_infections
    susceptible = susceptible - new_infections

    for t in infected:
        color[t] = 'red'

    ax.set_title( dt.utcfromtimestamp(ts_i+i*10) )
    scat.set_offsets(offsets[i])
    scat.set_color(color)

    print(f"it: {i}, infected: {len(infected)}")


anim = FuncAnimation(fig,
                     animate,
                     interval=1000,
                     frames=range(len(offsets)),
                     repeat=False)

plt.draw()
plt.show()
