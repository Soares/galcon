from logging import getLogger
log = getLogger('nate')

class Contract:
    def __init__(self, source, dest, fleets, time):
        self.source, self.dest, self.fleets = source, dest, fleets
        delay = source.distance(dest)
        self.wait = time - delay
        source.contracts.setdefault(self.wait, set()).add(self)
        self.opposition = None

    def abort(self):
        self.source.contracts[self.wait].remove(self)

    def oppose(self, obj):
        self.opposition = obj

    def execute(self):
        if self.wait: return
        fleet, = self.source.send_fleets(self.dest, self.fleets)
        fleet.opposition = self.opposition
