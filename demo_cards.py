from typing import Callable


class Card:
    def __init__(self, name: str, effect: Callable):
        self.name = name
        self.effect = effect

    def play(self, game):
        self.effect(game)

    def __repr__(self):
        return self.name


def card1_effect(game):
    game.money += 1


def card2_effect(game):
    game.money -= 1


def card3_effect(game):
    game.money = 10


cards = [
    Card("card1", card1_effect),
    Card("card2", card2_effect),
    Card("card3", card3_effect)
]
