import model as md
from model.Round import Round
from statemachine import StateMachine, State
from statemachine.contrib.diagram import DotGraphMachine
import statemachine.callbacks

if __name__ == '__main__':
    class TestMachine(StateMachine):

        has_key = False
        def obtain_key(self):
            print("Picked Up Key!")
            self.has_key = True

        start = State('Start', initial=True)
        s_door = State('Door')
        s_bush = State('Bush', enter='obtain_key')

        start.to(s_door, event='move_door')
        start.to(s_bush, event='move_bush')
        s_bush.to(s_door, event='move_door')
        s_door.to(start, cond="has_key", event='move')

        def condition_resolver(self, *args):
            for callback in args:
                if not getattr(self, callback.func):
                    return False
            return True

        def walk(self):
            while True:
                possible_events = set()
                print(f"Current State: {self.current_state.name}")
                transitions = self.current_state.transitions
                for transition in transitions:
                    if self.condition_resolver(*transition.cond):
                        possible_events = possible_events.union(transition.events)
                if len(possible_events) == 0:
                    raise Exception("Dead End State Encountered")
                print(f"Possible Events: {possible_events}")
                choice = int(input(f"Choose an Event (0-{len(possible_events) - 1}): "))
                self.send(list(possible_events)[choice])



    sm = TestMachine()
    graph = DotGraphMachine(sm)
    dot = graph()
    dot.write_png("test.png")

    sm.walk()
