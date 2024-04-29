from typing import Callable, List, Set

from enums import Icon, ChoiceType
from Effect import Effect, BinaryDecisionEffectWithRequirement, noEffect, EffectWithChoices
from Requirement import Requirement, SpiceRequirement, noRequirement, Choice





class Card:
    def __init__(self,
                 name: str,
                 persuasion_cost: int = 0,
                 icons: Set[Icon] = {Icon.IMPERIUM, Icon.DESERT, Icon.FREMEN},
                 factions: List[str] = ['all'],
                 agent_effect: Effect = noEffect,
                 reveal_effect: Effect = noEffect,
                 removal_effect: Effect = noEffect,
                 acquisition_effect: Effect = noEffect):
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


class CardV2:
    def __init__(self,
                 name: str,
                 persuasion_cost: int = 0,
                 icons: Set[Icon] = {Icon.IMPERIUM, Icon.DESERT, Icon.FREMEN},
                 factions: List[str] = ['all'],
                 agent_effect: EffectWithChoices = noEffect,
                 reveal_effect: Effect = noEffect,
                 removal_effect: Effect = noEffect,
                 acquisition_effect: Effect = noEffect):
        self.name: str = name
        self.persuasion_cost: int = persuasion_cost
        self.icons: Set[Icon] = icons
        self.factions: List[str] = factions
        self.agent_effect: EffectWithChoices = agent_effect
        self.reveal_effect: Effect = reveal_effect
        self.removal_effect: Effect = removal_effect
        self.acquisition_effect: Effect = acquisition_effect
    def __repr__(self):
        return self.name + str(self.icons)



cardsV2 = [
    # CardV2(
    #     name="Option Master",
    #     agent_effect=EffectWithChoices(
    #         effect=lambda game, decision: game.current_player.change_money(2) if decision else game.current_player.change_spice(2),
    #         choices=[Choice(ChoiceType.BOOLEAN, lambda game, decision: True)]
    #     )
    # ),
    CardV2(
            name="Average No-Choicer",
            agent_effect=EffectWithChoices(
                effect = lambda game: game.current_player.change_money(2),
                choices=[]
            )
        ),
]



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


money_effect = Effect(lambda game: game.current_player.change_money(2))
spice_effect = Effect(lambda game: game.current_player.change_spice(2))
decision_effect = BinaryDecisionEffectWithRequirement(lambda game: game.current_player.change_to_deploy(1),
                                                      SpiceRequirement(3),
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
















