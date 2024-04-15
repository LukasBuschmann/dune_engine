from typing import Callable, List
from enum import Enum

from Factions import Faction


class DeckCard:
    def __init__(self) -> None:
        self.persuasion_cost: int = 0
        self.factions: List[Faction]
        self.acquisition_effects: List[CardEffect] = []
        self.agent_turn_effects: List[CardEffect] = []
        self.reveal_turn_effects: List[CardEffect] = []
        self.agent_icons: List[AgentIcon] = []
        self.name: str = "Unnamed Card"

    def apply_acquisition_effects(self) -> None:
        for acquisition_effect in self.acquisition_effects:
            acquisition_effect.apply()

    def apply_agent_turn_effects(self) -> None:
        for agent_turn_effect in self.agent_turn_effects:
            agent_turn_effect.apply()

    def apply_reveal_turn_effects(self) -> None:
        for reveal_turn_effect in self.reveal_turn_effects:
            reveal_turn_effect.apply()


class IntrigueCard:
    def __init__(self) -> None:
        self.intrigue_type: List[IntrigueType]
        self.intrigue_effects: List[CardEffect] = []

    def apply_intrigue_effects(self) -> None:
        for intrigue_effect in self.intrigue_effects:
            intrigue_effect.apply()


class IntrigueType(Enum):
    FINALE = "Finale Intrigue Card"
    COMBAT = "Combat Intrigue Card"
    AGENT = "Agent Intrigue Card"


class AgentIcon(Enum):
    EMPEROR = "Emperor"
    SPACING_GUILD = "Spacing Guild"
    BENE_GESSERIT = "Bene Gesserit"
    FREMEN = "Fremen"
    LANDSRAAD = "Landsraad"
    CITY = "City"
    SPICE_TRADE = "Spice Trade"


class CardEffect:
    def __init__(self, effect: Callable[[], None]):
        self.effect: Callable[[], None] = effect

    def apply(self):
        self.effect()
