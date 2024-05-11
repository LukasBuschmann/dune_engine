from typing import Callable, List, Set

from enums import Icon, ChoiceType
from Effect import Effect, swappero_effect, noEffect
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

    def __repr__(self):
        return self.name + str(self.icons)


def choice(game, decision):
    if decision == True:
        if game.current_player.solari > game.current_player.spice:
            return True
        else:
            return False
    elif decision == False:
        if game.current_player.solari <= game.current_player.spice:
            return True
        else:
            return False

def helper(game, faction):
    print(faction)
    print(game.current_player.get_influence_increase_possible_for(1))
    return True if faction in game.current_player.get_influence_increase_possible_for(1) else False

cards = [
    Card(
        name="Option Master",
        agent_effect=Effect(
            effect=lambda game, decision: game.current_player.change_solari(
                2) if decision else game.current_player.change_spice(2),
            choices=[Choice(ChoiceType.BOOLEAN, lambda game, decision: choice(game, decision))]
        ),
        reveal_effect=Effect(
            effect=lambda game: game.current_player.change_spice(2),
        )
    ),
    Card(
        name="Average No-Choicer",
        agent_effect=Effect(
            effect=lambda game: game.current_player.change_solari(2),
            choices=[]
        )
    ),



    Card(
        name="Firm Grip",
        agent_effect=Effect(
            effect=lambda game, activated, faction: (
                game.current_player.change_solari(-2),
                game.current_player.change_influence(faction, 1)
            ) if activated else None,
            choices=[
                Choice(
                    choice_type=ChoiceType.BOOLEAN,
                    condition=lambda game, decision: True if (game.current_player.solari >= 2 and game.current_player.get_influence_increase_possible_for(1)) or decision is False else False,
                    break_condition = lambda game: game.current_player.decided_choices[-1] is False),
                Choice(
                    choice_type=ChoiceType.FACTION,
                    condition=lambda game, faction: helper(game, faction))
            ],

        ),
    )
]


class PlotIntrigue:
    def __init__(self, name: str, effect: Effect, requirement: Requirement = noRequirement):
        self.name: str = name
        self.effect: Effect = effect
        self.requirement: Requirement = requirement

    def __repr__(self):
        return self.name


plots = [
    PlotIntrigue("Swappero", swappero_effect, noRequirement),
    PlotIntrigue(
        "Dispatch an Envoy ",
        Effect(
            effect=lambda game: game.current_player.add_icons(
                [Icon.IMPERIUM, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN])
        )
    )
]

"""
TODO:
"""
