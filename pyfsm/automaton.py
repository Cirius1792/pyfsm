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


class IllegalEventError(Exception):
    """This error is thrown when an event is issued in a state in which it is not allowed """
    def __init__(self, state, event):
        Exception.__init__(self, f"Event {event} not supported in state {state}")
        self.state = state
        self.event = event


class State(Mapping):
    """
    Represents the state of Finite State Machine, characterized by:
     - state name
     - transition matrix, in which for each event is specified if a transition will occurr and the next corresponding state
     - actions to be perfomed for each event occurring in the current state
    """

    def __init__(self, name, fail_for_undefined_events=False) -> None:

        self.name = name
        self.actions = {}
        self.transitions = {}
        self._event = None
        self._action = None
        self._target = None
        self._strict_mode = fail_for_undefined_events

    def _reset(self):
        self._event = None
        self._action = None
        self._target = None

    def when(self, event) -> TState:
        """
        specify the event triggering the transition
        """
        self._event = event
        clear = False
        if self._action:
            self.do(self._action)
            clear = True
        if self._target is not None:
            self.go_in(self._target)
            clear = True
        if clear:
            self._reset()
        return self

    def do(self, output) -> TState:
        """What to do when the transition will occurr"""
        if not self._event:
            self._action = output
            return self
        self.actions[self._event] = output
        return self

    def go_in(self, target: TState) -> TState:
        "In which state to go when the transition will occurr"
        if not self._event:
            self._target = target
            return self
        self.transitions[self._event] = target
        return self

    def __repr__(self):
        return "State: " + self.name

    def get_action(self, event):
        """Return the action associated to the transition that will occurr when the event event will be recieved"""
        return self.actions[event]

    def __getitem__(self, event) -> Tuple[str, TState]:
        target = self
        if event in self.transitions:
            target = self.transitions[event]
        action = None
        if event in self.actions:
            action = self.actions[event]
        elif self._strict_mode:
            raise StateConfigurationError(self.name, event)
        return (action, target)

    def __contains__(self, event):
        return event in self.transitions

    def __iter__(self):
        return self.transitions.__iter__()

    def __len__(self):
        return len(self.transitions)

    def __eq__(self, o):
        if not isinstance(o, State):
            return False
        if self.name != o.name:
            return False
        if set(self.transitions.keys()) != set(o.transitions.keys()):
            return False
        if set(self.actions.keys()) != set(o.actions.keys()):
            return False
        for k, v in self.transitions.items():
            if v != o.transitions[k]: return False
        for k, v in self.actions.items():
            if v != o.actions[k]: return False
        return True

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
        if self._current_state is None:
            self._current_state = self._initial_state
        if event not in self._current_state:
            raise IllegalEventError(self._current_state.name, event)
        action, next_state = self._current_state[event]
        self._current_state = next_state
        return action
