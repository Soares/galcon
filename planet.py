from logging import getLogger
log = getLogger('nate')

import action
from planetwars import planet
from planetwars.player import ME

class Planet(planet.Planet):
    def action(self):
        self.contracts = {}
        if self.owner == ME:
            return action.Defend(self)
        return action.Conquer(self)

    def fortify(self):
        # TODO: Something. Anything.
        pass

    def available(self, dest, expiration):
        delay = self.distance(dest)
        build_time = expiration - delay
        available = self.ship_count - 1
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
        return available
