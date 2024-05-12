from typing import List, Callable, Set

from  Requirement import  SpiceRequirement, noRequirement
from Effect import Effect, SpiceEffect, GarrisonEffect, spice_trade
import demo_cards as dc
from enums import Icon


class Location:
    def __init__(self, name: str, requirement: dc.Requirement, effect: dc.Effect,
                 icons: Set[Icon] = {Icon.IMPERIUM, Icon.ECONOMY, Icon.FREMEN}):
        self.name: str = name
        self.requirement: dc.Requirement = requirement
        self.effect: dc.Effect = effect
        self.is_occupied: bool = False
        self.icons: Set[Icon] = icons

    def occupy(self):
        self.is_occupied = True
    def clear(self):
        self.is_occupied = False

    def __repr__(self):
        return self.name + str(self.icons)




locations = [
    Location("Spice Mine", noRequirement, SpiceEffect(2), icons={Icon.IMPERIUM, Icon.ECONOMY}),
    Location("Fremen Outpost", SpiceRequirement(1), GarrisonEffect(2), icons={Icon.FREMEN}),
    Location("Trader's Guild", SpiceRequirement(2), spice_trade),
]
