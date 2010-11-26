from logging import getLogger
log = getLogger('nate')

from planetwars import universe

class Universe(universe.Universe):
    def __init__(self, *args, **kwargs):
        super(Universe, self).__init__(*args, **kwargs)
