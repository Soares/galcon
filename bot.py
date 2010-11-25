from itertools import chain
from logging import getLogger
from planetwars import BaseBot, Game
from fleets import Fleets, bigger
from planetwars.player import ME, ENEMY
from exceptions import MustAbandon, InsufficientFleets
log = getLogger(__name__)

def order_neutrals(universe):
    neutrals = universe.nobodies_planets
    return sorted(neutrals, cmp=bigger)


class MustAbandon(Exception):
    pass


class InsufficientFleets(Exception):
    pass


class MyBot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(MyBot, self).__init__(*args, **args)

    def do_turn(self):
        # 1. For each newly issued fleet to your planets,
        #   issue a commitment to stop it
        # 2. For each newly issued fleet to your neutrals,
        #   issue a commitment to stop it
        # 3. Issue commitments to new neutrals
        # 4. Update all bids
        universe = self.universe
        planets = universe.my_planets
        en_route = lambda n: universe.find_fleets(destination=n, owner=ME)
        contests = filter(en_route, universe.nobodies_planets)
        attacking = universe.new_fleets(owner=ENEMY, destination=planets)
        contesting = universe.new_fleets(owner=ENEMY, destination=contests)
        for fleet in chain(attacking, contesting):
            fleet.mark()
            try:
                fleet.destination.commit_against(fleet)
            except MustAbandon:
                fleet.destination.abandon_to(fleet)
        for target in self.targets():
            try:
                target.conquer()
            except InsufficientFleets:
                continue

        fleets = Fleets(self.universe, log)
        fleets.reinforce()
        neutrals = list(order_neutrals(self.universe))
        for i in range(50):
            fleets.increase_range()
            for neutral in neutrals:
                if fleets.can_take(neutral):
                    log.info("Taking %s" % neutral)
                    fleets.take(neutral)
            log.info(fleets.range)
        if not self.universe.nobodies_planets:
            for enemy in self.universe.enemy_planets:
                fleets.conquer(enemy)

Game(MyBot)
