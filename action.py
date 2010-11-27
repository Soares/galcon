from logging import getLogger
log = getLogger('nate')

from planetwars.player import ENEMIES

class InsufficientFleets(Exception):
    pass


def commit(planet, needs, sources, time):
    locks = set()
    for source in sorted(sources, key=lambda p: -p.proximity):
        fleets = min(needs, source.available(planet, time))
        locks.add((source, planet, fleets, time))
        needs -= fleets
        if not needs: break
    else:
        raise InsufficientFleets
    for (source, planet, fleets, time) in locks:
        source.lock(planet, fleets, time)


class Defend:
    def __init__(self, planet):
        self.planet = planet
        self.delay = planet.conquered_in + 1 if planet.conquering else 0
        self.defenders = planet.universe.my_planets - planet
        unopposed = lambda f: f.turns_remaining > self.delay
        self.bogies = sorted(filter(unopposed, planet.incoming_enemies),
                key=lambda f: f.turns_remaining)

    def engage(self):
        for bogie in self.bogies:
            try:
                self.oppose(bogie)
            except InsufficientFleets:
                self.planet.condemn_in = bogie.turns_remaining
                return

    def oppose(self, fleet):
        return commit(self.planet, fleet.ship_count, self.defenders, fleet.turns_remaining)


class Attack:
    def __init__(self, planet):
        self.planet = planet
        self.backup = planet.incoming_reinforcements
        self.bogies = planet.incoming_enemies

    def engage(self):
        # TODO: sort better, adjust for attackers better
        growth = self.planet.growth_rate if self.planet.owner & ENEMIES else 0
        base = self.planet.ship_count + 1
        planets = sorted(self.universe.my_planets, key=lambda p: p.distance(self.planet))
        for i in range(len(planets)):
            attackers = planets[:i+1]
            distance = planets[i].distance(self.planet)
            available = sum(p.available(self.planet, distance) for p in attackers)
            attacking = self.opposition(distance)
            reinforcing = self.reinforcments(distance)
            required = base + (distance * growth) + attacking - reinforcing
            if available > required: break
        else:
            self.planet.conquered_in = None
            return set()
        self.planet.conquered_in = distance
        commit(self.planet, required, attackers, distance)

    def reinforcements(self, distance):
        return sum(f.ship_count for f in self.backup if f.turns_remaining <= distance)

    def opposition(self, distance):
        return sum(f.ship_count for f in self.bogies if f.turns_remaining <= distance)
