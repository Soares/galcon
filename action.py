from itertools import chain
from contract import Contract
from issues import InsufficientFleets
from planetwars.player import ME, ENEMIES

class Action:
    priority = 1

    def __init__(self, planet):
        self.universe = planet.universe
        self.planet = planet
        self.contracts = set()

    def commit(self, source, dest, amount, time):
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


class Commitment(Action):
    def take(self, attackers, needed, time):
        for planet in sorted(attackers, key=lambda p: p.safety):
            fleets = min(planet.available(self, time))
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
        contract.oppose(self.fleet)


class Attack(Commitment):
    def take(self):
        # TODO: sort better
        base = self.planet.ship_count
        growth = self.planet.growth_rate if self.planet.owner == ENEMIES else 0
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


class MultiAction(Action):
    def take(self):
        return chain(a.take() for a in self.actions)

    def abort(self):
        return chain(a.abort() for a in self.actions)



class Defend(MultiAction):
    def __init__(self, planet):
        super(Defend, self).__init__(planet)
        self.actions = [OpposeFleet(planet, f) for f in planet.attacking_fleets]

    def __repr__(self):
        return 'Defend %s (%s)' % (self.planet, self.priority)


class Conquer(MultiAction):
    def __init__(self, planet):
        super(Conquer, self).__init__(planet)
        ours = self.universe.find_fleets(owner=ME, destination=planet)
        ours = filter(lambda f: not f.opposition, ours)
        if ours:
            time = max(f.turns_remaining for f in ours)
            fleets = sum(f.ship_count for f in ours)
            self.actions = [Request(planet, planet.ship_count - fleets, time)]
        else:
            self.actions = [Attack(planet)]
        for fleet in self.universe.find_fleets(owner=ENEMIES, destination=planet):
            self.actions.append(OpposeFleet(planet, fleet))

    def __repr__(self):
        return 'Conquer %s (%s)' % (self.planet, self.priority)
