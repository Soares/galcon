from itertools import chain
from logging import getLogger
log = getLogger('nate')

from contract import Contract
from exception import InsufficientFleets
from planetwars.player import ME, ENEMIES

class Action(object):
    priority = 1

    def __init__(self, planet):
        self.universe = planet.universe
        self.planet = planet
        self.contracts = set()

    def engage(self):
        try:
            contracts = self.take()
        except InsufficientFleets:
            contracts = self.abort()
            log.info("Couldn't %s" % self)
        else:
            log.info(self)
        return contracts

    def commit(self, source, dest, amount, time):
        if not amount: return None
        contract = Contract(source, dest, amount, time)
        self.contracts.add(contract)
        return contract

    def take(self):
        # Start with the back planets
        # Find guys who can send people here
        # Make them do it
        return self.contracts

    def abort(self):
        for contract in self.contracts:
            contract.abort()
        return ()

    def __lt__(self, other):
        return self.priority > other.priority

    def __repr__(self):
        return '%s: %s (%s)' % (self.__class__.__name__, self.planet, self.priority)


class Commitment(Action):
    def take(self, attackers, needed, time):
        for planet in sorted(attackers, key=lambda p: p.safety):
            fleets = min(needed, planet.available(self.planet, time))
            self.commit(planet, self.planet, fleets, time)
            needed -= fleets
            if not needed: break
        else:
            raise InsufficientFleets
        return self.contracts


class Request(Commitment):
    def __init__(self, planet, fleets, time):
        super(Request, self).__init__(planet)
        self.fleets = fleets
        self.time = time

    def take(self):
        return super(Request, self).take(self.universe.my_planets, self.fleets, self.time)



class OpposeFleet(Request):
    def __init__(self, planet, fleet):
        ours = planet.universe.find_fleets(owner=ME, destination=planet)
        sent = sum(f.ship_count for f in ours if f.opposition == fleet)
        super(OpposeFleet, self).__init__(planet, fleet.ship_count - sent, fleet.turns_remaining)
        self.fleet = fleet

    def commit(self, *args, **kwargs):
        contract = super(OpposeFleet, self).commit(*args, **kwargs)
        if contract: contract.oppose(self.fleet)


class Attack(Commitment):
    def __init__(self, planet):
        super(Attack, self).__init__(planet)
        self.priority = planet.growth_rate

    def take(self):
        # TODO: sort better, adjust for attackers better
        growth = self.planet.growth_rate if self.planet.owner == ENEMIES else 0
        base = self.planet.ship_count + 1
        planets = sorted(self.universe.my_planets, key=lambda p: p.distance(self.planet))
        for i in range(len(planets)):
            attackers = planets[:i+1]
            distance = planets[i].distance(self.planet)
            available = sum(p.available(self.planet, distance) for p in attackers)
            needed = base + (distance * growth)
            if available >= needed: break
        else:
            raise InsufficientFleets
        return super(Attack, self).take(attackers, needed, distance)

    def __repr__(self):
        return 'Attack %s (%s)' % (self.planet, self.priority)


class MultiAction(Action):
    def take(self):
        return list(chain(*(a.take() for a in self.actions)))

    def abort(self):
        return list(chain(*[a.abort() for a in self.actions]))



class Defend(MultiAction):
    def __init__(self, planet):
        super(Defend, self).__init__(planet)
        self.actions = [OpposeFleet(planet, f) for f in planet.attacking_fleets]
        self.priority = planet.growth_rate * 100

    def __repr__(self):
        return 'Defend %s (%s)' % (self.planet, self.priority)


class Reinforce(MultiAction):
    def __init__(self, planet):
        super(MultiAction, self).__init__(planet)
        ours = self.universe.find_fleets(owner=ME, destination=planet)
        time = max(f.turns_remaining for f in ours) if ours else 0
        fleets = planet.ship_count + (planet.growth_rate * time) + 1
        fleets -= sum(f.ship_count for f in ours)
        self.fleets = fleets
        self.actions = [Request(planet, fleets, time)] if fleets > 0 else []
        self.priority = planet.growth_rate * 10
        for fleet in self.universe.find_fleets(owner=ENEMIES, destination=planet):
            self.actions.append(OpposeFleet(planet, fleet))

    def __repr__(self):
        return 'Reinforce %s (%s) with %s' % (self.planet, self.priority, self.fleets)
