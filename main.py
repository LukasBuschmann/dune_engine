from transitions.extensions import GraphMachine
from transitions import Machine, Transition

from typing import Callable
from functools import partialmethod, partial

import demo_cards as dc


if __name__ == '__main__':

    def get_legal_triggers(machine):
        triggers = machine.get_triggers(machine.model.state)
        triggers = list(filter(lambda trigger: not trigger.startswith('to_'), triggers))
        legal_triggers = []
        for trigger in triggers:
            if getattr(machine.model, f'may_{trigger}')():
                legal_triggers.append(trigger)
        return list(set(legal_triggers))

    def walk(machine):
        while True:
            triggers = get_legal_triggers(machine)
            if len(triggers) == 0:
                raise Exception("Dead End state!")
            print(f'Current State: {machine.get_state(machine.model.state).name}')
            print('Actions:')
            [print(f'\t{i} - {trigger}') for i, trigger in enumerate(triggers)]
            choice = int(input(f"Choose an Action (0-{len(triggers)-1}): "))
            machine.model.trigger(triggers[choice])

    class Game(object):
        def __init__(self):
            self.money = 0
            self.cards = dc.cards
            self.hand_cards = self.cards[:-1]

        def is_playable(self, card: dc.Card):
            return card in self.hand_cards

        def play_card(self, card: dc.Card):
            card.play(self)
            self.hand_cards.remove(card)


    game = Game()
    machine = GraphMachine(
        model=game,
        states=['start', 'played_card'],
        initial='start',
        transitions=[
            {'trigger': f'play_{card.name}', 'source': 'start', 'dest': 'played_card',
             'conditions': partial(game.is_playable, card), 'after': partial(game.play_card, card)}
            for card in game.cards
        ] + [
            {'trigger': 'back', 'source': 'played_card', 'dest': 'start', }
        ],
        show_conditions=True

    )

    game.get_graph().draw('test.png', prog='dot')

    walk(machine)



