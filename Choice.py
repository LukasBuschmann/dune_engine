from typing import List, Callable, TypeVar, Generic
from abc import ABC, abstractmethod
from enums import Faction, TurnType
import random

T = TypeVar('T')
class ChoiceType(Generic[T]):
    def __init__(self,  name: str, get_choices: Callable[['Game'], List[T]]):
        self.name: str = name
        self.get_choices: Callable[['Game'], List[T]] = get_choices

class Choice(Generic[T]):
    def __init__(self, choice_type: ChoiceType[T], condition: Callable[['Game', T], bool]):
        self.choice_type = choice_type
        self.condition = condition

    def valid_choices(self, game: 'Game') -> List[T]:
        return [choice for choice in self.choice_type.get_choices(game) if self.condition(game, choice)]


class Resolver(ABC):
    @abstractmethod
    def resolve(self, game: 'Game', choices: List[T]) -> T:
        pass

class RandomResolver(Resolver):
    def resolve(self, game: 'Game', choices: List[T]) -> T:
        return random.choice(choices)


turn_type_choice_t: ChoiceType[TurnType] = ChoiceType('Turn Type', lambda game: game.current_player.get_turn_types())
boolean_choice_t: ChoiceType[bool] = ChoiceType('Boolean', lambda game: [True, False])
garrison_choice_t: ChoiceType[int] = ChoiceType('Garrison', lambda game: [i for i in range(-12, 13)])
spice_trade_choice_t: ChoiceType[int] = ChoiceType('Spice Trade', lambda game: [i for i in range(2, 6)])
hand_choice_t: ChoiceType['Card'] = ChoiceType('Hand Card', lambda game: game.current_player.hand_cards)
removable_choice_t: ChoiceType['Card'] = ChoiceType('Removable Cards', lambda game: game.current_player.played_cards + game.current_player.hand_cards + game.current_player.discard_pile)
shop_choice_t: ChoiceType['Card'] = ChoiceType('Shop Card', lambda game: game.shop.imperium_row)
location_choice_t: ChoiceType['Location'] = ChoiceType('Location', lambda game: game.locations)
faction_choice_t: ChoiceType['Faction'] = ChoiceType('Faction', lambda game: [faction for faction in Faction])

playable_cards_choice: Choice['Card'] = Choice(hand_choice_t, lambda game, card: card.is_playable_with(game, card))
