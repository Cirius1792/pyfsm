from unittest import TestCase
from pyfsm.automaton import Automaton, State, StateConfigurationError


class StatesTestCase(TestCase):
    def test_build_state(self):
        state = State("start").when("E1").do("B1")
        self.assertEqual("B1", state.get_action("E1"))
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        self.assertEqual("B1", state.get_action("E1"))
        self.assertEqual("B2", state.get_action("E2"))

    def test_build_automa(self):
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        start_state = State("start").when("E1").do("B1").go_in(state)
        self.assertEqual(state.name, start_state["E1"][1].name)

    def test_inconsistent_event(self):
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        with self.assertRaises(StateConfigurationError):
            state["E3"]

    def test_turnstile_fsm(self):
        unlocked = State("unlocked")
        unlocked.when("coin").go_in(unlocked)
        locked = State("locked").when("coin").go_in(unlocked) 
        locked.when("push").go_in(locked)
        unlocked.when("push").go_in(locked)

        curr_state = locked

        curr_state = curr_state["push"][1]
        self.assertEqual("locked", curr_state.name)
        curr_state = curr_state["coin"][1]
        self.assertEqual("unlocked", curr_state.name)
        curr_state = curr_state["push"][1]
        self.assertEqual("locked", curr_state.name)

class AutomatonTestCase(TestCase):
    
    def test_automaton(self):
        fsm = Automaton().start_from("start") \
            .when("E1").go_in("state_a").doing("B1") \
            .coming_from("start").when("E2").go_in("state_b").doing("B2") \
            .coming_from("state_b").when("E1").go_in("state_a").doing("B1")
        
        self.assertEqual("start", fsm.get_initial_state().name)
        self.assertEqual("start", fsm.get_current_state().name)
        self.assertEqual("B1", fsm("E1"))
        self.assertEqual("state_a", fsm.get_current_state().name)
        
    def test_automaton_2(self):
        fsm = Automaton().start_from("start") \
            .go_in("state_a").when("E1").doing("B1") \
            .coming_from("start").go_in("state_b").when("E2").doing("B2") \
            .coming_from("state_b").go_in("state_a").when("E1").doing("B1")
        
        self.assertEqual("start", fsm.get_initial_state().name)
        self.assertEqual("start", fsm.get_current_state().name)
        self.assertEqual("B1", fsm("E1"))
        self.assertEqual("state_a", fsm.get_current_state().name)
