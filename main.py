from transitions.extensions import GraphMachine
from transitions import Machine, Transition

from typing import Callable, List, Dict
from functools import partialmethod, partial

import Effect
import demo_player as dp
import demo_game as dg
import demo_board as db
import demo_cards as dc
from enums import ChoiceType, Faction

if __name__ == '__main__':


    # ToDo: find out how to make transitions work with player change
    # ToDo: Evaluate Location Effects separately


    def generate_transitions(game: 'Game') -> List[Dict]:

        def cp(game, function_on_cp):
            return function_on_cp(game.current_player)

        choices = []
        choices.append((ChoiceType.BOOLEAN, [True, False]))
        choices.append((ChoiceType.FACTION, [faction for faction in Faction]))
        choices.append((ChoiceType.NUMERIC, list(range(-game.max_troops, game.max_troops + 1))))

        transitions = []
        # Plot Cards
        plotable_states = ['start', 'Card Played', 'Revealed', 'Shop']

        # End Turn
        transitions.extend(
            [
                {'trigger': 'end_turn', 'source': 'Shop', 'dest': 'end', },
                {'trigger': 'end_turn', 'source': 'Revealed', 'dest': 'end'},
                {'trigger': 'end_turn', 'source': 'start', 'dest': 'end',
                 'conditions': lambda: game.current_player.has_revealed()},
            ]
        )
        # Shop
        shop_transition = [{'trigger': f'buy_{card.name}',
                            'source': 'Shop',
                            'dest': 'Shop',
                            'conditions': partial(lambda _card: game.current_player.can_buy(_card), card),
                            'after': partial(lambda _card: game.current_player.buy(_card), card)}
                           for card in game.cards]
        transitions.extend(shop_transition)
        transitions.append({'trigger': 'buy', 'source': 'Revealed', 'dest': 'Shop',
                            'conditions': lambda: not game.current_player.has_hand_cards()})
        # Garrison
        possible_troop_counts = list(range(-game.max_troops, game.max_troops + 1))
        possible_troop_counts.remove(0)
        transitions.extend(
            [
                {'trigger': f'deploy_{i}',
                 'source': ['start', 'Revealed', 'Shop'],
                 'dest': '=',
                 'conditions': partial(lambda _i: game.current_player.can_change_troop_count(_i), i),
                 'after': partial(lambda _i: game.current_player.deploy(_i), i)}
                for i in possible_troop_counts
            ]
        )
        # Agent Turn
        transitions.extend(
            [
                {'trigger': f'agent_turn',
                 'source': 'start',
                 'dest': 'Pick Card',
                 'conditions': lambda: game.current_player.has_playable_card()},
                {'trigger': f'end_turn',
                 'source': 'Card Played',
                 'dest': 'end'},
            ]
        )
        # Plot
        transitions.extend(
            [{'trigger': 'plot',
              'source': plotable_state,
              'dest': 'Pick Plot',
              'conditions': lambda: game.current_player.has_playable_plot(),
              'after': partial(lambda _plotable_state: game.current_player.set_last_state(_plotable_state), plotable_state)
              } for plotable_state in plotable_states]
        )
        # pick Card
        transitions.extend(
            [
                {'trigger': f'card_{card.name}',
                 'source': 'Pick Card',
                 'dest': 'Pick Location',
                 'conditions': partial(lambda _card: game.current_player.is_playable_card(_card), card),
                 'after': partial(lambda _card: game.current_player.pick_card(card), card)
                 }
                for card in game.cards  # trivial cards
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
                for location in game.locations  # trivial cards
            ]
        )
        # pick Plot
        transitions.extend(
            [{
                'trigger': f'plot_{plot.name}',
                'source': 'Pick Plot',
                'dest': 'Choicing',
                'conditions': partial(lambda _plot: game.current_player.plot_is_playable(_plot), plot),
                'after': partial(lambda _plot: game.current_player.pick_plot(_plot), plot)
            } for plot in game.plots])
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
              'dest': plotable_state,
              'conditions': lambda: game.current_player.can_evaluate_plot(),
              'after': lambda: game.current_player.evaluate_choices_plot()
              } for plotable_state in plotable_states]
        )
        # Choices
        for choice_type, choice_list in choices:
            transitions.extend([
                {'trigger': f'choice_{choice}',
                 'source': 'Choicing',
                 'dest': '=',
                 'conditions': partial(lambda _choice, _choice_type: game.current_player.can_make_choice(_choice, _choice_type), choice, choice_type),
                 'after': partial(lambda _choice: game.current_player.make_choice(_choice), choice)}
                for choice in choice_list
            ])
        # Location Choices
        for choice_type, choice_list in choices:
            transitions.extend([
                {'trigger': f'loc_choice_{choice}',
                 'source': 'Choicing',
                 'dest': '=',
                 'conditions': partial(lambda _choice, _choice_type: game.current_player.can_make_location_choice(_choice, _choice_type), choice, choice_type),
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

        return transitions

game = dg.Game()
machine = GraphMachine(
    name="player_turn",
    model=game,
    states=['start', 'Pick Card', 'Pick Location', 'Pick Plot', 'Card Played', 'Revealing', 'Choicing', 'Shop',
            'Revealed',
            'end', ],
    initial='start',
    transitions=generate_transitions(game) + [
        {'trigger': 'swap_player', 'source': 'end', 'dest': 'start', 'after': lambda: (game.current_player.reset(), game.advance_player())},
    ],
)
game.set_game_machine(machine)
game.update_graph_picture()

game.auto_walk()
# game.walk()