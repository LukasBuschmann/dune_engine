from typing import Callable, Any

class Requirement:
    def __init__(self, requirement: Callable[['Game'], bool], fulfillment: Callable[['Game'], None]):
        self.requirement: Callable[['Game'], bool] = requirement
        self.fulfillment: Callable[['Game'], None] = fulfillment

    def is_met(self, game: 'Game'):
        return self.requirement(game)

    def fulfill(self, game: 'Game'):
        self.fulfillment(game)


noRequirement = Requirement(lambda game: True, lambda game: None)

class Choice:
    def __init__(self, choice_type: 'ChoiceType', condition: Callable[['Game', 'Any'], bool]):
        self.choice_type = choice_type
        self.condition = condition
    def is_allowed(self, choice: Any, choice_type: 'ChoiceType', game: 'Game'):
        if not self.choice_type is choice_type:
            return False
        return self.condition(game, choice)


class SpiceRequirement(Requirement):
    def __init__(self, spice: int):
        self.requirement = lambda game: game.current_player.spice >= spice
        self.fulfillment = lambda game: game.current_player.change_spice(-2)
