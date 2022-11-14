from typing import TypeVar, Set, Tuple, Dict, Optional, List
from collections.abc import Mapping
from collections import namedtuple

import json

TState = TypeVar("TState", bound="State")
TAutomaton = TypeVar("TAutomaton", bound="Automaton")

ActionTargetTuple = namedtuple("ActionTargetTuple", "action target")


class MissingStateDeclarationError(Exception):
    """This error is thrown when an action, event or target state is provided to the configuration API before to declare the source state."""

    def __init__(self):
        Exception.__init__(
            self,
            f" Before to configure events, actions and target state, you must declare the starting state",
        )


class IllegalEventError(Exception):
    """This error is thrown when an event is issued in a state in which it is not allowed."""

    def __init__(self, state, event):
        Exception.__init__(self, f"Event {event} not supported in state {state}")
        self.state = state
        self.event = event


class State(Mapping):
    """
    Represents the state of Finite State Machine, characterized by:
     - state name
     - transition matrix, in which for each event is specified if a transition will occur and the next corresponding
     state
     - actions to be performed for each event occurring in the current state
    """

    def __init__(
        self,
        name,
    ) -> None:
        self.name = name
        self.transitions: Dict[ActionTargetTuple] = {}
        self._event = None
        self._action = None
        self._target = None

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

    def do(self, action) -> TState:
        """Define the action associated with the transition."""
        if not self._event:
            self._action = action
            return self
        if self._event in self.transitions:
            target = self.transitions[self._event].target
        elif self._target is None:
            target = self
        else:
            target = self._target
        self.transitions[self._event] = ActionTargetTuple(action, target)
        return self

    def go_in(self, target: TState) -> TState:
        """Define the state to go in when the transition will occur."""
        if not self._event:
            self._target = target
            return self
        if self._event in self.transitions:
            action = self.transitions[self._event].action
        else:
            action = self._action
        self.transitions[self._event] = ActionTargetTuple(action, target)
        return self

    def __repr__(self):
        return "State: " + self.name

    def get_action(self, event):
        """Return the action associated to the transition that will occurr when the event will be recieved."""
        return self.transitions[event].action

    def __getitem__(self, event) -> Tuple[str, TState]:
        """Return the action, if any, and the state associated to the given event.

        An IllegalEventError is raised fi the event is not allowed in this state."""
        if event in self.transitions:
            action_target = self.transitions[event]
            return action_target.action, action_target.target
        else:
            raise IllegalEventError(self.name, event)

    def __contains__(self, event):
        """Returns true if the event is allowed in this state."""
        return event in self.transitions

    def __iter__(self):
        """Iterate over all the event and transitions defined for this state."""
        return self.transitions.__iter__()

    def __len__(self):
        """Return the number of events defined over this state."""
        return len(self.transitions)

    def __eq__(self, o):
        """Compare the state and all the subgraph made by the possible transitions starting from this state."""
        def _eq(state_a, state_b, visited):
            if not isinstance(state_b, State):
                return False
            if state_a.name == state_b.name and state_a.name in visited:
                return True
            if state_a.name != state_b.name:
                return False
            if set(state_a.transitions.keys()) != set(state_b.transitions.keys()):
                return False
            visited.add(state_a.name)
            for k, v in state_a.transitions.items():
                if v.action != state_b.transitions[k].action or not _eq(
                    v.target, state_b.transitions[k].target, visited
                ):
                    return False
            return True

        return _eq(self, o, set())

    def __dict__(self):
        def _dump(current: State, visited: Set[str]) -> List[Tuple]:
            if current.name in visited:
                return []
            nodes = []
            visited.add(current.name)
            for event, action_target_tuple in current.transitions.items():
                nodes.append(
                    (
                        current.name,
                        event,
                        action_target_tuple.action,
                        action_target_tuple.target.name,
                    )
                )
                nodes = nodes + _dump(action_target_tuple.target, visited)
            return nodes

        return _dump(self, set())

    @staticmethod
    def dump(state: TState) -> str:
        """Return a string dump of the state in json format, inlcuding all the transitions and actions in its subgraph."""
        return json.dumps(state.__dict__())

    @staticmethod
    def load(states_dump: str):
        """Return a State object starting from a string dump of the state in json."""
        states_list = json.loads(states_dump)
        this = None
        states = {}
        for name, event, action, target in states_list:
            if name not in states:
                states[name] = State(name)
            if target not in states:
                states[target] = State(target)
            curr = states[name]
            curr.do(action)
            if name != target:
                curr.go_in(states[target])
            curr.when(event)
            if this is None:
                this = curr
        return this


class Automaton:
    """Utility class to define and use state machines."""

    def __init__(self, name=None, version=1):
        self._current_state = None
        self._initial_state = None
        self.states = {}
        self._current_configuring_state: Optional[State] = None
        self.name = name
        self.version = version

    def start_from(self, state_name: str) -> TAutomaton:
        """Define the initial state."""
        self = self.coming_from(state_name)
        self._initial_state = self.states[state_name]
        return self

    def go_in(self, state_name: str) -> TAutomaton:
        """Define the target state to go in when a given event occurrs."""
        if state_name not in self.states:
            self.states[state_name] = State(state_name)
        self._current_configuring_state.go_in(self.states[state_name])
        return self

    def coming_from(self, state_name: str) -> TAutomaton:
        """Define the source state for the following event, action and target state definitions."""
        if state_name not in self.states:
            self.states[state_name] = State(state_name)
        self._current_configuring_state = self.states[state_name]
        return self

    def when(self, event: str) -> TAutomaton:
        """Define the event triggering the transition."""
        if self._current_configuring_state is None:
            raise MissingStateDeclarationError()
        self._current_configuring_state.when(event)
        return self

    def doing(self, action: str) -> TAutomaton:
        """Define the action to perform when an event occurrs."""
        if self._current_configuring_state is None:
            raise MissingStateDeclarationError()
        self._current_configuring_state.do(action)
        return self

    def get_initial_state(self) -> State:
        """Return the initial state of the automaton."""
        return self._initial_state

    def get_current_state(self) -> State:
        """Return the current state of the automaton."""
        if self._current_state is None:
            self._current_state = self._initial_state
        return self._current_state

    def set_current_state(self, state_name):
        """Set the current state of the state machine"""
        self._current_state = self.states[state_name]

    def __call__(self, event):
        """Execute the state transition binded with the given event.

        The action associated with the executed transition is returned and the current state of the automaton is updated.
        """
        if self._current_state is None:
            self._current_state = self._initial_state
        if event not in self._current_state:
            raise IllegalEventError(self._current_state.name, event)
        action, next_state = self._current_state[event]
        self._current_state = next_state
        return action

    def __eq__(self, o):
        if not isinstance(o, Automaton) or o is None:
            return False

        return (
            self.name != o.name
            or self._initial_state == o.get_initial_state()
            or self.get_current_state().name != o.get_current_state().name
        )

    def __dict__(self):
        dct = {"states": self._initial_state.__dict__()}
        if self.name:
            dct["name"] = self.name
        dct["version"] = self.version
        dct["current_state"] = self._current_state.name
        dct["initial_state"] = self._initial_state.name
        return dct

    @staticmethod
    def dump(automaton: TAutomaton):
        return json.dumps(automaton.__dict__())

    @staticmethod
    def load(automaton_dump):
        dct = json.loads(automaton_dump)
        this = Automaton()
        if "name" in dct:
            this.name = dct["name"]
        this.version = dct["version"]
        state_list = dct["states"]
        start_state = None
        for name, event, action, target in state_list:
            if start_state is None:
                this.start_from(name)
            else:
                this.coming_from(name)
            this.go_in(target).doing(action).when(event)
        this.set_current_state(dct["current_state"])
        this._initial_state = this.states[dct["initial_state"]]
        return this
