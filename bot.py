from itertools import chain
from logging import getLogger
log = getLogger('nate')
from planetwars import BaseBot
from planetwars.player import ENEMIES, ME, NOBODY


class Bot(BaseBot):
    def update(self):
        self.universe.idlers = 0
        enemies = self.universe.enemy_planets
        if not enemies:
            return
        for planet in enemies:
            planet.proximity = 0
        for planet in self.universe.planets - enemies:
            enemy = planet.find_nearest_neighbor(owner=ENEMIES)
            planet.proximity = planet.distance(enemy)

    def quota(self):
        ours = sum(p.growth_rate for p in self.universe.planets if
                p.owner == ME or p.incoming_reinforcements)
        theirs = sum(p.growth_rate for p in self.universe.planets if
                p.owner == ENEMIES or
                p.owner == ME and p.condemned or
                p.owner == NOBODY and p.incoming_enemies)
        return max(theirs - ours + 6, self.universe.idlers / 20)

    def do_turn(self):
        self.update()
        log.debug('ORDERING ACTIONS =====================================')
        actions = sorted(chain(*(p.actions() for p in self.universe.planets)))
        actions = filter(lambda a: log.debug(a.show()) or a.priority > 0, actions)
        log.info('TAKING ACTIONS =====================================')
        for action in actions:
            action.engage()
        for planet in self.universe.my_planets:
            planet.execute()
        for planet in self.universe.planets:
            planet.step()
        self.universe.quota = self.quota()
        log.debug('quota is %d' % self.universe.quota)
