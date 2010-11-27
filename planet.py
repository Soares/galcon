from logging import getLogger
log = getLogger('nate')

import action
from planetwars import planet
from planetwars.player import ME, NOBODY

class Planet(planet.Planet):
    def actions(self):
        if self.owner == ME:
            yield action.Reserve(self)
            yield action.Defend(self)
        elif self.universe.find_fleets(owner=ME, destination=self):
            yield action.Reinforce(self)
        else:
            yield action.Attack(self)

    def fortify(self):
        # TODO: Something. Anything. Not this.
        nearby = self.universe.find_planets(owner=ME | NOBODY) - self
        contested = lambda p: self.universe.find_fleets(owner=ME, destination=p)
        forward = lambda p: p.safety > self.safety
        option = lambda p: forward(p) and (p.owner == ME or contested(p))
        ordered = sorted(filter(option, nearby), key=lambda p: p.distance(self))
        if not ordered: return
        target = ordered[0]
        available = self.available(target)
        if available: self.send_fleet(target, available)

    def available(self, dest, expiration=None):
        delay = self.distance(dest)
        if expiration is None: expiration = delay
        build_time = expiration - delay
        if build_time < 0: return 0
        available = self.ship_count
        available += build_time * self.growth_rate
        steps = max(self.contracts.keys()) if self.contracts else 0
        future_growth = 0
        for i in range(steps + 1):
            if i > build_time:
                future_growth += self.growth_rate
            for contract in self.contracts.get(i, set()):
                future_growth -= contract.fleets
            if future_growth < 0:
                available += future_growth
                future_growth = 0
        return max(0, available)
