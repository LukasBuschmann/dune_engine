import itertools
import random
from typing import List

from Cards import cards, plots, shop_cards, foldspace, the_spice_must_flow
from dune_engine.Choice import bool_choice


class Shop:
    def __init__(self):
        # Gets Card Instances for all cards in cards that are not in static_names
        self.draw_pile: List['CardInstance'] = list(
            itertools.chain.from_iterable(card.get_instances() for card in cards))
        random.shuffle(self.draw_pile)
        self.intrigues: List['IntrigueInstance'] = list(
            itertools.chain.from_iterable(plot.get_instances() for plot in plots))
        random.shuffle(self.intrigues)
        # Gets Card Instances for names defined in static_names
        self.imperium_row: List['CardInstance'] = list(
            itertools.chain.from_iterable(card.get_instances() for card in shop_cards))
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

    def get_cards_in_shop(self):  # ToDo: fix this to contain static cards as well
        return self.imperium_row

    def get_card(self, card: 'CardInstance', player: 'Player'):
        self.imperium_row.remove(card)
        self.refill()
        if player.recruitment:
            choice = bool_choice.resolve(player)
            if choice:
                player.deck.append(card)
                return
        player.discard_pile.append(card)

    def shop_buy(self, card: 'CardInstance', player: 'Player'):
        actual_cost = card.persuasion_cost
        if card is the_spice_must_flow:
            if player.guild_bankers:
                actual_cost -= 3

        player.change_persuasion(-actual_cost)
        card.acquisition_effect(player)

        self.get_card(card, player)

    def shop_can_buy(self, card: 'CardInstance', player: 'Player'):
        if card is the_spice_must_flow:
            if player.guild_bankers:
                return player.persuasion >= card.persuasion_cost - 3
        return card in self.imperium_row and player.persuasion >= card.persuasion_cost
