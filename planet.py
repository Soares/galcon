from math import tan, radians
from logging import getLogger
log = getLogger('nate')

from action import Attack, Defend
from planetwars import planet
from planetwars.player import ME, ENEMIES

MAX_WAYPOINT_ANGLE = radians(30)
MAX_REINFORCE_ANGLE = radians(45)

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
        if 0 in self.locks:
            log.debug('Executing fleet locks')
        for (planet, fleets) in self.locks.get(0, ()):
            self.send_fleet(planet, fleets)
        if self.condemned:
            log.debug('%s has been condemned (%d turns)' % (self, self.condemned_in))
        self.advance()

    def step(self):
        if self.conquering:
            self.conquered_in = self.conquered_in - 1 if self.conquered_in > 0 else None
        if self.condemned:
            self.condemned_in = self.condemned_in - 1 if self.condemned_in > 0 else None
        self.locks = {}

    ###################################################################
    # Helper Methods
    #
    def is_waypoint(self, source, dest, angle=MAX_WAYPOINT_ANGLE):
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
        return theta <= angle

    def advance(self):
        enemy = self.find_nearest_neighbor(owner=ENEMIES)
        if not enemy:
            self.universe.idlers += self.available()
            return
        waypoints = [p for p in self.universe.planets - self
                if (p.owner == ME or p.incoming_reinforcements)
                and p.is_waypoint(self, enemy)]
        if not waypoints:
            self.reinforce()
            self.universe.idlers += self.available()
            return
        target = min(waypoints, key=lambda p: p.distance(self))
        available = self.available()
        if available:
            log.debug('Advancing towards front lines')
            self.send_fleet(target, available)

    def reinforce(self):
        fleets = min(self.growth_rate, self.available())
        targets = [p for p in self.universe.marks
                if p.owner != ME and p.incoming_reinforcements
                and any(p.is_waypoint(self, e, MAX_REINFORCE_ANGLE)
                    for e in self.universe.enemy_planets)]
        if targets and fleets:
            log.debug('Reinforcing from front lines')
            self.send_fleet(min(targets, key=lambda p: p.distance(self)), fleets)

    ###################################################################
    # Fleet Calculation
    #
    def available(self, dest=None, expiration=None):
        delay = 0 if dest is None else self.distance(dest)
        build_time = 0 if expiration is None else expiration - delay
        if build_time < 0:
            return 0
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
        log.debug('%s locking %s for %s in %s' % (self, fleets, planet, time))
        delay = self.distance(planet)
        assert delay <= time
        if fleets:
            self.locks.setdefault(time - delay, set()).add((planet, fleets))

    def __lt__(self, other):
        ours = self.locks.get(0, set())
        theirs = other.locks.get(0, set())
        ours = (sum(f for (p, f) in ours), len(ours), self.id)
        theirs = (sum(f for (p, f) in theirs), len(theirs), other.id)
        return ours < theirs
