from typing import Callable, Any
from enums import ChoiceType


class Requirement:
    def __init__(self, requirement: Callable[['Game'], bool], fulfillment: Callable[['Game'], None]):
        self.requirement: Callable[['Game'], bool] = requirement
        self.fulfillment: Callable[['Game'], None] = fulfillment

    def is_met(self, game: 'Game'):
        return self.requirement(game)

    def fulfill(self, game: 'Game'):
        self.fulfillment(game)

    def __add__(self, other: 'Requirement'):
        return Requirement(
            requirement=lambda game: self.is_met(game) and other.is_met(game),
            fulfillment=lambda game: (self.fulfill(game), other.fulfill(game))
        )


class SpiceRequirement(Requirement):
    def __init__(self, spice: int):
        self.requirement = lambda game: game.current_player.spice >= spice
        self.fulfillment = lambda game: game.current_player.change_spice(-spice)

class SolariRequirement(Requirement):
    def __init__(self, solari: int):
        self.requirement = lambda game: game.current_player.solari >= solari
        self.fulfillment = lambda game: game.current_player.change_solari(-solari)

class WaterRequirement(Requirement):
    def __init__(self, water: int):
        self.requirement = lambda game: game.current_player.water >= water
        self.fulfillment = lambda game: game.current_player.change_water(-water)

class NoFullfillmentRequirement(Requirement):
    def __init__(self, requirement: Callable[['Game'], bool]):
        self.requirement = requirement
        self.fulfillment = lambda game: None

class InfluenceRequirement(NoFullfillmentRequirement):
    def __init__(self, faction: 'Faction', influence: int):
        self.requirement = lambda game: game.current_player.factions[faction]['influence'] >= influence


noRequirement = Requirement(lambda game: True, lambda game: None)


class Choice:
    def __init__(self, choice_type: 'ChoiceType', condition: Callable[['Game', 'Any'], bool],
                 break_condition: Callable[['Game'], bool] = lambda game: False):
        self.choice_type = choice_type
        self.condition = condition
        self.break_condition = break_condition

    def triggers_break(self, game: 'Game'):
        return self.break_condition(game)

    def is_allowed(self, choice: Any, choice_type: 'ChoiceType', game: 'Game'):
        if not self.choice_type is choice_type:
            return False
        return self.condition(game, choice)

    def __repr__(self):
        return self.choice_type.name


class BreakBinChoice(Choice):
    def __init__(self, condition: Callable[['Game', 'Any'], bool]):
        super().__init__(ChoiceType.BOOLEAN, condition, lambda game: game.current_player.decided_choices[-1] is False)
