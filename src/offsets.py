from config import DATABASE
import numpy as np
import psycopg2

from postgis.psycopg import register
from datetime import datetime, timezone

def get_taxis(cursor, n_record):
    taxis_x, taxis_y = {}, {}
    cursor.execute('select distinct taxi from tracks order by 1')
    for row in cursor.fetchall():
        taxi = int(row[0])
        taxis_x[taxi] = np.zeros(n_record)
        taxis_y[taxi] = np.zeros(n_record)
    return (taxis_x, taxis_y)

def get_points_in_time(cursor, t, ts_s, step, taxis_x, taxis_y):
    t_str = str(t)
    cursor.execute(
        f"select taxi, st_pointn(proj_track, {t_str}-ts) from tracks where "
        f"ts < {t_str} and ts + st_numpoints(proj_track) > {t_str}"
    )
    for row in cursor.fetchall():
        taxi = int(row[0])
        x, y = row[1].coords
        taxis_x[taxi][int((t-ts_s)/step)] = x
        taxis_y[taxi][int((t-ts_s)/step)] = y

def generate(step, start_time, end_time):
    # generate timestamps and number of records
    ts_s   = datetime(2019, 10, 10, start_time[0], start_time[1], start_time[2])
    ts_e   = datetime(2019, 10, 10, end_time[0], end_time[1], end_time[2])
    t_diff = ts_e - ts_s

    ts_s = int(ts_s.replace(tzinfo = timezone.utc).timestamp())
    ts_e = int(ts_e.replace(tzinfo = timezone.utc).timestamp())

    n_record = int(t_diff.seconds / step)

    # database
    conn = psycopg2.connect(database=DATABASE['dbname'], user=DATABASE['user'], password=DATABASE['password'])
    register(conn)
    cursor = conn.cursor()

    # build offsets
    taxis_x, taxis_y = get_taxis(cursor, n_record)

    for t in range(ts_s, ts_e, step):
        get_points_in_time(cursor, t, ts_s, step, taxis_x, taxis_y)

    offsets = []
    for rec in range(n_record):
        coords = []
        for taxi in taxis_x:
            coords.append([taxis_x[taxi][rec], taxis_y[taxi][rec]])
        offsets.append(coords)

    # save offsets
    fp_name = f"{ts_s}-{ts_e}.csv"
    with open(fp_name, 'w') as fp:
        for rec in offsets:
            print(f"{rec[0][0]} {rec[0][1]}", end='', file=fp)
            for i in range(1, len(rec)):
                print(f",{rec[i][0]} {rec[i][1]}", end='', file=fp)
            print("", file=fp)

    conn.close()
    return fp_name
