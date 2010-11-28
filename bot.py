from itertools import chain
from logging import getLogger
log = getLogger('nate')
from planetwars import BaseBot
from planetwars.player import ENEMIES, ME


class Bot(BaseBot):
    def update(self):
        self.universe.idlers = 0
        mine = self.universe.my_planets
        enemies = self.universe.enemy_planets
        if not enemies or not mine:
            return
        for planet in self.universe.planets:
            planet.safety = planet.distance(
                    planet if planet.owner & ENEMIES
                    else planet.find_nearest_neighbor(owner=ENEMIES))
            planet.proximity = planet.distance(
                    planet if planet.owner == ME
                    else planet.find_nearest_neighbor(owner=ME))
            planet.ourside = planet.safety >= planet.proximity

    def quota(self):
        ours = sum(p.growth_rate for p in self.universe.planets if
                p.owner == ME or p.incoming_reinforcements)
        theirs = sum(p.growth_rate for p in self.universe.planets if
                p.owner == ENEMIES or p.incoming_enemies)
        return max(theirs - ours, self.universe.idlers / 50)

    def do_turn(self):
        self.update()
        log.debug('ORDERING ACTIONS =====================================')
        actions = sorted(chain(*(p.actions() for p in self.universe.planets)))
        actions = filter(lambda a: log.debug(a.show()) or a.priority > 0, actions)
        log.info('TAKING ACTIONS =====================================')
        for action in actions:
            action.engage()
        for planet in sorted(self.universe.my_planets):
            planet.execute()
        for planet in self.universe.planets:
            planet.step()
        self.universe.quota = self.quota()
        log.debug('quota is %d' % self.universe.quota)
