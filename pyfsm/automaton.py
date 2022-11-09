from typing import TypeVar, List, Tuple
from collections.abc import Mapping

TState = TypeVar("TState", bound="State")
TAutomaton = TypeVar("TAutomaton", bound="Automaton")


class StateConfigurationError(Exception):
    def __init__(self, state, event):
        Exception.__init__(self, f"Event {event} not supported in state {state}")
        self.state = state
        self.event = event


class MissingStateDeclarationError(Exception):
    def __init__(self):
        Exception.__init__(
            self,
            f" Before to configure events, actions and target state, you must declare the starting state",
        )


class State(Mapping):
    def __init__(self, name) -> None:
        self.name = name
        self._event = None
        self.actions = {}
        self.transitions = {}

    def when(self, event) -> TState:
        self._event = event
        return self

    def do(self, output) -> TState:
        if not self._event:
            raise StateConfigurationError(self.name, None)
        self.actions[self._event] = output
        return self

    def go_in(self, target: TState) -> TState:
        if not self._event:
            raise StateConfigurationError(self.name, None)
        self.transitions[self._event] = target
        return self

    def get_action(self, event):
        return self.actions[event]

    def __getitem__(self, event):
        if event not in self.transitions:
            raise StateConfigurationError(self.name, event)
        action = None
        if event in self.actions:
            action = self.actions[event]
        return (action, self.transitions[event])

    def __iter__(self):
        return self.transitions.__iter__()

    def __len__(self):
        return len(self.transitions)


class Automaton:
    def __init__(self):
        self._current_state = None
        self._initial_state = None
        self.states = {}
        self._current_configuring_state: Optional[State] = None

    def start_from(self, state_name: str) -> TAutomaton:
        self = self.coming_from(state_name)
        self._initial_state = self.states[state_name]
        return self

    def go_in(self, state_name: str) -> TAutomaton:
        if state_name not in self.states:
            self.states[state_name] = State(state_name)
        self._current_configuring_state.go_in(self.states[state_name])
        return self

    def coming_from(self, state_name: str) -> TAutomaton:
        if state_name not in self.states:
            self.states[state_name] = State(state_name)
        self._current_configuring_state = self.states[state_name]
        return self

    def when(self, event: str) -> TAutomaton:
        if self._current_configuring_state is None:
            raise MissingStateDeclarationError()
        self._current_configuring_state.when(event)
        return self

    def doing(self, action: str) -> TAutomaton:
        if self._current_configuring_state is None:
            raise MissingStateDeclarationError()
        self._current_configuring_state.do(action)
        return self

    def get_initial_state(self) -> State:
        return self._initial_state
    
    def get_current_state(self) -> State:
        if self._current_state is None:
            self._current_state = self._initial_state
        return self._current_state
    
    def __call__(self, event):
      action, next_state = self._current_state[event]
      self._current_state = next_state
      return action  
