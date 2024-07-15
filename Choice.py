from typing import List, Callable, TypeVar, Generic, Set
from abc import ABC, abstractmethod
import random

from enums import Faction, IntrigueType, TurnType, LocationName

T = TypeVar('T')


class ChoiceType(Generic[T]):
    def __init__(self, name: str, get_choices: Callable[['Player'], List[T]]):
        self.name: str = name
        self.get_choices: Callable[['Player'], List[T]] = get_choices


class Choice(Generic[T]):
    def __init__(self, choice_type: ChoiceType[T], condition: Callable[['Player', T], bool]):
        self.choice_type = choice_type
        self.condition = condition

    def valid_choices(self, player: 'Player') -> List[T]:
        return [choice for choice in self.choice_type.get_choices(player) if self.condition(player, choice)]

    def resolve(self, player: 'Player') -> T:
        choices = self.valid_choices(player)
        return player.resolver.resolve(player, choices)


class Resolver(ABC):
    @abstractmethod
    def resolve(self, player: 'Player', choices: List[T]) -> T:
        pass


class RandomResolver(Resolver):
    def resolve(self, player: 'Player', choices: List[T]) -> T:
        return random.choice(choices)


turn_type_choice_t: ChoiceType[TurnType] = ChoiceType('Turn Type', lambda player: player.get_turn_types())
boolean_choice_t: ChoiceType[bool] = ChoiceType('Boolean', lambda player: [True, False])
garrison_choice_t: ChoiceType[int] = ChoiceType('Garrison', lambda player: [i for i in range(-12, 13)])
spice_trade_choice_t: ChoiceType[int] = ChoiceType('Spice Trade', lambda player: [i for i in range(2, 6)])
hand_choice_t: ChoiceType['CardInstance'] = ChoiceType('Hand Card', lambda player: player.hand_cards)
discard_pile_choice_t: ChoiceType['CardInstance'] = ChoiceType('Discard Pile Card', lambda player: player.discard_pile)
removable_choice_t: ChoiceType['CardInstance'] = ChoiceType('Removable Cards', lambda
    player: player.played_cards + player.hand_cards + player.discard_pile)  # ToDo: cannot import cards here! -> find generic way to make "no choice
shop_choice_t: ChoiceType['CardInstance'] = ChoiceType('Shop Card', lambda player: player.game.shop.imperium_row)
location_choice_t: ChoiceType['Location'] = ChoiceType('Location', lambda player: player.game.locations)
kwisatz_location_choice_t: ChoiceType['Location'] = ChoiceType('Location',
                                                               lambda
                                                                   player: player.game.locations)  # ToDo: cannot import cards here! -> find generic way to make "no choice
faction_choice_t: ChoiceType['Faction'] = ChoiceType('Faction', lambda player: [faction for faction in Faction])
player_choice_t: ChoiceType['Player'] = ChoiceType('Player', lambda player: player.game.players)
intrigue_choice_t: ChoiceType['IntrigueInstance'] = ChoiceType('Intrigue',
                                                               lambda
                                                                   player: player.intrigues)  # ToDo: cannot import cards here! -> find generic way to make "no choice

playable_cards_choice: Choice['CardInstance'] = Choice(hand_choice_t,
                                                       lambda player, card: card.is_playable(player, card))
removable_cards_choice: Choice['CardInstance'] = Choice(removable_choice_t, lambda player, card: True)
spice_trade_choice: Choice[int] = Choice(spice_trade_choice_t, lambda player, decision: player.spice >= (decision - 2))
bool_choice: Choice[bool] = Choice(boolean_choice_t, lambda player, decision: True)
hand_card_choice: Choice['CardInstance'] = Choice(hand_choice_t, lambda player, card: True)
discard_pile_bene_gesserit_choice: Choice['CardInstance'] = Choice(discard_pile_choice_t, lambda player,
                                                                                                 card: card.faction == Faction.BENE_GESSERIT)
kwisatz_location_choice: Choice['Location'] = Choice(location_choice_t,
                                                     lambda player, location: player in location.occupied_by or (
                                                             location.name == LocationName.AGENT_RESERVES.value and player.agents > 0))  # ToDo: cannot import cards here! -> find generic way to make "no choice
urgent_mission_location_choice: Choice['Location'] = Choice(
    location_choice_t,
    lambda player, location: player in location.occupied_by or (
            location.name == LocationName.AGENT_RESERVES.value and player.agents == player.max_agents + (
        1 if player.get_mentat else 0))
    # ToDo: cannot import cards here! -> find generic way to make "no choice
)
# ToDo: apply discounts to checked pice (hero ability)
bypass_protocol_3_choice = Choice(shop_choice_t, lambda player, card: card.persuasion_cost <= 3)
bypass_protocol_5_choice = Choice(shop_choice_t, lambda player, card: card.persuasion_cost <= 5)

# voice blocks kwisatz
# https://boardgamegeek.com/thread/2925736/kwisatz-haderach-and-voice
kwisatz_destination_choice: Choice['Location'] = Choice(location_choice_t,
                                                        lambda player, location: location.requirement.is_met(
                                                            player) and not location.voiced)
voice_location_choice: Choice['Location'] = Choice(location_choice_t, lambda player, location: True)
other_players_choice: Choice['Player'] = Choice(player_choice_t, lambda player, other_player: other_player != player)


def influence_choice(n: int, excluded_faction: Set['Faction']) -> Choice['Faction']:
    return Choice(
        faction_choice_t,
        lambda player, faction:
        player.can_change_faction(faction, n) and faction not in excluded_faction
    )


def intrigue_choice(intrigue_type: IntrigueType) -> Choice['IntrigueInstance']:
    return Choice(
        intrigue_choice_t,
        lambda player, intrigue: intrigue_type in intrigue.intrigue_types
    )
