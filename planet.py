from math import tan, radians
from logging import getLogger
log = getLogger('nate')

from action import Attack, Defend
from planetwars import planet
from planetwars.player import ME, ENEMIES

MAX_WAYPOINT_ANGLE = radians(20)

class Planet(planet.Planet):
    ###################################################################
    # Extra Properties
    #
    conquered_in = None
    conquering = property(lambda self: self.conquered_in is not None)
    condemned_in = None
    condemned = property(lambda self: self.condemned_in is not None)
    locks = {}

    ###################################################################
    # Convenience Properties
    #
    @property
    def incoming_enemies(self):
        return self.universe.find_fleets(owner=ENEMIES, destination=self)

    @property
    def incoming_reinforcements(self):
        return self.universe.find_fleets(owner=ME, destination=self)

    ###################################################################
    # Main Turn
    #
    def actions(self):
        if self.owner == ME and self.attacking_fleets:
            yield Defend(self)
        elif self.conquering and self.incoming_enemies:
            yield Defend(self)
        if self.owner != ME:
            yield Attack(self)

    def execute(self):
        for (planet, fleets) in self.locks.get(0, ()):
            self.send_fleet(planet, fleets)
        if self.condemned: log.debug('%s CONDEMNED' % self)
        self.advance()

    def step(self):
        if self.conquering:
            self.conquered_in -= 1
        if self.condemned:
            self.condemned_in -= 1
        self.locks = {}

    ###################################################################
    # Helper Methods
    #
    def is_waypoint(self, source, dest):
        if source == self:
            return False
        A = source.distance(dest)
        B = source.distance(self)
        C = self.distance(dest)
        if A**2 <= B**2 + C**2:
            return False
        if source.position.x == dest.position.x:
            return True
        a2b = float(source.position.y - self.position.y) / float(source.position.x - self.position.x)
        a2c = float(source.position.y - dest.position.y) / float(source.position.x - dest.position.x)
        theta = abs(tan(a2b - a2c))
        log.debug('WAYPOINT %s between %s and %s: %s' % (self, source, dest, theta))
        return theta <= MAX_WAYPOINT_ANGLE

    def advance(self):
        enemy = self.find_nearest_neighbor(owner=ENEMIES)
        if not enemy:
            return
        waypoints = [p for p in self.universe.planets
                if (p.owner == ME or p.conquering)
                and p.is_waypoint(self, enemy)]
        if not waypoints:
            self.universe.idlers += self.available()
            return
        target = min(waypoints, key=lambda p: p.distance(self))
        available = self.available()
        if available:
            self.send_fleet(target, available)

    ###################################################################
    # Fleet Calculation
    #
    def available(self, dest=None, expiration=None):
        delay = 0 if dest is None else self.distance(dest)
        build_time = 0 if expiration is None else expiration - delay
        if build_time < 0: return 0
        steps = max([build_time] + self.locks.keys())
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
        delay = self.distance(planet)
        assert delay <= time
        if fleets:
            self.locks.setdefault(time - delay, set()).add((planet, fleets))
