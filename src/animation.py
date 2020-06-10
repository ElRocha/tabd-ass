import csv
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import random
import math

from config import DATABASE
from util import eucl_dist, coin_toss
from datetime import datetime, timezone
from postgis.psycopg import register
from postgis import Polygon, MultiPolygon
from matplotlib.animation import FuncAnimation

def animate(i):
    global ax1, ax2, g, scat
    global step, ts_s
    global offsets
    global infected, susceptible, color, proximity

    # update iteration data
    inf_rate = math.ceil(60 / step)
    new_infections = set()

    for taxi in infected:
        for taxi2 in susceptible:
            xy1 = [float(x) for x in offsets[i][taxi]]
            xy2 = [float(x) for x in offsets[i][taxi2]]

            # ignore if any of the taxis isn't active
            if (xy1[0] == 0 and xy1[1] == 0) or (xy2[0] == 0 and xy2[1] == 0):
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
            inf_prob = min([100, inf_prob])

            if coin_toss(inf_prob):
                new_infections.add(taxi2)
                color[taxi2] = 'red'

    # update sets
    infected = infected | new_infections
    susceptible = susceptible - new_infections

    # scatter plot
    ax1.set_title(datetime.utcfromtimestamp(ts_s+i*step))
    scat.set_offsets(offsets[i])
    scat.set_color(color)

    # curve plot
    g.set_xdata(np.append(g.get_xdata(), i))
    g.set_ydata(np.append(g.get_ydata(), len(infected)))
    ax2.set_xlim((0, len(g.get_xdata())))
    ax2.set_ylim((0, len(infected)*1.2))

    #print(f"iteration: {i}, infected: {len(infected)}")

def sql_boundaries(cursor):
    cursor.execute('select distrito,st_union(proj_boundary) from cont_aad_caop2018 group by distrito')
    return cursor.fetchall()

def read_offsets(fp_offsets):
    offsets = []
    with open('data/' + fp_offsets, 'r') as fp:
        reader = csv.reader(fp)
        for row in reader:
            l = []
            for coords in row:
                x, y = coords.split()
                l.append([float(x), float(y)])
            offsets.append(l)
    return offsets

def read_first10(fp_first10):
    first10 = []
    with open('data/' + fp_first10, 'r') as fp:
        reader = csv.reader(fp)
        for row in reader:
            l = []
            for taxi in row:
                l.append(int(taxi))
            first10.append(l)
    return first10

def start(inc, delay, n_infected, start_time, fp_offsets, fp_first10, save=False):
    # define globals required for the animation function
    global ax1, ax2, g, scat
    global step, ts_s
    global offsets
    global infected, susceptible, color, proximity

    # step
    step = inc

    # start timestamp
    dt_s = datetime(2019, 10, 10, start_time[0], start_time[1], start_time[2])
    ts_s = int(dt_s.replace(tzinfo = timezone.utc).timestamp())

    # scatter plot
    scale = 1/3000000
    xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
    width_in_inches  = (xs_max - xs_min) / 0.0254*1.1
    height_in_inches = (ys_max - ys_min) / 0.0254*1.1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(width_in_inches*scale*3, height_in_inches*scale))

    ax1.axis('off')
    ax1.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

    # curve plot
    ax2.set(xlim=(0, 2), ylim=(0, 2*1.2))
    g, = ax2.plot([0], [0])
    ax2.set_xlabel('iteration')
    ax2.set_ylabel('infected taxis')

    # draw map boundaries
    conn = psycopg2.connect(database=DATABASE['dbname'], user=DATABASE['user'], password=DATABASE['password'])
    register(conn)
    cursor = conn.cursor()

    for row in sql_boundaries(cursor):
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

    conn.close()

    # read file data
    offsets = read_offsets(fp_offsets)
    first10 = read_first10(fp_first10)

    # animation vars
    n_taxis = len(offsets[0])
    infected = set()
    susceptible = set([t for t in range(n_taxis)])
    color = ['green' for _ in range(n_taxis)]
    proximity = {t: {} for t in range(n_taxis)}

    # initially infected taxis
    for concelho in first10:
        for idx in random.sample(range(10), n_infected):
            taxi = concelho[idx]
            infected.add(taxi)
            susceptible.remove(taxi)
            color[taxi] = 'red'

    # draw taxis first position
    x0, y0 = [], []
    for i in offsets[0]:
        x0.append(i[0])
        y0.append(i[1])

    scat = ax1.scatter(x0, y0, s=2, color=color)

    # animate !
    anim = FuncAnimation(
        fig,
        animate,
        interval=delay,
        frames=range(len(offsets)),
        repeat=False,
        cache_frame_data=False # nothing is the same between frames
    )

    if save:
        anim.save('animation.mp4')

    plt.draw()
    plt.show()
