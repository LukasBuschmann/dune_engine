from typing import Callable, List, Set

from enums import Icon

class Requirement:
    def __init__(self, requirement: Callable[['Game'], bool], fulfillment: Callable[['Game'], None]):
        self.requirement: Callable[['Game'], bool] = requirement
        self.fulfillment: Callable[['Game'], None] = fulfillment

    def is_met(self, game: 'Game'):
        return self.requirement(game)

    def fulfill(self, game: 'Game'):
        self.fulfillment(game)


class Effect:
    def __init__(self, effect: Callable[['Game'], None]):
        self.effect: Callable[['Game'], None] = effect

    def execute(self, game: 'Game'):
        self.effect(game)


class NoEffect(Effect):
    def __init__(self):
        self.effect = lambda game: None

    def execute(self, game: 'Game'):
        pass


class BinaryDecisionEffectWithRequirement(Effect):
    def __init__(self, effect: Callable[['Game'], None], requirement: Requirement, decision_effect: Callable[['Game'], None]):
        super().__init__(effect)
        self.requirement: Requirement = requirement
        self.decision_effect: Callable[['Game'], None] = decision_effect

    def decision_possible(self, game: 'Game'):
        return self.requirement.is_met(game)

    def execute_decision(self, game: 'Game', decision: bool):
        if decision:
            self.requirement.fulfill(game)
            self.decision_effect(game)
        self.execute(game) # applying standard effect. Will mostly be empty


class NoRequirement(Requirement):
    def __init__(self):
        self.requirement = lambda game: True
        self.fulfillment = lambda game: None

    def is_met(self, game: 'Game'):
        return True

    def fulfill(self, game: 'Game'):
        pass

class Card:
    def __init__(self,
                 name: str,
                 persuasion_cost: int = 0,
                 icons: Set[Icon] = {Icon.IMPERIUM, Icon.DESERT, Icon.FREMEN},
                 factions: List[str] = ['all'],
                 agent_effect: Effect = NoEffect(),
                 reveal_effect: Effect = NoEffect(),
                 removal_effect: Effect = NoEffect(),
                 acquisition_effect: Effect = NoEffect()):
        self.name: str = name
        self.persuasion_cost: int = persuasion_cost
        self.icons: Set[Icon] = icons
        self.factions: List[str] = factions
        self.agent_effect: Effect = agent_effect
        self.reveal_effect: Effect = reveal_effect
        self.removal_effect: Effect = removal_effect
        self.acquisition_effect: Effect = acquisition_effect

    def play(self, game: 'Game'):
        self.agent_effect.execute(game)

    def reveal(self, game: 'Game'):
        self.reveal_effect.execute(game)

    def __repr__(self):
        return self.name + str(self.icons)




class PlotIntrigue:
    def __init__(self, name: str, effect: Callable[['Game'], None], requirements: Callable[['Game'], bool]):
        self.name: str = name
        self.effect: Callable[['Game'], None] = effect
        self.requirements: Callable[['Game'], bool] = requirements

    def play(self, game: 'Game'):
        self.effect(game)

    def is_playable(self, game: 'Game'):
        return self.requirements(game)

    def __repr__(self):
        return self.name


money_effect = Effect(lambda game: setattr(game.current_player, "current_player.money", game.current_player.money + 2))


spice_effect = Effect(lambda game: game.current_player.change_spice(2))
decision_effect = BinaryDecisionEffectWithRequirement(lambda game: game.current_player.change_to_deploy(1),
                                                      Requirement(lambda game: game.current_player.spice >= 3, lambda game: game.current_player.change_spice(-3)),
                                                      lambda game: game.current_player.change_garrison(3))

cards = [
    Card("Spice Addict", reveal_effect=money_effect, icons={Icon.FREMEN}),
    Card("Everywhere Joe"),
    Card("Decisive General", reveal_effect=decision_effect),
    Card("Trader", agent_effect=spice_effect, icons={Icon.IMPERIUM}),
]

def swappero_effect(game):
    dspice = game.current_player.money - game.current_player.spice
    dmoney = game.current_player.spice - game.current_player.money
    game.current_player.change_spice(dspice)
    game.current_player.change_money(dmoney)


plots = [
    PlotIntrigue("Swappero",  swappero_effect, lambda game: True),
    PlotIntrigue("Spice_Harvest",  lambda game: game.current_player.change_money(1), lambda game: game.current_player.money >= 3),
]















"""
TODO:
"""
















