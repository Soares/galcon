from logging import getLogger
log = getLogger('nate')

from issues import InsufficientFleets

class Commitment(object):
    def __init__(self, planet, fleets, expiration):
        self.universe = planet.universe
        self.planet = planet
        self.fleets = fleets
        self.expiration = expiration
        self.contracts = set()

    def gather_contracts(self):
        if self.expiration is not None:
            return self.gather_from_distance()
        return self.gather_from_nearby()

    def gather_from_distance(self):
        assert not self.contracts
        planets = sorted(self.universe.my_planets, key=lambda p: -p.distance_to_enemy)
        needed = self.fleets
        for planet in planets:
            commit = min(needed, planet.available(self.planet, self.expiration))
            if commit <= 0: continue
            self.contracts.add((planet, commit))
            needed -= commit
            if needed == 0: break
        if needed > 0:
            raise InsufficientFleets
        for (source, amount) in self.contracts:
            source.contract(self.planet, amount, self.expiration)

    def gather_from_nearby(self):
        # TODO: bias towards back lines
        assert not self.contracts
        planets = sorted(self.universe.my_planets, key=lambda p: p.distance(self.planet))
        for i in range(len(planets)):
            attackers = planets[:i+1]
            distance = planets[i].distance(self.planet)
            available = sum(p.available(self.planet, distance) for p in attackers)
            if available >= self.fleets:
                break
        else:
            raise InsufficientFleets
        needed = self.fleets
        for planet in sorted(attackers, key=lambda p: -p.distance_to_enemy):
            commit = min(needed, planet.available(self.planet, distance))
            if commit <= 0: continue
            planet.contract(self.planet, commit, distance)
            self.contracts.add((planet, commit))
            needed -= commit
            if not needed: break

    def __repr__(self):
        if self.expiration is not None:
            return '<Commit %d to %d in %d>' % (self.fleets, self.planet.id, self.expiration)
        return '<Commit %d to %d immediately>' % (self.fleets, self.planet.id)

    def __str__(self):
        return repr(self) + '\n' + '\n'.join('\t%s sends %s' % c for c in self.contracts)
