from logging import getLogger
from planetwars import BaseBot, Game
from fleets import Fleets, bigger
log = getLogger(__name__)

def order_neutrals(universe):
    neutrals = universe.nobodies_planets
    return sorted(neutrals, cmp=bigger)


class MyBot(BaseBot):
    def do_turn(self):
        # 1. Reinforce planets being attacked
        # 2. Set distance to 1
        # 3. Order planets takable within distance by growth
        # 4. Take as many planets as possible
        # 5. Increase distance and go to 2 until you can't take planets
        # 6. If there were no neutral planets, go for their planets
        fleets = Fleets(self.universe, log)
        fleets.reinforce()
        neutrals = list(order_neutrals(self.universe))
        for i in range(50):
            fleets.increase_range()
            for neutral in neutrals:
                if fleets.can_take(neutral):
                    log.info("Taking %s" % neutral)
                    fleets.take(neutral)
            log.info(fleets.range)
        if not self.universe.nobodies_planets:
            for enemy in self.universe.enemy_planets:
                fleets.conquer(enemy)

Game(MyBot)
