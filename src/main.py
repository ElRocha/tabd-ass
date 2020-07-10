import sys
import argparse
import os.path

from offsets import generate, filename
from animation import start
from util import validate_args
from config import DEFAULTS

#
# Argument parsing
#
parser = argparse.ArgumentParser(prog=sys.argv[0])
parser.add_argument('--step', nargs='?', type=int, default=DEFAULTS['step'], help=f"Animation time step in seconds ([1,60]) (default={DEFAULTS['step']})")
parser.add_argument('--delay', nargs='?', type=int, default=DEFAULTS['delay'], help=f"Animation delay between frames in miliseconds ([10,5000]) (default={DEFAULTS['delay']})")
parser.add_argument('--infected', nargs='?', type=int, default=DEFAULTS['infected'], help=f"Number of starting infected taxis in Porto and Lisboa. ([1,10]) (default={DEFAULTS['infected']})")
parser.add_argument('--offline', action='store_true', default=DEFAULTS['offline'], help=f"Precompute data for each frame of the animation before actually running it.")
parser.add_argument('--start', nargs='+', type=int, default=DEFAULTS['start'], help=f"Animation start time (h[0,23] m[0,59] s[0,59]) (default={DEFAULTS['start'][0]} {DEFAULTS['start'][1]} {DEFAULTS['start'][2]})")
parser.add_argument('--end', nargs='+', type=int, default=DEFAULTS['end'], help=f"Animation end time (h[0,23] m[0,59] s[0,59]) (default={DEFAULTS['end'][0]} {DEFAULTS['end'][1]} {DEFAULTS['end'][2]})")
parser.add_argument('--record', action='store_true', default=DEFAULTS['record'], help=f"Save the animation.")

args = parser.parse_args()

if not validate_args(args):
    parser.print_help()
    sys.exit()

#
# Need for new offsets?
#
fp_offsets = filename(args.step, args.start, args.end)
fp_first10 = 'f10-' + fp_offsets

if not os.path.isfile('data/' + fp_offsets):
    print('Generating offsets... ')
    fp_offsets, fp_first10 = generate(args.step, args.start, args.end)
else:
    print('Found offsets for current parameter configuration! Skiping generation...')

#
# Animate!
#
start(args.step, args.delay, args.infected, args.start, fp_offsets, fp_first10, args.offline, args.record)
