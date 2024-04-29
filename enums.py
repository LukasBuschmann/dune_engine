from enum import Enum

class Faction(Enum):
    IMPERIUM = "Imperium"
    FREMEN = "Fremen"

class Icon(Enum):
    IMPERIUM = "Imperium"
    FREMEN = "Fremen"
    DESERT = "Desert"

    def __repr__(self):
        return self.value[0]

    def __str__(self):
        return self.value[0]

class TurnType(Enum):
    AGENT = "Agent"
    REVEAL = "Reveal"


class ChoiceType(Enum):
    BOOLEAN = 'bool'
    LOCATION = 'Location'
    CARD = 'Card'
