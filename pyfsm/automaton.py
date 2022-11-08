from typing import TypeVar, List, Tuple

TState = TypeVar("TState", bound="State")
TAutomaton = TypeVar("TAutomaton", bound="Automaton")

class TransitionError(Error):
    def __init__(self, state, event):
        Error.__init__(self, f"Event {event} not supported state {state}")
        self.state = state
        self.event = event

class State:
        def __init__(self, name) -> None:
            self.name = name
            self.actions = {}
            self.transitions = {}

        def when(self, event) -> TState:
            self._event = event
            return self

        def do(self, output) -> TState:
            self.actions[self._event] = output
            return self

        def go_in(self, target:TState) -> TState:
            self.transitions[self._event] = target
            return self
        
        def get_action(self, event):
            return self.actions[event]
        
        def get_next(self, event) -> Tuple[str, TState]:
            if event not in self.transitions:
                raise TransitionError(self.name, event)
            action = None
            if event in self.actions:
                action = self.actions[event]
            return (action, self.transitions[event])
            
class Automaton:
    def __init__(self):
        self.states = {}
        self._curr = None

    def start_from(self, state_name:str) -> TAutomaton:
        self._curr = State(state_name)
        self.start = self._curr
    
    def go_in(self, target_name:str) -> TAutomaton:
        self._curr.
        