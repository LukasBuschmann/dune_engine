from transitions import Machine
from typing import List, Set, ClassVar, Any
import random
import itertools
from demo_cards import start_cards
from demo_board import faction_rewards
from enums import Icon, Faction, Commander, IntrigueType, GameState, TurnType
import Effect

class Player(object):

    def __init__(self, game: 'Game', commander: Commander):
        self.game: 'Game' = game
        self.commander: Commander = commander

        self.victory_points = 0

        self.solari: int = 20
        self.spice: int = 20
        self.water: int = 1
        self.persuasion: int = 0

        self.agents = 2
        self.max_agents = 2

        self.factions = {faction: {'influence': 0, 't1_reward_received': False, "t2_reward_received": False} for faction in Faction}
        self.alliances = set()

        self.in_high_council = False

        self.garrison: int = 2
        self.in_combat: int = 0
        self.to_deploy: int = 0
        self.to_retreat: int = 0
        self.force: int = 0

        self.icons: Set[Icon] = set()

        self.deck: List['CardInstance'] = list(itertools.chain.from_iterable(card.get_instances() for card in start_cards))
        random.shuffle(self.deck)
        self.played_cards: List['CardInstance'] = []
        self.discard_pile: List['CardInstance'] = []

        self.current_card: 'CardInstance' = None
        self.hand_cards: List['CardInstance'] = []
        [self.draw() for _ in range(5)]

        self.current_intrigue: 'IntrigueInstance' = None
        self.intrigues: List['IntrigueInstance'] = []

        self.current_location: 'Location' = None
        self.revealed: bool = False
        self.is_revealing_turn: bool = False
        self.intrigue_origin_node: str = None

        self.current_choicing: str = None
        self.open_choices: List[Any] = []
        self.decided_choices: List[Any] = []
        self.open_location_choices: List[Any] = []
        self.decided_location_choices: List[Any] = []

        self.has_played_intrigue: bool = False
        self.has_resolved_conflict =   False
        self.conflict_ranking: int = None
        self.str_out = ""
        self.turn_type: TurnType = TurnType.UNDECIDED

    def __repr__(self):
        return self.commander.name
    def __str__(self):
        return self.commander.name

    def draw_foldspace(self):
        self.game.shop.draw_shop_foldspace(self)
    def is_in_high_council(self):
        return self.in_high_council
    def add_mentat(self):
        self.game.mentat_available = False
        self.agents += 1
    def add_max_agent(self):
        self.max_agents += 1
    def remove_agent(self):
        self.agents -= 1

    def is_in_reveal_turn(self):
        return self.is_revealing_turn
    def set_conflict_ranking(self, ranking: int):
        self.conflict_ranking = ranking
        self.str_out += f"\nConflict Ranking: {ranking}"

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

    def has_revealed(self):
        return self.revealed
    def has_alliance(self, faction: Faction):
        return faction in self.alliances
    def enter_high_council(self):
        self.in_high_council = True
        self.persuasion += 2

    def get_changeable_factions(self, n):
       return set(map(lambda t: t[0], filter(lambda faction:  faction[1]['influence'] + n <= self.game.max_influence, self.factions.items())))

    def can_change_faction(self, faction: Faction, n: int):
        return faction in self.get_changeable_factions(n)
    def has_changeable_factions(self, n: int):
        return len(self.get_changeable_factions(n)) != 0

    def change_victory_points(self, n: int):
        self.victory_points += n
        if n > 0:
            self.str_out += '\n' + (f"+Victory Points: {n}")
        else:
            self.str_out += '\n' + (f"-Victory Points: {n}")
    def change_water(self, n: int):
        self.water += n
        if n > 0:
            self.str_out += '\n' + (f"+Water: {n}")
        else:
            self.str_out += '\n' + (f"-Water: {n}")


    def change_influence(self, faction: Faction, n: int):
        if self.factions[faction]['influence'] + n > self.game.max_influence:
            raise Exception("Influence cap surpassed!")
        if self.factions[faction]['influence'] + n < 0:
            raise Exception("Influence cannot be negative!")
        self.factions[faction]['influence'] += n
        if n > 0:
            self.str_out += '\n' + (f"+{faction}: {n}")
        else:
            self.str_out += '\n' + (f"-{faction}: {n}")

        influence = self.factions[faction]['influence']
        get_alliance = True

        if influence < 2 and self.factions[faction]['t1_reward_received']:
            self.change_victory_points(-1)
        if influence < 4 and faction in self.alliances:
            self.remove_alliance(faction)
        if influence >= 4:
            if not self.factions[faction]['t2_reward_received']:
                faction_rewards[faction](self.game, self)
                self.factions[faction]['t2_reward_received'] = True
            for i, player in enumerate(self.game.players):
                if player is self:
                    continue
                if influence <= player.factions[faction]['influence']:
                    get_alliance = False
                    break
        else:
            get_alliance = False

        if get_alliance:
            for i, player in enumerate(self.game.players):
                if player is self:
                    continue
                player.remove_alliance(faction)
            self.add_alliance(faction)


    def has_no_removable_cards(self):
        return len(self.hand_cards) == 0 and len(self.played_cards) == 0 and len(self.discard_pile) == 0
    def is_removable_card(self, card: 'CardInstance'):
        return card in self.hand_cards or card in self.played_cards or card in self.discard_pile or self.has_no_removable_cards()

    def try_steal_intrigues(self):
        for player in self.game.players:
            if player is self:
                continue
            if len(player.intrigues) > 3:
                random.shuffle(player.intrigues)
                self.intrigues.append(player.intrigues.pop())

    def remove_card(self, card: 'CardInstance'):
        if self.has_no_removable_cards():
            return
        if card in self.hand_cards:
            self.hand_cards.remove(card)
        elif card in self.played_cards:
            self.played_cards.remove(card)
        elif card in self.discard_pile:
            self.discard_pile.remove(card)
        else:
            raise Exception("Card not found in player's hand, played cards or discard pile")

    def remove_alliance(self, faction: Faction):
        if faction in self.alliances:
            self.alliances.remove(faction)
            self.str_out += '\n' + (f"--Alliance: {faction}")
    def add_alliance(self, faction: Faction):
        if faction not in self.alliances:
            self.alliances.add(faction)
            self.str_out += '\n' + (f"++Alliance: {faction}")
    def add_icons(self, icons: List[Icon]):
        self.icons.update(icons)
    def draw(self, n=1):
        for _ in range(n):
            if len(self.deck) > 0:
                card = self.deck.pop()
                self.hand_cards.append(card)
            else:
                random.shuffle(self.discard_pile)
                self.deck = self.discard_pile
                self.discard_pile = []

    def change_force(self, n: int):
        self.force += n
        if n > 0:
            self.str_out += '\n' + (f"+Force: {n}")
        else:
            self.str_out += '\n' + (f"-Force: {n}")

    def change_persuasion(self, n: int):
        self.persuasion += n
        if n > 0:
            self.str_out += '\n' + (f"+Persuasion: {n}")
        else:
            self.str_out += '\n' + (f"-Persuasion: {n}")

    def change_spice_solari(self, spice: int, solari: int):
        self.change_spice(spice)
        self.change_solari(solari)
    def change_spice(self, n: int):
        self.spice += n
        if n > 0:
            self.str_out += '\n' + (f"+Spice: {n}")
        else:
            self.str_out += '\n' + (f"-Spice: {n}")

    def change_solari(self, n: int):
        self.solari += n
        if n > 0:
            self.str_out += '\n' + (f"+Money: {n}")
        else:
            self.str_out += '\n' + (f"-Money: {n}")

    def change_garrison(self, n: int):
        self.garrison += n
        if n > 0:
            self.str_out += '\n' + (f"+Garrison: {n}")
        else:
            self.str_out += '\n' + (f"-Garrison: {n}")

    def change_to_deploy(self, n: int):
        self.to_deploy += n
        if n > 0:
            self.str_out += '\n' + (f"+To Deploy: {n}")
        else:
            self.str_out += '\n' + (f"-To Deploy: {n}")

    def change_in_combat(self, n: int):
        if self.in_combat + n < 0:
            return
        if self.in_combat > self.game.max_troops:
            raise Exception("In Combat cannot be higher than max troops")
        self.in_combat += n
        self.force += 2*n
        if n > 0:
            self.str_out += '\n' + (f"+In Combat: {n}")
            self.str_out += '\n' + (f"+Force: {n}")
        else:
            self.str_out += '\n' + (f"-In Combat: {n}")
            self.str_out += '\n' + (f"-Force: {n}")


    def change_to_retreat(self, n: int):
        self.to_retreat += n
        if n > 0:
            self.str_out += '\n' + (f"+To Retreat: {n}")
        else:
            self.str_out += '\n' + (f"-To Retreat: {n}")

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
        return self.intrigue_origin_node == state

    def can_buy(self, card: 'CardInstance'):
        return self.game.shop.shop_can_buy(card, self)

    def buy(self, card: 'CardInstance'):
        self.game.shop.shop_buy(card, self)

    def draw_intrigue(self):
        self.game.shop.draw_intrigue(self)

    def reveal_current_card(self):
        self.current_card = self.hand_cards.pop()
        self.open_choices = self.current_card.reveal_effect.choices


    def reveal(self):
        self.revealed = True
        self.is_revealing_turn = True
        self.current_choicing = 'reveal'

    def done_reveal(self):
        self.current_choicing = None

    def can_return_to_node(self, node: str):
        return self.intrigue_origin_node == node

    def intrigue_is_playable(self, intrigue: 'IntrigueInstance'):
        if not intrigue in self.intrigues:
            return False

        allowed_intrigues = [
            (IntrigueType.PLOT, GameState.AGENT),
            (IntrigueType.CONFLICT, GameState.IN_CONFLICT),
            (IntrigueType.FINALE, GameState.FINALE)
        ]
        if (intrigue.intrigue_type, self.game.state) not in allowed_intrigues:
            return False

        return intrigue.requirement.is_met(self.game)



    def is_playing_trivial_card(self):
        return self.current_card.agent_effect.__class__ == Effect.Effect

    def play_current_card(self):
        self.current_card.play(self.game)
        self.current_card = None
        self.current_location = None

    def has_playable_intrigue(self):
        for intrigue in self.intrigues:
            if self.intrigue_is_playable(intrigue):
                return True
        return False

    def set_intrigue_origin_node(self, node: str):
        self.intrigue_origin_node = node

    def has_playable_card_and_agent(self):
        if self.agents == 0:
            return False
        for card in self.hand_cards:
            if self.is_playable_card(card):
                return True
        return False
    def location_available_for_card(self, location: 'Location', card: 'CardInstance'):
            return (location.requirement.is_met(self.game)
                    and len(location.icons.intersection(card.icons.union(self.icons))) != 0
                    and not location.is_occupied)
    def location_available(self, location: 'Location'):
        return location.requirement.is_met(self.game) and not location.is_occupied and len(location.icons.intersection(self.icons)) != 0

    def is_playable_card(self, card: 'CardInstance'):
        if not card in self.hand_cards:
            return False
        for location in self.game.locations:
            if self.location_available_for_card(location, card):
                return True
        return False

    def on_player_swap(self):
        self.is_revealing_turn = False
        if not self.game.game_state == GameState.IN_CONFLICT:
            self.has_played_intrigue = False

        if self.game.game_state == GameState.CONFLICT_OVER:
            self.agents = self.max_agents
            self.to_deploy = 0
            self.in_combat = 0
            self.to_retreat = 0
            self.persuasion = 2 if self.in_high_council else 0
            self.discard_pile.extend(self.played_cards)
            self.played_cards = []
            if len(self.hand_cards) != 0:
                raise Exception("Player still has cards in hand after turn!")
            [self.draw() for _ in range(5)]


    # Picking
    def pick_intrigue(self, plot: 'PlotIntrigue'):
        self.current_intrigue = plot
        self.intrigues.remove(plot)
        self.has_played_intrigue = True
        self.open_choices = plot.effect.choices
        self.current_choicing = 'plot'

    def pick_card(self, card: 'CardInstance'):
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

    def pick_conflict_reward(self):
        self.current_choicing = 'conflict'
        if self.game.current_player.conflict_ranking >= self.game.num_players - 1:
            return
        self.open_choices = self.game.get_current_conflict().rewards[self.conflict_ranking].choices



    # Choicing
    def has_choices(self):
        return len(self.open_choices) != 0
    def has_no_choices(self):
        return len(self.open_choices)== 0
    def has_location_choices(self):
        return len(self.open_location_choices) != 0
    def has_no_location_choices(self):
        return len(self.open_location_choices) == 0

    def can_evaluate_intrigue(self, node: str):
        return self.has_no_choices() and self.current_choicing == 'plot' and self.can_return_to_node(node)
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
        self.current_location.occupy()
        self.decided_choices = []
        self.decided_location_choices = []
        self.current_card = None
        self.current_location = None
        self.current_choicing = None
        self.icons = set()

    def evaluate_choices_reveal(self):
        self.current_card.reveal_effect.execute(self.game, self.decided_choices)
        self.played_cards.append(self.current_card)
        self.decided_choices = []
        self.current_card = None

    def evaluate_choices_intrigue(self):
        self.current_intrigue.effect.execute(self.game, self.decided_choices)
        self.current_intrigue = None
        self.current_choicing = None
        self.intrigue_origin_node = None
        self.decided_choices = []

    def evaluate_choices_conflict(self):
        if self.game.current_player.conflict_ranking < self.game.num_players - 1:
            print(self.decided_choices)
            self.game.get_current_conflict().rewards[self.conflict_ranking].execute(self.game, self.decided_choices)
        self.has_resolved_conflict = True
        self.current_choicing = None
        self.decided_choices = []
        self.revealed = False
