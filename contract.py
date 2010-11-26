from logging import getLogger
log = getLogger('nate')

class Contract:
    def __init__(self, source, dest, fleets, time):
        self.source, self.dest, self.fleets = source, dest, fleets
        delay = source.distance(dest)
        self.wait = time - delay
        self.opposition = None
        source.contracts.setdefault(self.wait, set()).add(self)

    def abort(self):
        if self.wait not in self.source.contracts: return
        if self not in self.source.contracts[self.wait]: return
        self.source.contracts[self.wait].remove(self)

    def oppose(self, obj):
        self.opposition = obj

    def execute(self):
        if self.source == self.dest or self.wait: return
        fleet = self.source.send_fleet(self.dest, self.fleets)
        fleet.opposition = self.opposition

    def __repr__(self):
        return '<%s fleets from %s to %s in %s>' % (self.fleets, self.source, self.dest, self.wait)
