from enum import Enum


# ToDo: no faction choosable?
class Faction(Enum):
    EMPEROR = "Emperor"
    FREMEN = "Fremen"
    SPACING_GUILD = "Spacing Guild"
    BENE_GESSERIT = "Bene Gesserit"


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
    COMBAT = 'Combat'
    FINALE = 'Finale'


class Statics(Enum):
    MAX_TROOPS = 12
    MAX_INFLUENCE = 6


class CardName(Enum):
    SEEK_ALLIES = "Seek Allies"
    IMPERIAL_SPY = "Imperial Spy"
    POWER_PLAY = "Power Play"
    THE_SPICE_MUST_FLOW = "The Spice Must Flow"

class LocationName(Enum):
    IMPERIAL_BASIN = "Imperial Basin"
    HAGGA_BASIN = "Hagga Basin"
    THE_GREAT_FLAT = "The Great Flat"
    AGENT_RESERVES = "Agent Reserves"
    NO_LOCATION = "No Location"

class TurnType(Enum):
    """
    We decided to abstract from the actual rules a bit for simplicity. Among
    other things the player will  only be allowed to play plot intrigues before
    choosing the turn type and inbetween the different stages of the turn
    types once. This limits possibilities for the player, but this should only
    apply to some edge cases.
    TODO: This could maybe be improved in the future.
    """

    """
    The Player has not yet decided what to do.
    In this stage it is allowed to play as many plot intrigues as they  want.
    """
    UNDECIDED = 'Undecided'

    """
    The Player has decided to play a card and send one Agent to a location.
    After picking a card and a location, the Player can play plot intrigue(s).
    Then the Player may deploy troops if possible.
    """
    AGENT = 'Agent'

    """
    The Player starts by picking the first card in his hand (Actually the Player
    is allowed to freely pick the order, in which cards get revealed. We 
    abstract for simplicity).
    After evaluating all hand cards, the player is able to buy as many cards
    in the shop as they can afford. 
    At last the Player is allowed to play plot intrigue(s) and then deploy troops.
    """
    REVEAL = 'Reveal'

    """
    The Player has the opportunity to either pass and play not conflict intrigue
    or play one conflict intrigue.
    """
    CONFLICT = 'Conflict'

    """
    The Player has the opportunity to play all of their finale intrigues. This 
    marks the last turn in the game for the player.
    """
    FINALE = 'Finale'
