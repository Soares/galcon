from logging import getLogger
log = getLogger('nate')

class Contract(object):
    def __init__(self, destination, fleets):
        self.universe = destination.universe
        self.dest = destination
        self.fleets = fleets

    def execute(self, source):
        if source.id == self.dest.id:
            return
        self.universe.send_fleet(source, self.dest, self.fleets)

    def __repr__(self):
        return '<%d fleets to %s>' % (self.fleets, self.dest)

class Contracts(object):
    def __init__(self, planet):
        self.universe = planet.universe
        self.source = planet
        self.contracts = {}

    def step(self):
        for contract in self.contracts.get(0, ()):
            contract.execute(self.source)
        self.contracts = dict((k-1, v) for (k, v) in self.contracts.items() if k > 0 and v)

    def __getitem__(self, i):
        return self.contracts.setdefault(i, set())

    def add(self, destination, fleets, turns):
        from planet import CONTESTED
        destination.state = CONTESTED
        delay = self.source.distance(destination)
        self[turns - delay].add(Contract(destination, fleets))

    @property
    def max(self):
        return max(self.contracts.keys() or [0])

    def __repr__(self):
        return '%s: %s' % (self.source, dict((k, v) for (k, v) in self.contracts.items() if v))
