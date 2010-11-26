from itertools import chain
from logging import getLogger
log = getLogger('nate')

from weight import Weight
from issues import MustAbandon, InsufficientFleets
from universe import Universe
from planet import Planet, CONTESTED
from fleet import Fleet

from planetwars import BaseBot, Game
from planetwars.player import ENEMIES
from Queue import PriorityQueue as queue


class Bot(BaseBot):
    def do_turn(self):
        # For each planet, determine what we want to do and how much we want it
        # Greedily try to take all actions
        for action in sorted(p.action() for p in self.universe.planets):
            try:
                action.take()
            except InsufficientFleets:
                action.impossible()
