from typing import List, Callable
class Location:
    def __init__(self, name: str, requirement: Callable[['Game'], bool], effect: Callable[['Game'], None]):
        self.name: str = name
        self.requirement: Callable[['Game'], bool] = requirement
        self.effect: Callable[['Game'], None] = effect
        self.is_occupied: bool = False

    def occupy(self, game: 'Game'):
        self.is_occupied = True
        self.effect(game)
    def __repr__(self):
        return self.name

def carthag(game: 'Game'):
    game.spice += 1
    game.to_deploy += 4
    game.garrison += 2

locations = [
    Location("Arrakeen", lambda game: game.money >= 3, lambda game: setattr(game, "money", game.money + 1)),
    Location("Carthag", lambda game: game.spice >= 2, carthag),
    Location("Hagga_Basin", lambda game: game.money >= 1, lambda game: setattr(game, "money", game.money + 1)),
    Location("Shield_Wall", lambda game: True, lambda game: setattr(game, "spice", game.spice + 1)),
]