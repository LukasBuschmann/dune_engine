from transitions import Machine
from typing import List, Set, ClassVar, Any
import random

from enums import Icon, TurnType, Faction
import Effect

class Player(object):

    def __init__(self, game: 'Game'):

        self.solari: int = 20
        self.spice: int = 20
        self.game: 'Game' = game
        self.hand_cards: List['Card'] = self.game.cards
        self.hand_plot_cards: List['Card'] = self.game.plots
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
        self.current_plot = None
        self.open_location_choices: List[Any] = []
        self.decided_location_choices: List[Any] = []
        self.current_choicing: str = None
        self.influence = {faction: 6 for faction in Faction}
        self.influence[Faction.FREMEN] = 0


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


    def get_influence_increase_possible_for(self, n):
       return set(map(lambda t: t[0] ,filter(lambda faction:  faction[1] + n <= self.game.max_influence, self.influence.items())))
    def change_influence(self, faction: Faction, n: int):
        if self.influence[faction] + n > self.game.max_influence:
            raise Exception("Influence cap surpassed!")
        if self.influence[faction] + n < 0:
            raise Exception("Influence cannot be negative!")
        self.influence[faction] += n
        if n > 0:
            print(f"+{faction}: {n}")
        else:
            print(f"-{faction}: {n}")

    def add_icons(self, icons: List[Icon]):
        self.icons.update(icons)
    def draw(self):
        if len(self.deck) == 0:
            random.shuffle(self.discard_pile)
            self.deck = self.discard_pile
            self.discard_pile = []
        card = self.deck.pop()
        self.hand_cards.append(card)

    def change_spice_solari(self, spice: int, solari: int):
        self.change_spice(spice)
        self.change_solari(solari)
    def change_spice(self, n: int):
        self.spice += n
        if n > 0:
            print(f"+Spice: {n}")
        else:
            print(f"-Spice: {n}")

    def change_solari(self, n: int):
        self.solari += n
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
        return self.solari >= card.cost and card in self.game.shop

    def buy(self, card: 'Card'):
        self.solari -= card.cost
        self.game.shop.remove(card)
        self.hand_cards.append(card)


    def reveal_current_card(self):
        self.current_card = self.hand_cards.pop()
        self.open_choices = self.current_card.reveal_effect.choices


    def reveal(self):
        self.has_revealed = True
        self.current_choicing = 'reveal'

    def done_reveal(self):
        self.current_choicing = None

    def can_return_to_by_plot(self, plot: 'PlotIntrigue', state: str):
        return self.plot_is_playable(plot) and self.was_last_state(state)

    def reset_last_state(self):
        self.last_state = None
    def plot_is_playable(self, plot: 'PlotIntrigue'):
        if not plot in self.hand_plot_cards:
            return False
        return plot.requirement.is_met(self.game)



    def is_playing_trivial_card(self):
        return self.current_card.agent_effect.__class__ == Effect.Effect

    def play_current_card(self):
        self.current_card.play(self.game)
        self.current_card = None
        self.current_location = None

    def has_playable_plot(self):
        for plot in self.hand_plot_cards:
            if plot.requirement.is_met(self.game):
                return True
        return False

    def set_last_state(self, state: str):
        self.last_state = state

    def has_playable_card(self):
        for card in self.hand_cards:
            if self.is_playable_card(card):
                return True
        return False
    def location_available_for_card(self, location: 'Location', card: 'Card'):
            return (location.requirement.is_met(self.game)
                    and len(location.icons.intersection(card.icons.union(self.icons))) != 0
                    and not location.is_occupied)
    def location_available(self, location: 'Location'):
        return location.requirement.is_met(self.game) and not location.is_occupied

    def is_playable_card(self, card: 'Card'):
        if not card in self.hand_cards:
            return False
        for location in self.game.locations:
            if self.location_available_for_card(location, card):
                return True
        return False

    def reset(self):
        self.has_revealed = False
        self.to_deploy = 0
        self.in_combat = 0
        self.current_card = None
        self.icons = set()
        self.discard_pile.extend(self.played_cards)
        self.played_cards = []
        self.to_retreat = 0
        self.last_state = 'start'
        if self.has_revealed and len(self.hand_cards) != 0:
            raise Exception("Player still has cards in hand after turn!")

        self.draw()
        self.draw()

    # Picking
    def pick_plot(self, plot: 'PlotIntrigue'):
        self.current_plot = plot
        self.hand_plot_cards.remove(plot)
        self.open_choices = plot.effect.choices
        self.current_choicing = 'plot'

    def pick_card(self, card: 'Card'):
        self.current_card = card
        self.hand_cards.remove(card)
        self.played_cards.append(card)
        self.open_choices = card.agent_effect.choices
        self.icons.update(card.icons)

    def pick_location(self, location: 'Location'):
        self.current_location = location
        self.open_location_choices = location.effect.choices
        location.occupy()
        location.requirement.fulfill(self.game)
        if len(location.effect.choices) != 0:
            self.current_choicing = 'location'
        else:
            self.current_choicing = 'agent'

    # Choicing
    def has_choices(self):
        return len(self.open_choices) != 0
    def has_no_choices(self):
        return len(self.open_choices)== 0
    def has_location_choices(self):
        return len(self.open_location_choices) != 0
    def has_no_location_choices(self):
        return len(self.open_location_choices) == 0

    def can_evaluate_plot(self):
        return self.has_no_choices() and self.current_choicing == 'plot'
    def can_evaluate_reveal(self):
        return self.has_no_choices() and self.current_choicing == 'reveal'
    def can_evaluate_agent_location(self):
        return self.has_no_choices() and self.has_no_location_choices() and self.current_choicing == 'agent'

    def can_make_choice(self, choice: Any, choice_type: 'ChoiceType'):
        if len(self.open_choices) == 0 or self.current_choicing == 'location':
            return False
        return self.open_choices[0].is_allowed(choice, choice_type, self.game)

    def can_make_location_choice(self, choice: Any, choice_type: 'ChoiceType'):
        if len(self.open_location_choices) == 0 or self.current_choicing != 'location':
            return False
        return self.open_location_choices[0].is_allowed(choice, choice_type, self.game)


    def make_choice(self, choice: Any):
        evaluated_choice = self.open_choices[0]
        self.decided_choices.append(choice)

        if evaluated_choice.triggers_break(self.game):
            self.open_choices = []
        else:
            self.open_choices = self.open_choices[1:]

    def make_location_choice(self, choice: Any):
        evaluated_choice = self.open_location_choices[0]
        self.decided_location_choices.append(choice)

        if evaluated_choice.triggers_break(self.game):
            self.open_location_choices = []
        else:
            self.open_location_choices = self.open_location_choices[1:]

        if self.has_no_location_choices():
            self.current_choicing = 'agent'


    def evaluate_choices_agent_location(self):
        self.current_card.agent_effect.execute(self.game, self.decided_choices)
        self.current_location.effect.execute(self.game, self.decided_location_choices)
        self.played_cards.append(self.current_card)
        self.current_location.occupy()
        self.decided_choices = []
        self.decided_location_choices = []
        self.current_card = None
        self.current_location = None
        self.current_choicing = None

    def evaluate_choices_reveal(self):
        self.current_card.reveal_effect.execute(self.game, self.decided_choices)
        self.played_cards.append(self.current_card)
        self.decided_choices = []
        self.current_card = None

    def evaluate_choices_plot(self):
        self.current_plot.effect.execute(self.game, self.decided_choices)
        self.current_plot = None
        self.current_choicing = None
        self.reset_last_state()

