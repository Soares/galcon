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
        elif self.universe.find_fleets(owner=ME, destination=self):
            return action.Reinforce(self)
        return action.Attack(self)

    def fortify(self):
        # TODO: Something. Anything. Not this.
        pass

    def available(self, dest, expiration):
        delay = self.distance(dest)
        build_time = expiration - delay
        if build_time < 0: return 0
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
        return max(0, available)

    def safety(self):
        # TODO: actually assess planet safety
        return (self.x, self.y)
