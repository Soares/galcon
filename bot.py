from graph import mark
from itertools import chain
from logging import getLogger
log = getLogger('nate')
from planetwars import BaseBot


class Bot(BaseBot):
    def do_turn(self):
        mark(self.universe.enemy_planets)
        actions = sorted(p.action() for p in self.universe.planets)
        actions = filter(lambda a: a.priority > 0, actions)
        for contract in chain(*(action.engage() for action in actions)):
            log.debug('\t%s' % contract)
            contract.execute()
        for planet in self.universe.my_planets:
            planet.fortify()
