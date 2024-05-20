from typing import Callable, List, Any, Set
from enums import ChoiceType, Faction
from Requirement import Choice


class Effect():
    def __init__(self, effect: Callable[['Game', List[Any]], Any], choices: List[Choice] = []):
        self.effect: Callable[['Game', List[Any]], None] = effect
        self.choices: List[Choice] = choices

    def execute(self, game: 'Game', decisions: List[Any]):
        # For breakpoints
        if len(decisions) != len(self.choices):
            diff = len(self.choices) - len(decisions)
            decisions.extend([None] * diff)
        self.effect(game, *decisions)

    # def __add__(self, other):
    #     if not isinstance(other, ChoicelessEffect):
    #         raise TypeError('Can only add Effect and ChoicelessEffect objects')
    #
    #     return Effect(
    #         effect=lambda game, decisions: (self.execute(game, decisions), other.execute(game, [])),
    #         choices=self.choices
    #     )


class ChoicelessEffect(Effect):
    def __init__(self, effect: Callable[['Game'], Any]):
        super().__init__(effect, [])

    def execute(self, game: 'Game', decisions: List[Any]):
        self.effect(game)

    # TODO: Add apply method
    # TODO: change Effect system to be more generic. i.e. all Effect.effect are lambdas taking in a game and a dictionary with all possible decision types. This way we will be able to cascade Effects instead of just ChoicelessEffect
    def __add__(self, other: 'ChoicelessEffect'):
        if not isinstance(other, ChoicelessEffect):
            raise TypeError('Can only add ChoicelessEffect objects')

        return ChoicelessEffect(effect=lambda game: (self.effect(game), other.effect(game)))


def _swappero_effect(game):
    dspice = game.current_player.solari - game.current_player.spice
    dmoney = game.current_player.spice - game.current_player.solari
    game.current_player.change_spice(dspice)
    game.current_player.change_solari(dmoney)


class SpiceEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_spice(n))


class SolariEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_solari(n))


class GarrisonEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_garrison(n))


class DeployEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_to_deploy(n))


class PersuasionEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_persuasion(n))


class ForceEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_force(n))


class VictoryEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_victory_points(n))


class IntrigueEffect(ChoicelessEffect):
    def __init__(self):
        super().__init__(lambda game: game.current_player.draw_intrigue())


class CardEffect(ChoicelessEffect):
    def __init__(self, n):
        super().__init__(lambda game: game.current_player.draw(n))


class WaterEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_water(n))


class MentatEffect(ChoicelessEffect):
    def __init__(self):
        super().__init__(lambda game: game.current_player.add_mentat())


class InfluenceChoiceEffect(Effect):
    def __init__(self, n: int, excluded_factions: Set[Faction] = set()):
        super().__init__(
            effect=lambda game, faction: game.current_player.change_influence(faction, n),
            choices=[Choice(
                ChoiceType.FACTION,
                lambda game, faction: faction not in excluded_factions and game.current_player.can_change_faction(
                    faction, n)
            )]
        )

class InfluenceEffect(ChoicelessEffect):
    def __init__(self, faction: Faction, n: int ):
        super().__init__(lambda game: game.current_player.change_influence(faction, n))

class CaptureSpiceEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(
            lambda game: game.capture_locations[game.current_player.current_location].change_spice(n)
            if game.capture_locations[game.current_player.current_location] is not None else None)


class CaptureSolariEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(
            lambda game: game.capture_locations[game.current_player.current_location].change_solari(n)
            if game.capture_locations[game.current_player.current_location] is not None else None)

class FoldSpaceEffect(ChoicelessEffect):
    def __init__(self):
        super().__init__(
            lambda game: game.current_player.draw_foldspace()
        )

class WormSpiceEffect(ChoicelessEffect):
    def __init__(self):
        super().__init__(
            lambda game: game.current_player.change_spice(game.worm_locations[game.current_player.current_location]))

class RemoveCardEffect(Effect):
    def __init__(self):
        super().__init__(
            effect=lambda game, card: game.current_player.remove_card(card),
            choices=[Choice(
                ChoiceType.CARD,
                lambda game, card: game.current_player.is_removable_card(card)
            )])


class StealIntrigueEffect(ChoicelessEffect):
    def __init__(self):
        super().__init__(
            lambda game: game.current_player.try_steal_intrigues()
        )



noEffect = ChoicelessEffect(lambda game: None)
swappero_effect = ChoicelessEffect(_swappero_effect)
bin_choice = Effect(
    lambda game, decision: game.current_player.change_solari(2) if decision else game.current_player.change_spice(2),
    choices=[Choice(
        ChoiceType.BOOLEAN,
        lambda game, decision:
        True if decision
        else game.current_player.solari > game.current_player.spice)])

spice_trade = Effect(
    effect=lambda game, decision: game.current_player.change_spice_solari(2 - decision, 6 + (2 * (decision - 2))),
    choices=[Choice(
        choice_type=ChoiceType.NUMERIC,
        condition=lambda game, decision: decision in [2, 3, 4, 5] and game.current_player.spice >= decision
    )]
)
