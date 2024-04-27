from transitions.extensions import GraphMachine
from transitions import Machine, Transition

from typing import Callable, List, Dict
from functools import partialmethod, partial

import demo_player as dp
import demo_game as dg
import demo_cards as dc


if __name__ == '__main__':
    max_troops = 12
    players = 4


    def generate_transitions(game: 'Game') -> List[Dict]:
        transitions = []
        # Plot Cards
        plotable_states = ['start', 'Card Played', 'Shop']
        for plot in game.plots:
            for state in plotable_states:
                transition = {
                    'trigger': f'plot_{plot.name}',
                    'source': 'Pick Plot',
                    'dest': state,
                    'conditions': partial(game.current_player.can_return_to_by_plot, plot, state),
                    'after': partial(game.current_player.play_plot, plot)
                }
                transitions.append(transition)
        transitions.extend(
            [{'trigger': 'plot',
              'source': plotable_state,
              'dest': 'Pick Plot',
              'conditions': game.current_player.has_playable_plot,
              'after': partial(game.current_player.set_last_state, plotable_state
                               )} for plotable_state in plotable_states]
        )
        # End Turn
        transitions.extend(
            [
                {'trigger': 'end_turn', 'source': 'Shop', 'dest': 'end', },
                {'trigger': 'end_turn', 'source': 'Revealing', 'dest': 'end', 'conditions': partial(lambda: not game.current_player.has_hand_cards)},
                {'trigger': 'end_turn', 'source': 'start', 'dest': 'end',
                 'conditions': lambda: game.current_player.has_revealed},
            ]
        )
        # Shop
        shop_transition = [{'trigger': f'buy_{card.name}',
                            'source': 'Shop',
                            'dest': 'Shop',
                            'conditions': partial(game.current_player.can_buy, card),
                            'after': partial(game.current_player.buy, card)}
                           for card in game.cards]
        transitions.extend(shop_transition)
        transitions.append({'trigger': 'buy', 'source': 'Revealing', 'dest': 'Shop', 'conditions': partial(lambda: not game.current_player.has_hand_cards)})
        # Garrison
        possible_troop_counts = list(range(-max_troops, max_troops+1))
        possible_troop_counts.remove(0)
        transitions.extend(
            [
                {'trigger': f'deploy_{i}',
                 'source': ['start', 'Revealing', 'Shop'],
                 'dest': '=',
                 'conditions': partial(game.current_player.can_change_troop_count, i),
                 'after': partial(game.current_player.deploy, i)}
                for i in possible_troop_counts
            ]
        )
        # TRIVIAL Card Play V2
        transitions.extend(
            [
                {'trigger': f'agent_turn',
                 'source': 'start',
                 'dest': 'Pick Card',
                 'conditions': partial(game.current_player.has_playable_card)},
                {'trigger': f'end_turn',
                 'source': 'Card Played',
                 'dest': 'end'},
            ]
        )
        # pick Card
        transitions.extend(
            [
                {'trigger': f'card_{card.name}',
                 'source': 'Pick Card',
                 'dest': 'Pick Location',
                 'conditions': partial(game.current_player.is_playable_card, card),
                 'after': partial(game.current_player.pick_card, card)}
                for card in game.cards  # trivial cards
            ]
        )
        # pick Location
        transitions.extend(
            [
                {'trigger': f'location_{location.name}',
                 'source': 'Pick Location',
                 'dest': 'Card Played',
                 'conditions': partial(game.current_player.location_available, location),
                 'after': partial(game.current_player.play_current_card_and_occupy, location)}
                for location in game.locations  # trivial cards
            ]
        )

        # Reveal
        transitions.extend(
            [
                {'trigger': 'reveal', 'source': 'start', 'dest': 'Revealing',
                 'conditions': lambda: not game.current_player.has_revealed, 'after': game.current_player.reveal},
            ]
        )
        transitions.extend(
            [
                {'trigger': f'decision_yes',
                 'source': 'Revealing',
                 'dest': 'Revealing',
                 'conditions': partial(game.current_player.can_make_reveal_decision, card),
                 'after': partial(game.current_player.make_reveal_decision, card, True)}
                for card in list(
                filter(lambda card: card.reveal_effect.__class__ == dc.BinaryDecisionEffectWithRequirement, game.cards))
            ]
        )
        transitions.extend(
            [
                {'trigger': f'decision_no',
                 'source': 'Revealing',
                 'dest': 'Revealing',
                 'conditions': partial(game.current_player.can_make_reveal_decision, card),
                 'after': partial(game.current_player.make_reveal_decision, card, False)}
                for card in list(
                filter(lambda card: card.reveal_effect.__class__ == dc.BinaryDecisionEffectWithRequirement, game.cards))
            ]
        )

        return transitions


    game = dg.Game()
    machine = GraphMachine(
        name="player_turn",
        model=game,
        states=['start', 'Pick Card', 'Pick Location', 'Pick Plot', 'Card Played', 'Revealing', 'Shop',
                'end'],
        initial='start',
        transitions=generate_transitions(game) + [
            {'trigger': 'back', 'source': 'end', 'dest': 'start', },
        ],
    )
    game.set_game_machine(machine)

    game.walk()
