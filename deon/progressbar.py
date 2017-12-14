import sys


class Progressbar():

    def __init__(self):
        self.step = '\\'

    def update(self):
        self._next_step()
        sys.stdout.write('\r')
        sys.stdout.write('\t{}'.format(self.step))
        sys.stdout.flush()

    def _next_step(self):
        if self.step == '\\':
            self.step = '/'
        else:
            self.step = '\\'
