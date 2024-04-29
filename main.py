from transitions.extensions import GraphMachine
from transitions import Machine, Transition

from typing import Callable, List, Dict
from functools import partialmethod, partial

import Effect
import demo_player as dp
import demo_game as dg
import demo_board as db
import demo_cards as dc
from enums import ChoiceType



if __name__ == '__main__':
    max_troops = 12
    players = 4


    # ToDo: find out how to make transitions work with player change
    # ToDo: Evaluate Location Effects separately

    choices = []
    choices.append((ChoiceType.BOOLEAN, [True, False]))


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
                {'trigger': 'end_turn', 'source': 'Revealed', 'dest': 'end'},
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
        transitions.append({'trigger': 'buy', 'source': 'Revealed', 'dest': 'Shop',
                            'conditions': partial(lambda: not game.current_player.has_hand_cards)})
        # Garrison
        possible_troop_counts = list(range(-max_troops, max_troops + 1))
        possible_troop_counts.remove(0)
        transitions.extend(
            [
                {'trigger': f'deploy_{i}',
                 'source': ['start', 'Revealed', 'Shop'],
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
                 'after': partial(game.current_player.pick_choice_card, card)
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
                 'conditions': partial(game.current_player.location_available, location),
                 'after': partial(game.current_player.pick_location, location)}
                for location in game.locations  # trivial cards
            ]
        )
        # Reveal
        transitions.extend(
            [
                {'trigger': 'reveal', 'source': 'start', 'dest': 'Revealing',
                 'conditions': lambda: not game.current_player.has_revealed, 'after': game.current_player.reveal},
                {'trigger': 'done_reveal', 'source': 'Revealing', 'dest': 'Revealed',
                 'conditions': lambda: not game.current_player.has_hand_cards()}
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

        # (StartNode, EndNode, EffectType)
        agent_effect_types = [('Binary Decision', 'Binary Decision', Effect.BinaryDecisionEffectWithRequirement)]
        transitions.append(
            {'trigger': 'trivial_effect',
             'source': 'Evaluate Effect',
             'dest': 'Card Played',
             'conditions': lambda: game.current_player.is_playing_trivial_card(),
             'after': lambda: game.current_player.play_current_card()}
        )
        transitions.extend(
            [
                {'trigger': 'decide_effect',
                 'source': 'Evaluate Effect',
                 'dest': effect_start_node,
                 'conditions': lambda: game.current_player.current_card.agent_effect.__class__ == effect_type}
                for effect_start_node, _, effect_type in agent_effect_types
            ]
        )
        transitions.extend(
            [
                {'trigger': 'effect_done',
                 'source': effect_end_node,
                 'dest': 'Card Played',
                 'conditions': lambda: game.current_player.current_card != None}
                for effect_start_node, effect_end_node, _ in agent_effect_types
            ]
        )

        for choice_type, choice_list in choices:
            transitions.extend([
                {'trigger': f'choice_{choice}',
                 'source': 'Choicing',
                 'dest': '=',
                 'conditions': lambda: game.current_player.has_choices() and  game.current_player.can_make_choice(choice, choice_type),
                 'after': lambda: game.current_player.make_choice(choice)}
                for choice in choice_list
            ])
        transitions.append(
            {'trigger': f'evaluate_choices',
             'source': 'Choicing',
             'dest': 'Card Played',
             'conditions': lambda: not game.current_player.has_choices(),
             'after': lambda: game.current_player.evaluate_choices()}
        )


        return transitions


    game = dg.Game()
    machine = GraphMachine(
        name="player_turn",
        model=game,
        states=['start', 'Pick Card', 'Pick Location', 'Pick Plot', 'Card Played', 'Revealing', 'Choicing', 'Shop', 'Revealed',
                'end', 'Evaluate Effect'],
        initial='start',
        transitions=generate_transitions(game) + [
            {'trigger': 'back', 'source': 'end', 'dest': 'start', 'after': partial(game.current_player.reset)},
        ],
    )
    game.set_game_machine(machine)
    game.update_graph_picture()
    game.auto_walk()
