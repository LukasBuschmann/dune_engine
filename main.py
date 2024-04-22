from transitions.extensions import GraphMachine
from transitions import Machine, Transition

from typing import Callable, List, Dict
from functools import partialmethod, partial

import demo_player as dp
import demo_game as dg

if __name__ == '__main__':
    max_troops = 12
    players = 4

    def generate_transitions(game: 'Game') -> List[Dict]:
        transitions = []
        # Agent Turn
        for card in game.cards:
            for location in game.locations:
                transition = {
                    'trigger': f'play_{card.name}_to_{location.name}',
                    'source': 'start',
                    'dest': 'agent_turn',
                    'conditions': partial(game.current_player.is_playable_to, card, location),
                    'after': partial(game.current_player.play_card_to, card, location)}
                transitions.append(transition)
        # Plot Cards
        for plot in game.plots:
            transition = {
                'trigger': f'plot_{plot.name}',
                'source': ['start', 'agent_turn', 'reveal_turn', 'shop'],
                'dest': '=',
                'conditions': partial(game.current_player.plot_is_playable, plot),
                'after': partial(game.current_player.play_plot, plot)
            }
            transitions.append(transition)
        # End Turn
        transitions.extend(
            [
                {'trigger': 'end_turn', 'source': ['agent_turn', 'reveal_turn', 'shop'], 'dest': 'end', },
                {'trigger': 'end_turn', 'source': 'start', 'dest': 'end', 'conditions': lambda: game.current_player.has_revealed},
            ]
        )
        # Reveal Turn
        transitions.extend(
            [
                {'trigger': 'reveal', 'source': 'start', 'dest': 'reveal_turn',
                 'conditions': lambda: not game.current_player.has_revealed, 'after': game.current_player.reveal},
            ]
        )
        # Shop
        shop_transition = [{'trigger': f'buy_{card.name}',
                            'source': ['reveal_turn', 'shop'],
                            'dest': 'shop',
                            'conditions': partial(game.current_player.can_buy, card),
                            'after': partial(game.current_player.buy, card)}
                           for card in game.cards]
        transitions.extend(shop_transition)
        # Garrison
        transitions.extend(
            [
                {'trigger': f'deploy_{i}',
                 'source': ['start', 'agent_turn', 'reveal_turn', 'shop'],
                 'dest': '=',
                 'conditions': partial(game.current_player.can_deploy, i),
                 'after': partial(game.current_player.deploy, i)}
                for i in range(1, max_troops)
            ]
        )
        return transitions


    game = dg.Game()
    machine = GraphMachine(
        name="player_turn",
        model=game,
        states=['start', 'agent_turn', 'reveal_turn', 'shop', 'end'],
        initial='start',
        transitions=generate_transitions(game) + [
            {'trigger': 'back', 'source': 'end', 'dest': 'start', },
        ],
    )
    game.set_game_machine(machine)

    game.walk()
