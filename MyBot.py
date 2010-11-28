from planet import Planet
from planetwars import universe
from planetwars import Game
from bot import Bot

class Universe(universe.Universe):
    quota = float('infinity')
    idlers = 0
    marks = set()

Game(Bot, Universe, Planet)
