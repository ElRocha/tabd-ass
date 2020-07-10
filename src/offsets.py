from config import DATABASE
import numpy as np
import psycopg2

from postgis.psycopg import register
from datetime import datetime, timezone
from util import utc_timestamp

def filename(step, start_time, end_time):
    ts_s = datetime(2019, 10, 10, start_time[0], start_time[1], start_time[2])
    ts_s = int(utc_timestamp(ts_s))

    ts_e = datetime(2019, 10, 10, end_time[0], end_time[1], end_time[2])
    ts_e = int(utc_timestamp(ts_e))

    return f"{step}-{ts_s}-{ts_e}.csv"

def sql_taxis(cursor):
    cursor.execute('select distinct taxi from tracks order by 1')
    return cursor.fetchall()

def sql_taxis_by_concelho(cursor, concelho):
    taxis = []
    cursor.execute(
        'select distinct taxi from tracks, cont_aad_caop2018 where '
        f"st_within(proj_track, proj_boundary) and concelho = '{concelho}'"
    )
    return cursor.fetchall()

def sql_points_in_time(cursor, t):
    t_str = str(t)
    cursor.execute(
        f"select taxi, st_pointn(proj_track, {t_str}-ts) from tracks where "
        f"ts < {t_str} and ts + st_numpoints(proj_track) > {t_str}"
    )
    return cursor.fetchall()

"""
Generate taxi offsets based on step and start and end time params

Offsets are written to a file whose name is returned from the
function. The first 10 taxis appearing in Porto and Lisboa are
also written to a custom file whose name is also returned from
the function.
"""
def generate(step, start_time, end_time):
    # generate timestamps and number of records
    ts_s   = datetime(2019, 10, 10, start_time[0], start_time[1], start_time[2])
    ts_e   = datetime(2019, 10, 10, end_time[0], end_time[1], end_time[2])
    t_diff = ts_e - ts_s

    ts_s = int(utc_timestamp(ts_s))
    ts_e = int(utc_timestamp(ts_e))

    n_record = int(t_diff.seconds / step) + 5 # give some space to be sure

    # database
    conn = psycopg2.connect(database=DATABASE['dbname'], user=DATABASE['user'], password=DATABASE['password'])
    register(conn)
    cursor = conn.cursor()

    # build offsets and first10 taxis by concelho
    taxis_x, taxis_y = {}, {}
    cur, taxi_idx = 0, {}
    for row in sql_taxis(cursor):
        taxi = int(row[0])
        taxis_x[taxi] = np.zeros(n_record)
        taxis_y[taxi] = np.zeros(n_record)
        taxi_idx[taxi] = cur
        cur += 1

    taxis_concelho = {'PORTO': [], 'LISBOA': []}
    for concelho in taxis_concelho:
        for row in sql_taxis_by_concelho(cursor, concelho):
            taxi = int(row[0])
            taxis_concelho[concelho].append(taxi)

    first10_concelho = {'PORTO': [], 'LISBOA': []}

    for t in range(ts_s, ts_e, step):
        for row in sql_points_in_time(cursor, t):
            taxi = int(row[0])
            x, y = row[1].coords
            taxis_x[taxi][int((t-ts_s)/step)] = x
            taxis_y[taxi][int((t-ts_s)/step)] = y

            if taxi in taxis_concelho['PORTO']:
                if len(first10_concelho['PORTO']) < 10 and not taxi_idx[taxi] in first10_concelho['PORTO']:
                    first10_concelho['PORTO'].append(taxi_idx[taxi])

            elif taxi in taxis_concelho['LISBOA']:
                if len(first10_concelho['LISBOA']) < 10 and not taxi_idx[taxi] in first10_concelho['LISBOA']:
                    first10_concelho['LISBOA'].append(taxi_idx[taxi])

    offsets = []
    for rec in range(n_record):
        coords = []
        for taxi in taxis_x:
            coords.append([taxis_x[taxi][rec], taxis_y[taxi][rec]])
        offsets.append(coords)

    # save offsets
    fp_offsets = filename(step, start_time, end_time)
    with open('data/' + fp_offsets, 'w') as fp:
        for rec in offsets:
            print(f"{rec[0][0]} {rec[0][1]}", end='', file=fp)
            for i in range(1, len(rec)):
                print(f",{rec[i][0]} {rec[i][1]}", end='', file=fp)
            print("", file=fp)

    # save first 10 taxis
    fp_first10 = 'f10-' + fp_offsets
    with open('data/' + fp_first10, 'w') as fp:
        for concelho in first10_concelho:
            print(f"{first10_concelho[concelho][0]}", end='', file=fp)
            for i in range(1, 10):
                print(f",{first10_concelho[concelho][i]}", end='', file=fp)
            print("", file=fp)

    conn.close()
    return (fp_offsets, fp_first10)
