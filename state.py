LOCATIONS = (THEIRS, FRONTLINE, OURS) = (0, 1, 2)


class State:
    # owner = ME | ENEMIES | NOBODY
    # location = THEIRS | FRONTLINE | OURS
    # attacking = TRUE | FALSE
    # attacked = TRUE | FALSE
    # reinforced = TRUE | FALSE

    def __init__(self, planet):
        self.owner = planet.owner
        if planet.frontline:
            self.location = FRONTLINE
        elif planet.in_their_territory():
            self.location = THEIRS
        elif planet.in_our_territory():
            self.location = OURS
        else:
            assert False
        self.attackers = set(planet.attackers)
        self.backup = set(planet.backup)
        self.offense = set(planet.offense)
