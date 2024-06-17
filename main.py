from transitions.extensions import GraphMachine
from transitions import Machine, Transition

from typing import Callable, List, Dict
from functools import partialmethod, partial

import Effect
import demo_player as dp
import demo_game as dg
from demo_board import locations
import demo_board as db
import demo_cards as dc
from enums import ChoiceType, Faction, GameState, TurnType

if __name__ == '__main__':

    # ToDo: find out how to make transitions work with player change
    # ToDo: Evaluate Location Effects separately

    def generate_transitions(game: 'Game') -> List[Dict]:

        cards = game.shop.draw_pile + game.shop.imperium_row + game.shop.foldspaces
        [cards.extend(player.hand_cards + player.deck) for player in game.players]
        # cards with no icons are not playable in agent turn
        playable_cards_agent = list(filter(lambda card: len(card.icons) != 0, cards))
        buyable_cards = game.shop.draw_pile + game.shop.imperium_row
        plots = game.shop.intrigues

        possible_troop_counts = list(range(-game.max_troops, game.max_troops + 1))
        possible_troop_counts.remove(0)

        choices = []
        choices.append((ChoiceType.BOOLEAN, [True, False]))
        choices.append((ChoiceType.FACTION, [faction for faction in Faction]))
        choices.append((ChoiceType.NUMERIC, possible_troop_counts))
        choices.append((ChoiceType.PLAYER, game.players))
        choices.append((ChoiceType.CARD, cards))
        choices.append((ChoiceType.LOCATION,  locations))

        transitions = []
        # Plot Cards
        intrigueable_nodes = ['start', 'Card Played', 'Revealed', 'Shop']

        # End Turn
        transitions.extend(
            [
                {'trigger': 'end_turn', 'source': 'Shop', 'dest': 'end', },
                {'trigger': 'end_turn', 'source': 'Revealed', 'dest': 'end'},
                {'trigger': 'end_turn', 'source': 'start', 'dest': 'end',
                 'conditions': lambda: game.current_player.has_revealed() and game.game_state != GameState.CONFLICT_OVER},
            ]
        )
        # Shop
        transitions.append({'trigger': 'buy', 'source': 'Revealed', 'dest': 'Shop',
                            'conditions': lambda: game.current_player.is_in_reveal_turn()})
        transitions.extend([{'trigger': f'buy_{card.name}_{card.id}',
                             'source': 'Shop',
                             'dest': 'Shop',
                             'conditions': partial(lambda _card: game.current_player.can_buy(_card), card),
                             'after': partial(lambda _card: game.current_player.buy(_card), card)}
                            for card in buyable_cards])
        # Garrison
        transitions.extend(
            [
                {'trigger': f'deploy_{n}',
                 'source': ['start', 'Revealed', 'Shop'],
                 'dest': '=',
                 'conditions': partial(lambda _n: game.current_player.can_change_troop_count(_n), n),
                 'after': partial(lambda _n: game.current_player.deploy(_n), n)}
                for n in possible_troop_counts
            ]
        )
        # Agent Turn
        transitions.extend(
            [
                {'trigger': f'agent_turn',
                 'source': 'start',
                 'dest': 'Pick Card',
                 'conditions': lambda: game.current_player.has_playable_card_and_agent(),
                 'after': lambda: game.current_player.remove_agent()},
                {'trigger': f'end_turn',
                 'source': 'Card Played',
                 'dest': 'end'},
            ]
        )
        # Intrigue
        transitions.extend(
            [{'trigger': 'intrigue',
              'source': intrigueable_node,
              'dest': 'Pick Intrigue',
              'conditions': lambda: game.current_player.has_playable_intrigue(),
              'after': partial(lambda _node: game.current_player.set_intrigue_origin_node(_node),
                               intrigueable_node)
              } for intrigueable_node in intrigueable_nodes]
        )
        # pick Card
        transitions.extend(
            [
                {'trigger': f'card_{card.name}_{card.id}',
                 'source': 'Pick Card',
                 'dest': 'Pick Location',
                 'conditions': partial(lambda _card: game.current_player.is_playable_card(_card), card),
                 'after': partial(lambda _card: game.current_player.pick_card(_card), card)
                 }
                for card in playable_cards_agent
            ]
        )
        # pick Location
        transitions.extend(
            [
                {'trigger': f'location_{location.name}',
                 'source': 'Pick Location',
                 'dest': 'Choicing',
                 'conditions': partial(lambda _location: game.current_player.location_available(_location), location),
                 'after': partial(lambda _location: game.current_player.pick_location(_location), location)}
                for location in game.locations
            ]
        )
        # Pick Intrigue
        transitions.extend(
            [{
                'trigger': f'plot_{plot.name}',
                'source': 'Pick Intrigue',
                'dest': 'Choicing',
                'conditions': partial(lambda _plot: game.current_player.intrigue_is_playable(_plot), plot),
                'after': partial(lambda _plot: game.current_player.pick_intrigue(_plot), plot)
            } for plot in plots])
        # Reveal
        transitions.extend(
            [
                {
                    'trigger': 'reveal',
                    'source': 'start',
                    'dest': 'Revealing',
                    'conditions': lambda: not game.current_player.has_revealed(),
                    'after': lambda: game.current_player.reveal()
                },
                {
                    'trigger': 'done_reveal',
                    'source': 'Revealing',
                    'dest': 'Revealed',
                    'conditions': lambda: not game.current_player.has_hand_cards(),
                    'after': lambda: game.current_player.done_reveal()
                },
                {
                    'trigger': 'decide_card',
                    'source': 'Revealing',
                    'dest': 'Choicing',
                    'conditions': partial(lambda: game.current_player.has_hand_cards()),
                    'after': lambda: game.current_player.reveal_current_card()
                },
                {
                    'trigger': 'evaluate_choices_reveal',
                    'source': 'Choicing',
                    'dest': 'Revealing',
                    'conditions': lambda: game.current_player.can_evaluate_reveal(),
                    'after': lambda: game.current_player.evaluate_choices_reveal()
                },
            ]
        )

        transitions.extend(
            [{'trigger': 'evaluate_choices_plot',
              'source': 'Choicing',
              'dest': intrigueable_node,
              'conditions': partial(lambda _node: game.current_player.can_evaluate_intrigue(_node), intrigueable_node),
              'after': lambda: game.current_player.evaluate_choices_intrigue()
              } for intrigueable_node in intrigueable_nodes]
        )
        # Choices
        for choice_type, choice_list in choices:
            transitions.extend([
                {'trigger': f'choice_{choice}',
                 'source': 'Choicing',
                 'dest': '=',
                 'conditions': partial(
                     lambda _choice, _choice_type: game.current_player.can_make_choice(_choice, _choice_type), choice,
                     choice_type),
                 'after': partial(lambda _choice: game.current_player.make_choice(_choice), choice)}
                for choice in choice_list
            ])
        # Location Choices
        for choice_type, choice_list in choices:
            transitions.extend([
                {'trigger': f'loc_choice_{choice}',
                 'source': 'Choicing',
                 'dest': '=',
                 'conditions': partial(
                     lambda _choice, _choice_type: game.current_player.can_make_location_choice(_choice, _choice_type),
                     choice, choice_type),
                 'after': partial(lambda _choice: game.current_player.make_location_choice(_choice), choice)}
                for choice in choice_list
            ])
        transitions.append(
            {'trigger': f'evaluate_choices_agent_location',
             'source': 'Choicing',
             'dest': 'Card Played',
             'conditions': lambda: game.current_player.can_evaluate_agent_location(),
             'after': lambda: game.current_player.evaluate_choices_agent_location()}
        )
        # Conflict
        transitions.append(
            {'trigger': f'get_conflict_reward',
             'source': 'start',
             'dest': 'Choicing',
             'conditions': lambda: game.game_state == GameState.CONFLICT_OVER,
             'after': lambda: game.current_player.pick_conflict_reward()}
        ),
        transitions.append(
            {'trigger': f'evaluate_choices_conflict',
             'source': 'Choicing',
             'dest': 'end',
             'conditions': lambda: game.current_player.current_choicing == 'conflict' and game.current_player.has_no_choices(),
             'after': lambda: game.current_player.evaluate_choices_conflict()}
        )

        return transitions

game = dg.Game()
machine = GraphMachine(
    name="player_turn",
    model=game,
    states=['start', 'Pick Card', 'Pick Location', 'Pick Intrigue', 'Card Played', 'Revealing', 'Choicing', 'Shop',
            'Revealed',
            'end', ],
    initial='start',
    transitions=generate_transitions(game) + [
        {
            'trigger': 'swap_player',
            'source': 'end',
            'dest': 'start',
            'after': lambda: (game.current_player.on_player_swap(), game.advance_player(), game.check_game_state())
        }
    ],
)
game.set_game_machine(machine)
game.update_graph_picture()

move_list=[]

game.walk(
    move_list=move_list,
    auto=True,
    debug=True
)
