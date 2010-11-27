from itertools import chain
from logging import getLogger
log = getLogger('nate')
from planetwars import BaseBot
from planetwars.player import ENEMIES


class Bot(BaseBot):
    def update(self):
        planets = self.universe.my_planets
        enemies = self.universe.enemy_planets

        for planet in planets:
            enemy = planet.find_nearest_neighbor(owner=ENEMIES)
            planet.proximity = planet.distance(enemy)
            planet.contracts = {}
        for planet in self.universe.nobodies_planets:
            enemy = planet.find_nearest_neighbor(owner=ENEMIES)
            if enemy: planet.proximity = planet.distance(enemy)
        for planet in enemies:
            planet.proximity = 0
            planet.safety = 0

        current = set(enemies)
        mine = set(self.universe.my_planets | self.universe.nobodies_planets)
        while mine:
            safer = set()
            for unsafe in current:
                planet = sorted(mine, key=lambda p: p.distance(unsafe))[0]
                planet.safety = unsafe.safety + 1
                safer.add(planet)
            mine -= safer
            current = safer


    def do_turn(self):
        self.update()
        actions = sorted(chain(*(p.actions() for p in self.universe.planets)))
        log.debug('ORDERING ACTIONS =====================================')
        for action in actions:
            log.debug(action)
        actions = filter(lambda a: a.priority > 0, actions)
        log.debug('TAKING ACTIONS =====================================')
        for contract in chain(*(action.engage() for action in actions)):
            contract.execute()
        for planet in self.universe.my_planets:
            planet.fortify()
