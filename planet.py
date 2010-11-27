from math import tan, radians
from logging import getLogger
log = getLogger('nate')

from action import Attack, Defend
from planetwars import planet
from planetwars.player import ME, ENEMIES

MAX_WAYPOINT_ANGLE = radians(30)

class Planet(planet.Planet):
    conquered_in = None
    conquering = property(lambda self: self.conquered_in is not None)
    condemned_in = None
    condemned = property(lambda self: self.condemned_in is not None)
    threats = set()
    locks = {}

    @property
    def incoming_enemies(self):
        return self.universe.find_fleets(owner=ENEMIES, destination=self)

    @property
    def incoming_reinforcements(self):
        return self.universe.find_fleets(owner=ME, destination=self)

    def actions(self):
        if self.owner == ME and self.attacking_fleets:
            yield Defend(self)
        elif self.conquering and self.incoming_enemies:
            yield Defend(self)
        if self.owner != ME:
            yield Attack(self)

    def step(self):
        if self.contested:
            self.conquered_in -= 1
        if self.condemned:
            self.condemned_in -= 1
        self.threats = set()
        self.locks = {}

    def is_waypoint(self, source, dest):
        if source == self:
            return False
        A = source.distance(dest)
        B = source.distance(self)
        C = self.distance(dest)
        if A**2 >= B**2 + C**2:
            return False
        a2b = float(source.y - self.y) / float(source.x - self.x)
        a2c = float(source.y - dest.y) / float(source.x - dest.x)
        theta = abs(tan(a2b - a2c))
        return theta <= MAX_WAYPOINT_ANGLE

    def targets(self):
        # TODO: Don't send through planets that are condemned before we arrive
        if self.threats:
            return filter(self.is_waypoint, self.universe.contested)
        targets = self.universe.contested
        targets |= set(p for p in self.universe.my_planets if p.threats)
        target = min(targets, key=lambda p: p.distance(self))
        waypoints = (p for p in self.universe.my_planets if p.is_waypoint(self, target))
        return [min(waypoints, key=lambda p: p.distance(self))]

    def flood(self, targets):
        if len(targets) == 1:
            target, = targets
            self.send_fleets(target, self.available())
            return
        weights = dict((p, Attack.weigh(p)) for p in targets)
        total = sum(w for w in weights.values() if w > 0)
        available = self.available()
        for (planet, weight) in weights.items():
            if weight <= 0: continue
            self.send_fleets(p, int(available * (weight / total)))

    def execute(self):
        for (planet, fleets) in self.locks[0]:
            self.send_fleet(planet, fleets)
        self.flood(self.targets())

    def available(self, dest=None, expiration=None):
        delay = 0 if dest is None else self.distance(dest)
        build_time = 0 if expiration is None else expiration - delay
        if build_time < 0: return 0
        steps = max([build_time] + self.contracts.keys())
        available = self.ship_count
        futures = 0
        for i in range(steps + 1):
            if self.condemned and i > self.condemned_in:
                pass
            elif i > build_time:
                futures += self.growth_rate
            elif i:
                available += self.growth_rate
            for (planet, fleets) in self.locks.get(i, ()):
                futures -= fleets
            if futures < 0:
                available -= abs(futures)
                futures = 0
        return max(0, available)

    def lock(self, planet, fleets, time):
        self.locks.setdefault(time, set()).add((planet, fleets))
