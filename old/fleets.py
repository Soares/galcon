from planetwars import player

bigger = lambda p1, p2: cmp(p2.growth_rate, p1.growth_rate)

class Fleets(object):
    range = 0

    def __init__(self, universe, log):
        self.log = log
        self.universe = universe
        self.planets = universe.my_planets

    def reinforce(self):
        # Send troops to reinforce any planets that they're attacking
        ## Improvement: make this actually do something
        pass

    def required(self, planet):
        # Return the number of fleets necessary to take planet safely
        ## Improvement: make this work for enemies, make this send a buffer
        return planet.ship_count + 1

    def can_take(self, neutral):
        # Return true if we can take the neutral planet
        fleets = 0
        if self.universe.find_fleets(destination=neutral, owner=player.ME):
            return False
        for planet in self.planets:
            if planet.distance(neutral) <= self.range:
                fleets += planet.ship_count
        return fleets >= self.required(neutral)

    def take(self, neutral):
        # Conquer a neutral planet
        ## Improvement: choose fleets from planets intelligently
        required = self.required(neutral)
        for planet in self.planets:
            if planet.distance(neutral) <= self.range:
                fleets = min(planet.ship_count, required)
                required -= fleets
                planet.send_fleet(neutral, fleets)
                if not required:
                    break

    def conquer(self, enemy):
        # Conquer an enemy planet
        ## Improvement: make a better heuristic for number of fleets to send
        if self.universe.find_fleets(destination=enemy, owner=player.ME):
            return False
        required = self.required(enemy) * 2
        sent = 0
        for i in range(50):
            if sent >= required: return
            for planet in self.planets:
                if planet.ship_count < 10: continue
                if planet.distance(enemy) > range: continue
                sent += int(planet.ship_count / 2)
                planet.send_fleet(enemy, planet.ship_count / 2)

    def increase_range(self):
        self.range += 1
