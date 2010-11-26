from itertools import chain
from logging import getLogger
log = getLogger('nate')

from issues import MustAbandon, InsufficientFleets
from universe import Universe
from planet import Planet, CONTESTED
from fleet import Fleet

from planetwars import BaseBot, Game
from planetwars.player import ENEMIES


class Bot(BaseBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    def do_turn(self):
        # 1. For each newly issued fleet to your planets,
        #   issue a commitment to stop it
        # 2. For each newly issued fleet to your neutrals,
        #   issue a commitment to stop it
        # 3. Issue commitments to new neutrals
        # 4. Update all contracts
        universe = self.universe
        planets = universe.my_planets
        committed = filter(lambda n: n.state == CONTESTED,
                universe.nobodies_planets)
        attacking = filter(lambda f: not f.marked,
                universe.find_fleets(owner=ENEMIES, destination=planets))
        contesting = filter(lambda f: not f.marked,
                universe.find_fleets(owner=ENEMIES, destination=committed))
        log.info('Incoming -> ours: %s' % attacking)
        log.info('Incoming -> contest: %s' % contesting)
        for fleet in chain(attacking, contesting):
            fleet.mark()
            try:
                fleet.destination.oppose(fleet)
            except MustAbandon:
                fleet.destination.abandon_to(fleet)
        # TODO: Mark their dests as contested
        neutrals = filter(lambda n: n.state != CONTESTED, universe.nobodies_planets)
        self.expand(self.order(neutrals)) if neutrals else self.agress()
        committed = filter(lambda n: n.state == CONTESTED, universe.nobodies_planets)
        for planet in chain(planets, committed):
            for (turn, contracts) in planet.contracts.contracts.items():
                for contract in contracts:
                    log.debug('%d: %d from %s to %s' % (turn, contract.fleets, planet, contract.dest))
        for planet in chain(planets, committed):
            planet.contracts.step()

    def order(self, neutrals):
        planets = self.universe.my_planets
        log.info('PLANETS: %s' % planets)
        ordered = {}
        for neutral in neutrals:
            distance = min(neutral.distance(p) for p in planets)
            ordered.setdefault(distance, set()).add(neutral)
        log.info('NEUTRAL: %s' % ' '.join(str(p.id) for p in chain(*ordered.values())))
        return sorted((d, sorted(ps,
            key=lambda p: (-p.growth_rate, p.ship_count)))
            for (d, ps) in ordered.items())

    def expand(self, ordered):
        hit_someone = False
        for (range, planets) in ordered:
            log.debug('Considering planets at range %d...' % range)
            attacked = False
            for planet in planets:
                try:
                    planet.conquer()
                except InsufficientFleets:
                    continue
                else:
                    hit_someone = True
                    attacked = True
            if hit_someone and not attacked:
                log.debug('No conquerable planets within range.')
                break

    def agress(self):
        log.info('Beginning agression.')
        for planet in self.universe.my_planets:
            if planet.ship_count <= 12: continue
            neighbor = planet.find_nearest_neighbor(owner=ENEMIES)
            log.info('Attacking %s from %s with %s' % (neighbor, planet, planet.ship_count - 10))
            planet.send_fleet(neighbor, planet.ship_count - 10)

Game(Bot, Universe, Planet, Fleet)
