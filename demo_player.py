from transitions import Machine
from typing import List
class Player(object):

    def __init__(self, game: 'Game'):

        self.money: int = 0
        self.spice: int = 0
        self.game: 'Game' = game
        self.hand_cards: List['Card'] = self.game.cards[:-1]
        self.hand_plot_cards: List['Card'] = self.game.plots[:-1]
        self.has_revealed: bool = False
        self.discard_pile: List['Card'] = []
        self.garrison: int = 2
        self.in_combat: int = 0
        self.to_deploy: int = 0

    def can_deploy(self, n: int):
        return self.to_deploy >= n and self.garrison >= n
    def deploy(self, n: int):
        self.to_deploy -= n
        self.garrison -= n
        self.in_combat += n

    def can_buy(self, card: 'Card'):
        return self.money >= card.cost and card in self.game.shop

    def buy(self, card: 'Card'):
        self.money -= card.cost
        self.game.shop.remove(card)
        self.hand_cards.append(card)

    def reveal(self):
        self.has_revealed = True
        [hand_card.reveal(self) for hand_card in self.hand_cards]
        self.discard_pile.extend(self.hand_cards)
        self.hand_cards = []

    def plot_is_playable(self, plot: 'PlotIntrigue'):
        return plot.is_playable(self) and plot in self.hand_plot_cards

    def play_plot(self, plot: 'PlotIntrigue'):
        plot.play(self)
        self.hand_plot_cards.remove(plot)

    def is_playable_to(self, card: 'Card', location: 'Location'):
        return card in self.hand_cards and location.requirement(self) and not location.is_occupied and not self.has_revealed

    def play_card_to(self, card: 'Card', location: 'Location'):
        card.play(self)
        location.occupy(self)
        self.hand_cards.remove(card)
