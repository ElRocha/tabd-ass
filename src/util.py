from datetime import datetime

"""
Custom cmd-argument validation function.

The --help output produced by the argparse module
when choices for each argument were provided was
too ugly and difficult to handle for multi-param
arguments. Therefore, we only use the argparse
module for a faster setup but do our own validation.
"""
def validate_args(args):
    step = args.step
    if step < 1 or step > 60:
        return False

    delay = args.delay
    if delay < 10 or delay > 5000:
        return False

    dt = []
    for t in [args.start, args.end]:
        h, m, s = t
        # simple time unit validation
        if h < 0 or h > 23 or m < 0 or m > 59 or s < 0 or s > 59:
            return False

        dt.append(datetime(2019, 10, 10, h, m, s))

    # start-time must come before end-time
    if dt[0].timestamp() >= dt[1].timestamp():
        return False

    return True
