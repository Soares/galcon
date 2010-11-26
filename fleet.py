from logging import getLogger
log = getLogger('nate')

from planetwars import fleet

class Fleet(fleet.Fleet):
    marked = False

    def mark(self):
        log.info('Marking new enemy fleet %s' % self)
        self.marked = True
