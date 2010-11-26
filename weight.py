# Intuitively, here's how it works:
# 1. First, defend your existing or contested planets
# 2. Then, take cheap inner planets
# 3. Push your front line forwards if it's a sure thing
# 4. Reinforce your front line
from planetwars.player import ME, NOBODY, ENEMIES

# Action Weights
REINFORCE_OURS = 10
TAKE_INNER = 7
REINFORCE_CONTESTED = 5
ADVANCE = 4
FORTIFY = 3

# Overall Weights
GROWTH_RATE = 5
COST = 3
DISTANCE = 2

# Integration Weights
ACTION = 3
OVERALL = 1

# Normalizers
NORMALIZE_GROWTH_RATE = lambda r: r / 5
NORMALIZE_COST = lambda cost: cost / 100
NORMALIZE_DISTANCE = lambda distance: distance / 20

class Weight:
    def __init__(self, planet):
        pass

    def reinforce_ours(planet):
        return 1 if planet.under_attack and planet.owner == ME else 0

    def reinforce_contested(planet):
        return 1 if planet.under_attack and planet.owner == NOBODY else 0

    def take_inner(planet):
        return 1 if planet.owner == NOBODY and planet.is_inner else 0

    def advance(planet):
        return 1 if planet.owner == ENEMIES and planet.is_target else 0

    def fortify(planet):
        return 1 if planet.owner == ME and planet.is_front_line else 0

    def cost(planet):
        neighbor = planet.find_nearest_neighbor(owner=ME)
        return planet.distance(neighbor)

    def score(self, planet):
        if planet.under_attack and planet.owner == ME:
            weight = REINFORCE_OURS

        ro = REINFORCE_OURS * self.reinforce_ours(planet)
        rc = REINFORCE_CONTESTED * self.reinforce_contested(planet)
        ti = TAKE_INNER * self.take_inner(planet)
        av = ADVANCE * self.advace(planet)
        fy = FORTIFY * self.fortify(planet)
        action = ro + rc + ti + av + fy        

        gr = GROWTH_RATE * NORMALIZE_GROWTH_RATE(planet.growth_rate)
        cost = 
        dx = 


    def __lt__(self, other):
        return self.score() < other.score()
