from logging import getLogger
log = getLogger('nate')

from planetwars.player import ME, ENEMIES

class InsufficientFleets(Exception):
    pass


def commit(planet, needs, sources, time):
    locks = set()
    for source in sorted(sources, key=lambda p: -p.proximity):
        fleets = min(needs, source.available(planet, time))
        if fleets:
            locks.add((source, planet, fleets, time))
            needs -= fleets
        if not needs:
            break
    else:
        raise InsufficientFleets
    for (source, planet, fleets, time) in locks:
        source.lock(planet, fleets, time)


class Action(object):
    @classmethod
    def weigh_growth(cls, planet):
        g = min(planet.growth_rate, 5)
        return (g**2) / 25.0

    @classmethod
    def weigh_proximity(cls, planet):
        if not planet.universe.enemy_planets:
            return 1
        if not planet.universe.my_planets:
            return 1
        distance = min(planet.distance(p) for p in planet.universe.my_planets)
        proximity = min(planet.distance(p) for p in planet.universe.enemy_planets)
        p = max(proximity, 7)
        p = (7.0 / p)**2
        return p if proximity >= distance else -p

    @classmethod
    def weigh_distance(cls, planet):
        if not planet.universe.my_planets:
            return 1
        distance = min(planet.distance(p) for p in planet.universe.my_planets)
        d = max(distance, 7)
        return (7.0 / d)**2

    @classmethod
    def weigh_cost(cls, planet):
        if not planet.universe.my_planets:
            return 1
        distance = min(planet.distance(p) for p in planet.universe.my_planets)
        growth_rate = planet.growth_rate if planet.owner & ENEMIES else 0
        growth = growth_rate * distance * 1.5
        c = max(planet.ship_count + growth, 10)
        return 10.0 / c

    @classmethod
    def weigh(cls, planet):
        g = cls.weigh_growth(planet)
        d = cls.weigh_distance(planet)
        c = cls.weigh_cost(planet)
        p = cls.weigh_proximity(planet)
        return (40*g) + (30*d) + (15*p) + (25*c)

    @property
    def priority(self):
        return self.WEIGHT * self.weigh(self.planet)

    def __lt__(self, other):
        return self.priority > other.priority

    def __repr__(self):
        return '%s: %s %s' % (int(self.priority), self.__class__.__name__, self.planet)

    def show(self):
        return '%s: %s %s (%.2fg %.2fd %.2fc %.2fp)' % (
          int(self.priority),
          self.__class__.__name__,
          self.planet,
          self.weigh_growth(self.planet),
          self.weigh_distance(self.planet),
          self.weigh_cost(self.planet),
          self.weigh_proximity(self.planet))

class Defend(Action):
    WEIGHT = 2

    @classmethod
    def weigh(cls, planet):
        weight = Action.weigh(planet)
        return weight * (1 if planet.owner == ME else .7)

    def __init__(self, planet):
        self.universe = planet.universe
        self.planet = planet
        self.delay = planet.conquered_in + 1 if planet.conquering else 0
        self.defenders = planet.universe.my_planets
        unopposed = lambda f: f.turns_remaining > self.delay
        self.bogies = sorted(filter(unopposed, planet.incoming_enemies),
                key=lambda f: f.turns_remaining)

    def engage(self):
        log.info(self)
        last = 0
        for bogie in self.bogies:
            arrival = bogie.turns_remaining
            try:
                self.oppose(bogie, self.reinforcements(last, arrival))
            except InsufficientFleets:
                self.planet.condemned_in = bogie.turns_remaining
                log.debug("Can't oppose %s" % bogie)
                self.universe.marks.discard(self.planet)
                return
            last = arrival

    def oppose(self, fleet, backup):
        if fleet.ship_count - backup > 0:
            return commit(self.planet, fleet.ship_count - backup,
                    self.defenders, fleet.turns_remaining)

    def reinforcements(self, after, before):
        return sum(f.ship_count for f in self.planet.incoming_reinforcements if
                f.turns_remaining > after and f.turns_remaining <= before)


class Attack(Action):
    WEIGHT = 1

    @classmethod
    def overexpanding(cls, planet):
        owned = sum(p.growth_rate for p in planet.universe.my_planets)
        taking = sum(p.growth_rate for p in planet.universe.contested)
        ratio = (taking + planet.growth_rate) / owned
        return ratio > 2

    @classmethod
    def weigh(cls, planet):
        weight = Action.weigh(planet)
        return weight * (1 if planet.owner == ME else .7)

    def __init__(self, planet):
        self.universe = planet.universe
        self.planet = planet
        self.backup = planet.incoming_reinforcements
        self.bogies = planet.incoming_enemies

    def engage(self):
        if self.planet not in self.universe.marks and self.universe.quota <= 0:
            log.debug('Will not attack %s - overexpansion' % self.planet)
            return
        growth = self.planet.growth_rate if self.planet.owner & ENEMIES else 0
        base = self.planet.ship_count + 1
        planets = sorted(self.universe.my_planets, key=lambda p: p.distance(self.planet))
        for i in range(len(planets)):
            attackers = planets[:i+1]
            distance = planets[i].distance(self.planet)
            available = sum(p.available(self.planet, distance) for p in attackers)
            attacking = self.opposition(distance)
            reinforcing = self.reinforcements(distance)
            required = base + (distance * growth) + attacking - reinforcing
            if available >= required:
                break
        else:
            log.info('%s FAILED' % self)
            self.planet.conquered_in = None
            self.universe.marks.discard(self.planet)
            return set()
        log.info(self)
        self.planet.conquered_in = distance
        self.universe.marks.add(self.planet)
        self.universe.quota -= self.planet.growth_rate
        if required > 0:
            commit(self.planet, required, attackers, distance)

    def reinforcements(self, distance):
        return sum(f.ship_count for f in self.backup if f.turns_remaining <= distance)

    def opposition(self, distance):
        return sum(f.ship_count for f in self.bogies if f.turns_remaining <= distance)
