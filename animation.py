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

fig, (ax1,ax2) = plt.subplots(1,2,figsize=(width_in_inches*scale*3, height_in_inches*scale))
ax1.axis('off')
ax1.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

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
            ax1.plot(xs, ys, color='black', lw='0.2')
    if type(geom) is Polygon:
        xys = geom[0].coords
        xs, ys = [], []
        for (x, y) in xys:
            xs.append(x)
            ys.append(y)
        ax1.plot(xs, ys, color='black', lw='0.2')

offsets = []
with open('offsets_do_prof.csv','r') as fp:
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

scat = ax1.scatter(x, y, s=2, color='green')

ax2.set(xlim=(0,2),ylim=(0,2*1.2))
g, = ax2.plot([0],[2])
ax2.set_xlabel('iteration')
ax2.set_ylabel('infected taxis')

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

    # update iteration data
    inf_rate = math.ceil(60 / step)
    new_infections = set()

    for taxi in infected:
        for taxi2 in susceptible:
            xy1 = [float(x) for x in offsets[i][taxi]]
            xy2 = [float(x) for x in offsets[i][taxi2]]

            # ignore if any of the taxis isn't active
            if (xy1[0] == 0 and xy1[1]== 0) or (xy2[0]== 0 and xy2[1]==0):
                proximity[taxi][taxi2] = 0
                continue

            # update proximity counter
            d = eucl_dist(xy1[0], xy1[1], xy2[0], xy2[1])

            if taxi2 in proximity[taxi]:
                if d < 50:
                    proximity[taxi][taxi2] += 1
                else:
                    proximity[taxi][taxi2] = 0
            else:
                if d < 50:
                    proximity[taxi][taxi2] = 1
                else:
                    proximity[taxi][taxi2] = 0

            # new infection ?
            inf_prob = math.floor(proximity[taxi][taxi2] / inf_rate) * 10
            inf_prob = min( [100, inf_prob] )

            if test_infection(inf_prob):
                new_infections.add(taxi2)
                color[taxi2] = 'red'

    # update sets
    infected = infected | new_infections
    susceptible = susceptible - new_infections

    # scatter plot
    ax1.set_title(dt.utcfromtimestamp(ts_i+i*10))
    scat.set_offsets(offsets[i])
    scat.set_color(color)

    # curve plot
    g.set_xdata(np.append(g.get_xdata(),i))
    g.set_ydata(np.append(g.get_ydata(),len(infected)))
    ax2.set_xlim((0,len(g.get_xdata())))
    ax2.set_ylim((0,len(infected)*1.2))

    print(f"it: {i}, infected: {len(infected)}")

anim = FuncAnimation(fig,
                     animate,
                     interval=500,
                     frames=range(len(offsets)),
                     repeat=False,
                     cache_frame_data=False) # nothing is the same between frames

plt.draw()
plt.show()
