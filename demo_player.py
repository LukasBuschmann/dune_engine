from transitions import Machine
from typing import List, Set, ClassVar, Any
import random

from demo_cards import BinaryDecisionEffectWithRequirement
from enums import Icon, TurnType
import Effect

class Player(object):

    def __init__(self, game: 'Game'):

        self.money: int = 20
        self.spice: int = 20
        self.game: 'Game' = game
        self.hand_cards: List['Card'] = self.game.cards
        self.hand_plot_cards: List['Card'] = self.game.plots[:-1]
        self.has_revealed: bool = False
        self.discard_pile: List['Card'] = []
        self.garrison: int = 2
        self.in_combat: int = 0
        self.to_deploy: int = 0
        self.icons: Set[Icon] = set()
        self.current_card: 'Card' = None
        self.last_state: str = None
        self.to_retreat: int = 0
        self.played_cards: List['Card'] = []
        self.deck: List['Card'] = self.game.cards[-1:]
        self.current_location: 'Location' = None
        self.open_choices: List[Any] = []
        self.decided_choices: List[Any] = []

    def has_playable_card_with_agent_effect(self, effect_type: ClassVar):
        for card in self.hand_cards:
            if card.agent_effect.__class__ == effect_type:
                if isinstance(card.agent_effect, Effect.EffectWithRequirement):
                    effect: Effect.EffectWithRequirement = card.agent_effect
                    if effect.requirement_met(self.game):
                        return True
                else:
                    return True
        return False

    def draw(self):
        if len(self.deck) == 0:
            random.shuffle(self.discard_pile)
            self.deck = self.discard_pile
            self.discard_pile = []
        card = self.deck.pop()
        self.hand_cards.append(card)

    def change_spice(self, n: int):
        self.spice += n
        if n > 0:
            print(f"+Spice: {n}")
        else:
            print(f"-Spice: {n}")

    def change_money(self, n: int):
        self.money += n
        if n > 0:
            print(f"+Money: {n}")
        else:
            print(f"-Money: {n}")

    def change_garrison(self, n: int):
        self.garrison += n
        if n > 0:
            print(f"+Garrison: {n}")
        else:
            print(f"-Garrison: {n}")

    def change_to_deploy(self, n: int):
        self.to_deploy += n
        if n > 0:
            print(f"+To Deploy: {n}")
        else:
            print(f"-To Deploy: {n}")

    def change_in_combat(self, n: int):
        self.in_combat += n
        if n > 0:
            print(f"+In Combat: {n}")
        else:
            print(f"-In Combat: {n}")

    def change_to_retreat(self, n: int):
        self.to_retreat += n
        if n > 0:
            print(f"+To Retreat: {n}")
        else:
            print(f"-To Retreat: {n}")

    def has_hand_cards(self):
        return len(self.hand_cards) != 0

    def can_change_troop_count(self, n: int):
        if n > 0:
            return self.to_deploy >= n and self.garrison >= n
        else:
            n = -n
            return self.to_retreat >= n and self.in_combat >= n
    def deploy(self, n: int):
        self.to_deploy -= n
        self.garrison -= n
        self.in_combat += n

    def was_last_state(self, state: str):
        return self.last_state == state

    def can_buy(self, card: 'Card'):
        return self.money >= card.cost and card in self.game.shop

    def buy(self, card: 'Card'):
        self.money -= card.cost
        self.game.shop.remove(card)
        self.hand_cards.append(card)


    def reveal(self):
        self.has_revealed = True
        # reveal trivial cards
        trivial_reveal = list(filter(lambda card: card.reveal_effect.__class__ != BinaryDecisionEffectWithRequirement, self.hand_cards))
        [card.reveal_effect.execute(self.game) for card in trivial_reveal]
        self.played_cards.extend(trivial_reveal)
        [self.hand_cards.remove(card) for card in trivial_reveal]
        # reveal decision cards that are not allowed to be decided positively
        for card in self.hand_cards:
            effect: BinaryDecisionEffectWithRequirement = card.reveal_effect
            if not effect.decision_possible(self.game):
                self.played_cards.append(card)
                card.reveal_effect.execute(self.game)
                self.hand_cards.remove(card)

    def make_reveal_decision(self, card: 'Card', decision: bool):
        effect: BinaryDecisionEffectWithRequirement = card.reveal_effect
        effect.execute_decision(self.game, decision)
        self.played_cards.append(card)
        self.hand_cards.remove(card)
        self.current_card = None

    def can_make_reveal_decision(self, card: 'Card'):
        if card not in self.hand_cards:
            return False
        return card.reveal_effect.decision_possible(self.game) and card == self.hand_cards[0]


    def can_return_to_by_plot(self, plot: 'PlotIntrigue', state: str):
        return self.plot_is_playable(plot) and self.was_last_state(state)
    def plot_is_playable(self, plot: 'PlotIntrigue'):
        return plot.is_playable(self.game) and plot in self.hand_plot_cards

    def play_plot(self, plot: 'PlotIntrigue'):
        plot.play(self.game)
        self.hand_plot_cards.remove(plot)

    def pick_card(self, card: 'Card'):
        self.current_card = card
        self.hand_cards.remove(card)
        self.played_cards.append(card)

    def pick_location(self, location: 'Location'):
        self.current_location = location
        location.occupy(self.game)

    def is_playing_trivial_card(self):
        return self.current_card.agent_effect.__class__ == Effect.Effect

    def play_current_card(self):
        self.current_card.play(self.game)
        self.current_card = None
        self.current_location = None

    def has_playable_plot(self):
        for plot in self.hand_plot_cards:
            if plot.is_playable(self.game):
                return True
        return False


    def pick_card(self, card: 'Card'):
        self.current_card = card
        self.hand_cards.remove(card)
        self.played_cards.append(card)

    def set_last_state(self, state: str):
        self.last_state = state

    def has_playable_card(self):
        for card in self.hand_cards:
            if self.is_playable_card(card):
                return True
        return False
    def location_available_for_card(self, location: 'Location', card: 'Card'):
            return location.requirement.is_met(self.game) and len(location.icons.intersection(card.icons.union(self.icons))) != 0 and not location.is_occupied
    def location_available(self, location: 'Location'):
        return location.requirement.is_met(self.game) and not location.is_occupied

    def is_playable_card(self, card: 'Card'):
        if not card in self.hand_cards:
            return False
        for location in self.game.locations:
            if self.location_available_for_card(location, card):
                return True
        return False

    def pick_choice_card(self, card: 'Card'):
        self.current_card = card
        self.open_choices = card.agent_effect.choices
        self.hand_cards.remove(card)
    def has_choices(self):
        return len(self.open_choices) != 0
    def has_no_choices(self):
        return not self.has_choices()
    def can_make_choice(self, choice: Any, choice_type: 'ChoiceType'):
        if len(self.open_choices) == 0:
            return False
        return self.open_choices[0].is_allowed(choice, choice_type, self.game)
    def make_choice(self, choice: Any):
        self.open_choices = self.open_choices[1:]
        self.decided_choices.append(choice)
    def evaluate_choices(self):
        self.current_card.agent_effect.execute(self.game, self.decided_choices)
        self.decided_choices = []
        self.current_card = None

    def reset(self):
        self.has_revealed = False
        self.to_deploy = 0
        self.in_combat = 0
        self.current_card = None
        self.icons = []
        self.discard_pile.extend(self.played_cards)
        self.played_cards = []
        self.to_retreat = 0
        self.last_state = 'start'
        if self.has_revealed and len(self.hand_cards) != 0:
            raise Exception("Player still has cards in hand after turn!")


        self.draw()
        self.draw()