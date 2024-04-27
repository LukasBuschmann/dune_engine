from transitions import Machine
from typing import List, Set

from demo_cards import BinaryDecisionEffectWithRequirement
from enums import Icon

class Player(object):

    def __init__(self, game: 'Game'):

        self.money: int = 0
        self.spice: int = 4
        self.game: 'Game' = game
        self.hand_cards: List['Card'] = self.game.cards[:-1]
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
        """
        certain cards can add tasks to the task queue these will send player to the specific part of the decision machine
        Tasks can be derived of subtasks. If the task is started all subtasks musst be completed before another task
        can be worked on. There is only one level of task hierarchy. The bottom level are elemental tasks meaning all
        the nodes in the decision machine.
        Some cards will be able to throw you into a task, once they are played regardless of other current tasks.
        It is also possible to be prompted to do a task while it is not your turn. This will porbably require a stand-by
        node after the end node of the turn, where a interrupt can be triggered.
        """


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
        # [print(card.reveal_effect.__class__ != BinaryDecisionEffectWithRequirement) for card in self.hand_cards]
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

    def play_current_card_and_occupy(self, location: 'Location'):
        print("doin it")
        self.current_card.play(self.game)
        location.occupy(self.game)
        self.current_card = None

    def has_playable_plot(self):
        for plot in self.hand_plot_cards:
            if plot.is_playable(self.game):
                return True
        return False


    def pick_card(self, card: 'Card'):
        self.current_card = card
        self.hand_cards.remove(card)

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

    # def on_end_turh(self):
    #     self.has_revealed = False
    #     self.to_deploy = 0
    #     self.in_combat = 0
    #     self.current_card = None
    #     self.task_queue = []
    #     self.icons = []