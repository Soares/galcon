from contract import Contract

GROWTH_RATE = 5
CONTRACT_COST = 3
OUR_FLEETS = 1
ENEMY_FLEETS = 3


class Action:
    def __init__(self, planet):
        self.planet = planet
        self.contract = self.create_contract()

    def apply(self):
        return self.contract.seal()

    @property
    def weight(self):
        return self.WEIGHT * self.score()

    def __lt__(self, other):
        return self.weight < other.weight


class ReinforceOurs(Action):
    WEIGHT = 10

    def create_contract(self):
        fleets, time = self.planet.necessary_backup
        return Contract(self.planet, fleets, time)

    def score(self):
        g = self.planet.growth_rate * GROWTH_RATE
        c = self.contract.cost * CONTRACT_COST
        f = self.planet.ship_count * OUR_FLEETS
        return g + c + f

    def apply(self):
        try:

class ReinforceContested(Action):
    WEIGHT = 5

class ConquerInner(Action):
    WEIGHT = 7

class Advance(Action):
    WEIGHT = 3

# TODO: Add fortifications and abandonments
