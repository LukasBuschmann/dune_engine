from typing import Callable



class Card:
    def __init__(self, name: str, effect: Callable[['Game'], None] = lambda game: None, reveal_effect: Callable[['Game'], None] = lambda game: None, cost: int = 0):
        self.name: str = name
        self.effect: Callable[['Game'], None] = effect
        self.reveal_effect: Callable[['Game'], None] = reveal_effect
        self.cost: int = cost

    def play(self, game: 'Game'):
        self.effect(game)

    def reveal(self, game: 'Game'):
        self.reveal_effect(game)

    def __repr__(self):
        return self.name


class PlotIntrigue:
    def __init__(self, name: str, effect: Callable[['Game'], None], requirements: Callable[['Game'], bool]):
        self.name: str = name
        self.effect: Callable[['Game'], None] = effect
        self.requirements: Callable[['Game'], bool] = requirements

    def play(self, game: 'Game'):
        self.effect(game)

    def is_playable(self, game: 'Game'):
        return self.requirements(game)

    def __repr__(self):
        return self.name


cards = [
    Card("Kwisatz_Haderach", lambda game: setattr(game, "spice", game.spice + 1),  lambda game: setattr(game, "spice", game.spice + 4)  ),
    Card("Fremen", lambda game: setattr(game, "money", game.money + 1)),
    Card("Emperor", lambda game: setattr(game, "money", game.money + 1)),
]

plots = [
    PlotIntrigue("Spice_Harvest",  lambda game: setattr(game, "money", game.money + 1), lambda game: game.money >= 3),
    PlotIntrigue("Attack_on_the_Emperor",  lambda game: (setattr(game, "money", game.spice + 1)), lambda game: game.spice <= 3),
    PlotIntrigue("git_gud",  lambda game: (setattr(game, "to_deploy", game.to_deploy + 2)), lambda game: game.spice <= 3),
    PlotIntrigue("Guild_Heist",  lambda game: setattr(game, "money", game.money + 1), lambda game: True)
]
