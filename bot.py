from itertools import chain
from logging import getLogger
log = getLogger('nate')
from planetwars import BaseBot
from planetwars.player import ENEMIES, ME


class Bot(BaseBot):
    def update(self):
        self.universe.contested = set()
        planets = self.universe.my_planets
        enemies = self.universe.enemy_planets
        firstline = set()
        secondline = set()

        for planet in planets:
            planet.proximity = planet.distance(self if planet.owner & ENEMIES else 
                    planet.find_nearest_neighbor(owner=ENEMIES))
        for enemy in enemies:
            threatened = enemy.find_nearest_neigbor(owner=ME)
            threatened.threats.add(enemy)
            firstline.add(threatened)
        for planet in planets - firstline:
            backup = min(planets - firstline - planet, key=lambda p: p.distance(self))
            distance = planet.distance(backup)
            if distance >= planet.proximity:
                secondline.add(planet)
                planet.threats |= set(e for e in enemies if e.distance(planet) <= distance)


    def do_turn(self):
        self.update()
        log.debug('ORDERING ACTIONS =====================================')
        actions = sorted(chain(*(p.actions() for p in self.universe.planets)))
        actions = filter(lambda a: log.debug(a) or a.priority > 0, actions)
        log.debug('TAKING ACTIONS =====================================')
        for action in actions:
            action.engage()
        for planet in self.universe.my_planets:
            planet.execute()
        for planet in self.universe.my_planets:
            planet.fortify()
        for planet in self.universe.planets:
            planet.step()
