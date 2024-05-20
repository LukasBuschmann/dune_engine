from enum import Enum

class Faction(Enum):
    EMPEROR = "Emperor"
    FREMEN = "Fremen"
    SPACING_GUILD = "Spacing Guild"
    BENE_GESSERIT = "Bene Gesserit"
    # NO_FACTION = "No Faction"

class Icon(Enum):
    EMPEROR = "Emperor"
    FREMEN = "Fremen"
    SPACING_GUILD = "Spacing Guild"
    BENE_GESSERIT = "Bene Gesserit"
    ECONOMY = "Economy"
    STATECRAFT = "Statecraft"
    SETTLEMENT = "Settlement"

    def __repr__(self):
        return self.value[0]

    def __str__(self):
        return self.value[0]


class ChoiceType(Enum):
    BOOLEAN = 'bool'
    LOCATION = 'Location'
    CARD = 'Card'
    NUMERIC = 'Numeric'
    FACTION = 'Faction'
    PLAYER = 'Player'

class Commander(Enum):
    PAUL_ARTREIDES = "Paul Artreides"
    THE_BEAST = "The Beast"
    BARON_VLADIMIR_HARKONNEN = "Baron Vladimir Harkonnen"
    DUKE_LETO_ARTREIDES = "Duke Leto Artreides"

class GameState(Enum):
    AGENT = 'Agent'
    IN_CONFLICT = 'In Conflict'
    CONFLICT_OVER = 'Conflict Over'
    FINALE = 'Finale'

class IntrigueType(Enum):
    PLOT = 'Plot'
    CONFLICT = 'Conflict'
    FINALE = 'Finale'

class TurnType(Enum):
    UNDECIDED = 'Undecided'
    AGENT = 'Agent'
    REVEAL = 'Reveal'