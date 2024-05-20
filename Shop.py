from typing import Set, List
import random
import itertools
from demo_cards import cards, plots, shop_cards, foldspace
class Shop:
    def __init__(self, game: 'Game'):
        static_names = ['The Spice Must Flow', 'Arrakis Liaison']
        # Gets Card Instances for all cards in cards that are not in static_names
        self.draw_pile: List['CardInstance'] =  list(itertools.chain.from_iterable(card.get_instances() for card in cards))
        random.shuffle(self.draw_pile)
        self.intrigues: List['PlotInstance'] = list(itertools.chain.from_iterable(plot.get_instances() for plot in plots))
        random.shuffle(self.intrigues)
        # Gets Card Instances for names defined in static_names
        self.imperium_row: List['CardInstance'] = list(itertools.chain.from_iterable(card.get_instances() for card in shop_cards))
        while len(self.imperium_row) <= 5:
            self.refill()
        self.reserved_card = None
        self.foldspaces: List['CardInstance'] = foldspace.get_instances()

    def refill(self):
        if len(self.draw_pile) > 0:
            self.imperium_row.append(self.draw_pile.pop())

    def draw_intrigue(self, player: 'Player'):
        if len(self.intrigues) > 0:
            player.intrigues.append(self.intrigues.pop())

    def draw_shop_foldspace(self, player: 'Player'):
        if len(self.foldspaces) > 0:
            player.discard_pile.append(self.foldspaces.pop())
    def get_cards_in_shop(self):
        return self.imperium_row
    def shop_buy(self, card: 'Card', player: 'Player'):
        if card not in self.imperium_row:
            raise Exception("Card not in the imperium row")
        if player.persuasion < card.persuasion_cost:
            raise Exception("Not enough solari")
        self.imperium_row.remove(card)
        self.refill()
        player.discard_pile.append(card)
        player.change_persuasion(-card.persuasion_cost)
        card.acquisition_effect.execute(player.game, []) # We only have choiceless effects

    def shop_can_buy(self, card: 'Card', player: 'Player'):
        return card in self.imperium_row and player.persuasion >= card.persuasion_cost