from typing import Callable, List, Any
import Requirement
class Effect:
    def __init__(self, effect: Callable[['Game'], None], requirement: 'Requirement' = Requirement.noRequirement):
        self.effect: Callable[['Game'], None] = effect
        self.requirement: 'Requirement' = requirement

    def requirement_met(self, game: 'Game'):
        print(self.requirement.is_met)
        return self.requirement.is_met(game)
    def execute(self, game: 'Game'):
        if not self.requirement_met(game):
            raise Exception("Requirement not met, but tried to execute")
        self.effect(game)
        self.requirement.fulfill(game)
        self.effect(game)

noEffect = Effect(lambda game: None)

class BinaryDecisionEffectWithRequirement(Effect):
    def __init__(self, effect: Callable[['Game'], None], requirement: 'Requirement', decision_effect: Callable[['Game'], None]):
        super().__init__(effect)
        self.requirement: 'Requirement' = requirement
        self.decision_effect: Callable[['Game'], None] = decision_effect

    def decision_possible(self, game: 'Game'):
        return self.requirement.is_met(game)
    def execute_decision(self, game: 'Game', decision: bool):
        self.execute(game) # applying standard effect. Will mostly be empty
        if decision:
            self.requirement.fulfill(game)
            self.decision_effect(game)

class EffectWithChoice(Effect):
    def __init__(self, effect: Callable[['Game'], None], requirement: 'Requirement', choices: List[Callable[['Game'], None]]):
        super().__init__(effect, requirement)
        self.choices: List[Callable[['Game'], None]] = choices

    def decision_possible(self, game: 'Game'):
        return self.requirement.is_met(game)
    def execute_decision(self, game: 'Game', decision: int):
        self.execute(game) # applying standard effect. Will mostly be empty
        self.choices[decision](game)

class EffectWithChoices():
    def __init__(self, effect: Callable[['Game', List[Any]], None], choices: List[Requirement.Choice]):
        self.effect = effect
        self.choices: List[Requirement] = choices

    def execute(self, game: 'Game', decisions: List[Any]):
        self.effect(game, *decisions)


    """
    TODO:
        the general Class used for cards should be EffectWithChoices
    """