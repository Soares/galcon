import weight
from itertools import chain
from logging import getLogger
log = getLogger('nate')

from contract import Contract
from exception import InsufficientFleets
from planetwars.player import ME, ENEMIES

class Action(object):
    def __init__(self, planet):
        self.universe = planet.universe
        self.planet = planet
        self.contracts = set()

    def engage(self):
        try:
            contracts = self.take()
        except InsufficientFleets:
            contracts = self.abort()
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
        return '%s: %s %s' % (int(self.priority), self.__class__.__name__, self.planet)


class Commitment(Action):
    def take(self, attackers, needed, time):
        for planet in sorted(attackers, key=lambda p: -p.proximity):
            fleets = min(needed, planet.available(self.planet, time))
            self.commit(planet, self.planet, fleets, time)
            needed -= fleets
            if not needed: break
        else:
            raise InsufficientFleets
        return self.contracts


class MultiAction(Action):
    def take(self):
        return list(chain(*(a.take() for a in self.actions)))

    def abort(self):
        return list(chain(*[a.abort() for a in self.actions]))


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

    def take(self):
        return super(OpposeFleet, self).take()



class Defend(MultiAction):
    @property
    def priority(self):
        return weight.weigh_defend(self) * 18

    def __init__(self, planet):
        super(Defend, self).__init__(planet)
        fleets = planet.attacking_fleets
        self.actions = [OpposeFleet(planet, f) for f in fleets]
        self.forces = sum(f.ship_count for f in fleets)

    def __repr__(self):
        return super(Defend, self).__repr__() + ' (against %s)' % self.forces


class Reinforce(MultiAction):
    # TODO: if the first request fails, make a lighter one
    # (override engage)

    @property
    def priority(self):
        return weight.weigh_reinforce(self) * 13

    def __init__(self, planet):
        super(Reinforce, self).__init__(planet)
        ours = self.universe.find_fleets(owner=ME, destination=planet)
        time = max(f.turns_remaining for f in ours) if ours else 0
        fleets = planet.ship_count + (planet.growth_rate * time) + 1
        fleets -= sum(f.ship_count for f in ours)
        self.fleets, self.time = fleets, time
        self.actions = [Request(planet, fleets, time)] if fleets > 0 else []
        for fleet in self.universe.find_fleets(owner=ENEMIES, destination=planet):
            self.actions.append(OpposeFleet(planet, fleet))

    def __repr__(self):
        return super(Reinforce, self).__repr__() + '(with %s by %s)' % (self.fleets, self.time)


class Attack(Commitment):
    @property
    def priority(self):
        return weight.weigh_attack(self) * 10

    def take(self):
        # TODO: sort better, adjust for attackers better
        growth = self.planet.growth_rate if self.planet.owner & ENEMIES else 0
        base = self.planet.ship_count + 1
        planets = sorted(self.universe.my_planets, key=lambda p: p.distance(self.planet))
        for i in range(len(planets)):
            attackers = planets[:i+1]
            distance = planets[i].distance(self.planet)
            available = sum(p.available(self.planet, distance) for p in attackers)
            required = base + (distance * growth)
            if available >= required: break
        else:
            raise InsufficientFleets
        return super(Attack, self).take(attackers, required, distance)

    def __repr__(self):
        neighbor = self.planet.find_nearest_neighbor(owner=ME)
        distance = self.planet.distance(neighbor)
        return super(Attack, self).__repr__() + ' %d' % distance


class Reserve(Action):
    @property
    def priority(self):
        return weight.weigh_reserve(self) * 8

    def __init__(self, planet):
        super(Reserve, self).__init__(planet)
        self.fleets = planet.ship_count / 2

    def take(self):
        available = self.planet.available(self.planet, 0)
        if available < self.fleets: raise InsufficientFleets
        self.commit(self.planet, self.planet, self.fleets, 0)
        return self.contracts

    def __repr__(self):
        return super(Reserve, self).__repr__() + ' (keep %s)' % self.fleets
