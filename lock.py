from logging import getLogger
log = getLogger('nate')

class Lock:
    def __init__(self, source, dest, fleets, time):
        self.source, self.dest, self.fleets = source, dest, fleets
        delay = source.distance(dest)
        self.wait = time - delay

    def engage(self):
        if self.fleets:
            self.source.locks.setdefault(self.wait, set()).add(self)

    def disengage(self):
        try:
            self.source.locks[self.wait].remove(self)
        except KeyError:
            pass

    def execute(self):
        if self.source != self.dest and self.wait == 0:
            self.source.send_fleet(self.dest, self.fleets)

    def __repr__(self):
        return '<%s fleets from %s to %s in %s>' % (self.fleets, self.source, self.dest, self.wait)
