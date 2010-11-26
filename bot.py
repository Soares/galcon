from itertools import chain
from logging import getLogger
log = getLogger('nate')

from exception import InsufficientFleets
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
        for contract in chain(*map(self.engage, actions)):
            contract.execute()
        for planet in self.universe.my_planets:
            planet.fortify()

    def engage(self, action):
        try:
            contracts = action.take()
        except InsufficientFleets:
            contracts = action.abort()
        return contracts

Game(Bot, Universe, Planet, Fleet)
