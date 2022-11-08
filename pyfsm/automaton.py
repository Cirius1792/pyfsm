from typing import TypeVar, List, Tuple
from collections.abc import Mapping
TState = TypeVar("TState", bound="State")
TAutomaton = TypeVar("TAutomaton", bound="Automaton")

class TransitionError(Exception):
    def __init__(self, state, event):
        Exception.__init__(self, f"Event {event} not supported state {state}")
        self.state = state
        self.event = event

class State(Mapping):

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
        
            
        def __getitem__(self, event):
            if event not in self.transitions:
                raise TransitionError(self.name, event)
            action = None
            if event in self.actions:
                action = self.actions[event]
            return (action, self.transitions[event])
        
        def __iter__(self):
            return self.transitions.__iter__()
        
        def __len__(self):
            return len(self.transitions)
    

class Automaton:

    def start_from(self, state_name:str) -> TAutomaton:
        pass
    
    def go_in(self, state_name:str) -> TAutomaton:
        pass

    def coming_from(self, state_name:str) -> TAutomaton:
        pass

    def because_of(self, event:str) -> TAutomaton:
        pass
    
    def doing(self, action:str) -> TAutomaton:
        pass
            