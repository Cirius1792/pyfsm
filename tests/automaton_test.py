from unittest import TestCase
from pyfsm.automaton import State, TransitionError


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
        with self.assertRaises(TransitionError):
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
