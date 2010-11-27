from planetwars.player import ME, ENEMIES
# Beware, magic numbers lie ahead
# TODO: Add something that benefits "cutting them off at the choke"
# TODO: Expand to the farthest equidistant

# Planet Weights (0-1)
def weigh_growth(planet):
    return planet.growth_rate / 5.0

def weigh_distance(planet):
    # 0-3 Range
    neighbor = planet.find_nearest_neighbor(owner=ME)
    distance = planet.distance(neighbor)
    return 7.0 / max(7, distance)

def weigh_cost(planet):
    cost = planet.ship_count
    if planet.owner == ENEMIES:
        initiator = planet.find_nearest_neigbor(owner=ME)
        distance = planet.distance(initiator)
        cost += distance * planet.growth_rate * 2
    if not cost: return 4
    return 4.0 / max(4, cost)

def weigh_steal(planet):
    return 1 if planet.owner & ENEMIES else 0

def weigh_contested(planet):
    if planet.owner & ENEMIES: return 0
    fleets = planet.universe.find_fleets(owner=ENEMIES, destination=planet)
    return 1 if fleets else 0

def weigh_safety(planet):
    return max(planet.safety, 9) / 9.0

def weigh_proximity(planet):
    return 10.0 / min(10, planet.proximity)

def weigh_attackers(planet):
    attackers = planet.universe.find_fleets(owner=ENEMIES, destination=planet)
    attacking = sum(f.ship_count for f in attackers)
    return 20.0 / max(20, attacking)

def weigh_commitment(planet):
    dispatched = planet.universe.find_fleets(owner=ME, destination=planet)
    fleets = sum(f.ship_count for f in dispatched)
    return min(120, fleets) / 120


# Action weights (0-100)
def weigh_defend(action):
    g = weigh_growth(action.planet)
    s = weigh_safety(action.planet)
    a = weigh_attackers(action.planet)
    return (50*g) + (30*s) + (20*a)

def weigh_reinforce(action):
    g = weigh_growth(action.planet)
    s = weigh_safety(action.planet)
    c = weigh_commitment(action.planet)
    t = weigh_contested(action.planet)
    e = weigh_steal(action.planet)
    return (30*g) + (20*s) + (10*c) + (20*t) + (20*e)

def weigh_attack(action):
    g = weigh_growth(action.planet)
    d = weigh_distance(action.planet)
    s = weigh_safety(action.planet)
    c = weigh_cost(action.planet)
    t = weigh_contested(action.planet)
    e = weigh_steal(action.planet)
    return (10*g) + (35*d) + (15*s) + (20*c) + (10*t) + (10*e)

def weigh_reserve(action):
    g = weigh_growth(action.planet)
    p = weigh_proximity(action.planet)
    a = weigh_attackers(action.planet)
    return (60*g) + (30*p) + (10*a)
