import itertools
import random
from typing import List, Set

from enums import Commander, Faction, Icon, IntrigueType, TurnType, Statics
from Cards import start_cards, no_card, kwisatz_haderach, no_intrigue, CardInstance, IntrigueInstance
from Choice import RandomResolver, Resolver, intrigue_choice
from Location import no_location, faction_rewards, Location


class Player(object):

    def __init__(self, game: 'Game', commander: Commander):
        self.game: 'Game' = game
        self.commander: Commander = commander

        self.resolver: 'Resolver' = RandomResolver()

        self.victory_points = 0

        self.solari: int = 0
        self.spice: int = 0
        self.water: int = 1
        self.persuasion: int = 0

        self.agents = 2
        self.max_agents = 2

        # ToDo: change this to a object
        self.factions = {faction: {'influence': 0, 't1_reward_received': False, "t2_reward_received": False} for faction
                         in Faction}
        self.alliances = set()

        self.in_high_council = False

        self.garrison: int = 2
        self.in_combat: int = 0
        self.deployable: int = 0
        self.retractable: int = 0
        self.force: int = 0

        self.icons: Set[Icon] = set()

        self.deck: List['CardInstance'] = list(
            itertools.chain.from_iterable(card.get_instances() for card in start_cards))
        random.shuffle(self.deck)

        self.played_cards: List['CardInstance'] = []
        self.revealed_cards: List['CardInstance'] = []
        self.discard_pile: List['CardInstance'] = []
        self.hand_cards: List['CardInstance'] = []

        self.intrigues: List['IntrigueInstance'] = []

        self.current_location: 'Location' = no_location
        self.revealed: bool = False
        self.is_revealing_turn: bool = False
        self.passed_combat_intrigue = False

        self.agent_on_combat_location = False

        self.on_win = []

        self.get_mentat = False
        self.guild_bankers = False
        self.voice = False
        self.infiltrate = False
        self.recruitment = False
        self.bindu_suspension = False

        self.in_turn = False
        self.in_finale = False

    def __repr__(self):
        return self.commander.name

    def __str__(self):
        return self.commander.name

    def draw_from_discard(self, card: 'CardInstance'):
        if card in self.discard_pile:
            self.discard_pile.remove(card)
            self.hand_cards.append(card)
        else:
            raise Exception("Card not in discard pile")

    def draw_foldspace(self):
        self.game.shop.draw_shop_foldspace(self)

    def is_in_high_council(self):
        return self.in_high_council

    def enter_high_council(self):
        self.in_high_council = True
        self.change_persuasion(2)

    # ToDo: combine to one function
    def add_mentat(self):
        self.game.mentat_available = False
        self.agents += 1

    def try_add_mentat(self):
        if self.game.mentat_available:
            self.add_mentat()

    def add_swordmaster(self):
        self.max_agents += 1
        self.agents += 1

    def has_revealed(self):
        return self.revealed

    # ToDo: allow overshoot
    def get_changeable_factions(self, n):
        return set(map(lambda t: t[0],
                       filter(lambda faction: 0 <= faction[1]['influence'] + n <= Statics.MAX_INFLUENCE,
                              self.factions.items())))

    def can_change_faction(self, faction: Faction, n: int):
        return faction in self.get_changeable_factions(n)

    def change_victory_points(self, n: int):
        self.victory_points += n

    def change_water(self, n: int):
        self.water += n

    # todo: should this be managed in the player?
    def change_influence(self, faction: Faction, n: int):
        if self.factions[faction]['influence'] + n > self.game.max_influence:
            return
        if self.factions[faction]['influence'] + n < 0:
            raise Exception("Influence cannot be negative!")
        self.factions[faction]['influence'] += n

        influence = self.factions[faction]['influence']
        get_alliance = True

        if influence < 2 and self.factions[faction]['t1_reward_received']:
            self.change_victory_points(-1)
        if influence < 4 and faction in self.alliances:
            self.remove_alliance(faction)
        if influence >= 4:
            if not self.factions[faction]['t2_reward_received']:
                faction_rewards[faction](self)
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

    def remove_card(self, card: 'CardInstance'):
        if card is no_card:
            return
        if card in self.hand_cards:
            self.hand_cards.remove(card)
        elif card in self.played_cards:
            self.played_cards.remove(card)
        elif card in self.discard_pile:
            self.discard_pile.remove(card)
        card.removal_effect(self)

    def remove_deck_top(self):
        self.deck.pop()

    def remove_alliance(self, faction: Faction):
        if faction in self.alliances:
            self.alliances.remove(faction)

    def add_alliance(self, faction: Faction):
        if faction not in self.alliances:
            self.alliances.add(faction)

    # ToDo: does this really work?
    def add_icons(self, new_icons: Set[Icon]):
        self.icons.update(new_icons)

    def draw(self, n=1):
        for _ in range(n):
            if len(self.deck) > 0:
                card = self.deck.pop()
                self.hand_cards.append(card)
            else:
                random.shuffle(self.discard_pile)
                self.deck = self.discard_pile
                self.discard_pile = []

    def discard(self, card: 'CardInstance'):
        self.hand_cards.remove(card)
        self.discard_pile.append(card)

    def change_force(self, n: int):
        self.force += n

    def change_persuasion(self, n: int):
        self.persuasion += n

    def change_spice(self, n: int):
        self.spice += n

    def change_solari(self, n: int):
        self.solari += n

    def change_garrison(self, n: int):
        if self.garrison + n < 0 or self.garrison + n > self.game.max_troops:
            return

        self.garrison += n
        if self.agent_on_combat_location:
            self.change_to_deploy(n)

    def change_to_deploy(self, n: int):
        self.deployable += n

    def change_to_retreat(self, n: int):
        self.retractable += n

    def change_in_combat(self, n: int):
        if self.in_combat + n < 0:
            return
        if self.in_combat > self.game.max_troops:
            raise Exception("In Combat cannot be higher than max troops")

        new_in_combat = self.in_combat + n
        self.in_combat = new_in_combat if new_in_combat <= self.game.max_troops else self.game.max_troops
        # ToDo: separate force and troops
        self.force += 2 * n

    def draw_intrigue(self):
        self.game.shop.draw_intrigue(self)

    def has_playable_card(self) -> bool:
        for card in self.hand_cards:
            if card.is_playable(self, card):
                return True
        return False

    def get_all_cards(self) -> List['CardInstance']:
        return self.hand_cards + self.played_cards + self.revealed_cards + self.discard_pile + self.deck

    def get_turn_types(self) -> List[TurnType]:
        allowed_turns = []
        if self.has_playable_card():
            allowed_turns.append(TurnType.AGENT)
        if not self.has_revealed():
            allowed_turns.append(TurnType.REVEAL)
        return allowed_turns

    def location_available_for_card(self, location: 'Location', card: 'CardInstance'):
        return location.is_available_with(self, card)

    def get_playable_cards(self) -> List['CardInstance']:
        return [card for card in self.hand_cards if card.is_playable(self, card)]

    def get_playable_locations_with(self, card: 'CardInstance') -> List['Location']:
        return [location for location in self.game.locations if self.location_available_for_card(location, card)]

    def get_in_play(self, faction: Faction) -> int:
        return sum(
            map(lambda played_card: played_card.factions.count(faction), self.played_cards + self.revealed_cards))

    def get_in_discard(self, faction: Faction) -> int:
        return sum(map(lambda card: card.factions.count(faction), self.discard_pile))

    # Only use this for reveal turn i.e. fremen bond
    def get_in_potential_play(self, faction: Faction) -> int:
        return sum(map(lambda played_card: played_card.factions.count(faction),
                       self.played_cards + self.revealed_cards + self.hand_cards))

    def get_in_play_and_hand(self, faction: Faction) -> int:
        return sum(map(lambda played_card: played_card.factions.count(faction),
                       self.played_cards + self.revealed_cards + self.hand_cards))

    def deploy(self, n: int):
        self.garrison -= n
        self.in_combat += n

    def play_intrigue(self, intrigue_type: IntrigueType) -> IntrigueInstance:
        chosen_intrigue = intrigue_choice(intrigue_type).resolve(self)
        self.intrigues.remove(chosen_intrigue)
        chosen_intrigue.effect(self)
        return chosen_intrigue

    def play_intrigues(self, intrigue_type: IntrigueType):
        while True:
            played_intrigue = self.play_intrigue(intrigue_type)
            if played_intrigue is no_intrigue:
                break

    def can_buy(self, card: 'CardInstance'):
        return self.game.shop.shop_can_buy(card, self)

    def buy(self, card: 'CardInstance'):
        self.game.shop.shop_buy(card, self)

    def deploy_troops(self):
        deployable_troops = list(range(-min(self.retractable, self.in_combat), min(self.deployable, self.garrison) + 1))
        deployment_choice = self.resolver.resolve(self, deployable_troops)
        self.deploy(deployment_choice)

    def after_conflict(self):
        self.in_combat = 0
        self.force = 0
        self.deployable = 0
        self.retractable = 0
        self.persuasion = 2 if self.in_high_council else 0
        self.agents = self.max_agents
        # get mentat notes that the mentat is available next round (f.e. through a conflict reward)
        # adding the mentat registers it as unavailable for the current round
        if self.get_mentat:
            self.add_mentat()

        self.passed_combat_intrigue = False

        self.on_win = []

    def agent_turn(self):
        playable_cards = self.get_playable_cards()
        card_choice: 'CardInstance' = self.resolver.resolve(self, playable_cards)
        self.hand_cards.remove(card_choice)
        self.played_cards.append(card_choice)

        # kwisatz manages the turn itself in the card effect
        if card_choice is kwisatz_haderach:
            card_choice.agent_effect(self)
        else:
            playable_locations = self.get_playable_locations_with(card_choice)
            location_choice: 'Location' = self.resolver.resolve(self, playable_locations)
            self.current_location = location_choice  # needed for some effects
            self.agents -= 1

            location_choice.requirement.fulfill(self)
            location_choice.effect(self)

            card_choice.agent_effect(self)
            location_choice.occupy(self)

        self.current_location = no_location

        self.play_intrigues(IntrigueType.PLOT)
        self.deploy_troops()

        self.agent_on_combat_location = False
        self.get_mentat = False
        self.voice = False
        self.infiltrate = False
        self.recruitment = False

    def reveal_turn(self):
        self.revealed = True
        self.is_revealing_turn = True
        while self.hand_cards:
            card = self.hand_cards.pop()
            self.revealed_cards.append(card)
            card.reveal_effect(self)
        while True:
            available_cards = self.game.shop.get_cards_in_shop()
            purchasable_cards = [card for card in available_cards if
                                 self.can_buy(card)] + no_card  # todo: find a better solution
            card_choice: 'CardInstance' = self.resolver.resolve(self, purchasable_cards)
            if card_choice is no_card:
                break
            self.buy(card_choice)
        self.play_intrigues(IntrigueType.PLOT)
        self.deploy_troops()  # todo: RESTRICTION we cannot use a plot card to deploy troops and then use another plot card to retreat troops for reward
        self.discard_pile.extend(self.played_cards)
        self.discard_pile.extend(self.revealed_cards)
        self.played_cards = []
        self.revealed_cards = []
        self.is_revealing_turn = False

        self.guild_bankers = False
        self.voice = False

    def agent_or_reveal_turn(self):
        self.draw(5)
        turn_types = self.get_turn_types()
        turn_choice = self.resolver.resolve(self, turn_types)
        self.play_intrigues(IntrigueType.PLOT)

        # skip turn
        if self.bindu_suspension:
            self.bindu_suspension = False
        else:
            self.in_turn = True
            if turn_choice == TurnType.AGENT:
                self.agent_turn()
            elif turn_choice == TurnType.REVEAL:
                self.reveal_turn()

        self.in_turn = False

    def combat_turn(self):
        self.passed_combat_intrigue = False
        intrigue = self.play_intrigue(IntrigueType.COMBAT)
        if intrigue is no_intrigue:
            self.passed_combat_intrigue = True


    def finale_turn(self):
        self.in_finale = True
        for finale_intrigue in filter(lambda intrigue: IntrigueType.FINALE in intrigue.intrigue_types, self.intrigues):
            finale_intrigue.effect(self)
