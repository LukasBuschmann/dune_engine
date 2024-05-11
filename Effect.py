from typing import Callable, List, Any
from enums import ChoiceType
from Requirement import Choice
class Effect():
    def __init__(self, effect: Callable[['Game', List[Any]], None], choices: List[Choice] = []):
        self.effect:  Callable[['Game', List[Any]], None] = effect
        self.choices: List[Choice] = choices

    def execute(self, game: 'Game', decisions: List[Any]):
        if len(decisions) != len(self.choices):
            diff = len(self.choices) - len(decisions)
            decisions.extend([None] * diff)
        self.effect(game, *decisions)


class ChoicelessEffect(Effect):
    def __init__(self, effect: Callable[['Game'], None]):
        super().__init__(effect, [])

    def execute(self, game: 'Game', decisions: List[Any]):
        self.effect(game)

def _swappero_effect(game):
    dspice = game.current_player.solari - game.current_player.spice
    dmoney = game.current_player.spice - game.current_player.solari
    game.current_player.change_spice(dspice)
    game.current_player.change_solari(dmoney)

class SpiceEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_spice(n))

class MoneyEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_solari(n))

class GarrisonEffect(ChoicelessEffect):
    def __init__(self, n: int):
        super().__init__(lambda game: game.current_player.change_garrison(n))



noEffect = ChoicelessEffect(lambda game: None)
swappero_effect = ChoicelessEffect(_swappero_effect)
bin_choice = Effect(lambda game, decision: game.current_player.change_solari(2) if decision else game.current_player.change_spice(2),
                    choices=[Choice(
                        ChoiceType.BOOLEAN,
                        lambda game, decision:
                            True if decision
                            else game.current_player.solari > game.current_player.spice)])


spice_trade = Effect(
    effect=lambda game, decision: game.current_player.change_spice_solari(2 - decision, 6 + (2 * (decision - 2))),
    choices=[Choice(
        choice_type=ChoiceType.NUMERIC,
        condition=lambda game, decision: decision in [2,3,4,5] and game.current_player.spice >= decision
    )]
)
