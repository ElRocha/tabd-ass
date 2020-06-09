import sys
import argparse
#import offsets

from util import *
from config import DEFAULTS

#
# Argument parsing
#
parser = argparse.ArgumentParser(prog=sys.argv[0])
parser.add_argument('--step', nargs='?', type=int, default=DEFAULTS['step'], help=f"Animation time step in seconds ([1,60]) (default={DEFAULTS['step']})")
parser.add_argument('--delay', nargs='?', type=int, default=DEFAULTS['delay'], help=f"Animation delay between frames in miliseconds ([10,5000]) (default={DEFAULTS['delay']})")
parser.add_argument('--start', nargs='+', type=int, default=DEFAULTS['start'], help=f"Animation start time (h[0,23] m[0,59] s[0,59]) (default={DEFAULTS['start'][0]} {DEFAULTS['start'][1]} {DEFAULTS['start'][2]})")
parser.add_argument('--end', nargs='+', type=int, default=DEFAULTS['end'], help=f"Animation end time (h[0,23] m[0,59] s[0,59]) (default={DEFAULTS['end'][0]} {DEFAULTS['end'][1]} {DEFAULTS['end'][2]})")

args = parser.parse_args()

if not validate_args(args):
    parser.print_help()
    sys.exit()

#
# Need for new offsets?
#
fp_offsets = 'offsets_cached.csv' # offsets for default params

if args.step != DEFAULTS['step'] or args.start != DEFAULTS['start'] or args.end != DEFAULTS['end']:
    print('Calculating offsets... ', end='')
    # fp_offsets = offsets.generate(args)
    print('DONE!')

#
# Animate!
#


# How am I gonna use this?
# |
# v
def get_first_infected():
    sql = 'select distinct taxi,ts from tracks, cont_aad_caop2018 where st_contains(proj_boundary, st_startpoint(proj_track)) and concelho like \'LISBOA\' order by 2 limit 10'
    cursor_psql.execute(sql)
    lis_taxis = cursor_psql.fetchall()
    sql = 'select distinct taxi,ts from tracks, cont_aad_caop2018 where st_contains(proj_boundary, st_startpoint(proj_track)) and concelho like \'PORTO\' order by 2 limit 10'
    cursor_psql.execute(sql)
    por_taxis = cursor_psql.fetchall()
    return [lis_taxis[random.randint(0, 9)][0], por_taxis[random.randint(0, 9)][0]]
