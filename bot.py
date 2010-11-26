from itertools import chain
from logging import getLogger
log = getLogger('nate')

from universe import Universe
from planet import Planet
from fleet import Fleet

from planetwars import BaseBot, Game


class Bot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.actions = dict((p, p.action()) for p in self.universe.planets)
        self.reactions = set()
        self.owned = set(p.id for p in self.universe.my_planets)

    def do_turn(self):
        actions = sorted(p.action() for p in self.universe.planets)
        actions = filter(lambda a: a.priority > 0, actions)
        for contract in chain(*(action.engage() for action in actions)):
            log.debug('\t%s' % contract)
            contract.execute()
        for planet in self.universe.my_planets:
            planet.fortify()

Game(Bot, Universe, Planet, Fleet)
