from logging import getLogger
log = getLogger('nate')

import action
from planetwars import planet
from planetwars.player import ME

class Planet(planet.Planet):
    @property
    def contested(self):
        if self.owner == ME:
            return bool(self.attacking_fleets)
        return bool(self.universe.find_fleets(owner=ME, destination=self))

    def actions(self):
        if self.owner == ME:
            yield action.Reserve(self)
            yield action.Defend(self)
        elif self.contested:
            yield action.Reinforce(self)
        else:
            yield action.Attack(self)

    def fortify(self):
        candidates = filter(lambda p: p.contested, self.universe.planets)
        if not candidates: return
        target = min(candidates, key=lambda p: p.distance(self))
        distance = self.distance(target)
        others = self.universe.my_planets - self
        closer = filter(lambda p: p.distance(target) < distance, others)
        if closer: target = min(closer, key=lambda p: p.distance(self))
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
