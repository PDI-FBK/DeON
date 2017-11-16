import sys


def print_progress(msg, done, total='oo'):
    sys.stdout.write('\r')
    sys.stdout.write('\t{} {}/{}'.format(msg, done, total))
    sys.stdout.flush()
