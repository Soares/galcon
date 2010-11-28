from logging import getLogger
log = getLogger('nate')

from planetwars import universe

class Universe(universe.Universe):
    quota = float('infinity')
    idlers = 0
    marks = set()
