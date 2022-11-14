import json
from unittest import TestCase
from pyautomaton.automaton import Automaton, State, IllegalEventError


class StatesTestCase(TestCase):
    def test_build_state_syntax2(self):
        state = State("start").when("E1").do("B1")
        self.assertEqual("B1", state.get_action("E1"))
        state = (
            State("state_a")
            .when("E1")
            .do("B1")
            .go_in(State("state_a"))
            .when("E2")
            .do("B2")
            .go_in(State("state_b"))
        )
        self.assertEqual("B1", state.get_action("E1"))
        self.assertEqual("B2", state.get_action("E2"))
        self.assertEqual("B1", state["E1"][0])
        self.assertEqual("state_a", state["E1"][1].name)
        self.assertEqual("B2", state["E2"][0])
        self.assertEqual("state_b", state["E2"][1].name)

    def test_build_state_syntax2(self):
        state = (
            State("state_a")
            .go_in(State("state_a"))
            .do("B1")
            .when("E1")
            .when("E2")
            .do("B2")
            .go_in(State("state_b"))
        )
        self.assertEqual("B1", state.get_action("E1"))
        self.assertEqual("B2", state.get_action("E2"))
        self.assertEqual("B1", state["E1"][0])
        self.assertEqual("state_a", state["E1"][1].name)
        self.assertEqual("B2", state["E2"][0])
        self.assertEqual("state_b", state["E2"][1].name)

        state = State("state_a").do("B1").when("E1").do("B2").when("E2")
        self.assertEqual("B1", state.get_action("E1"))
        self.assertEqual("B2", state.get_action("E2"))
        self.assertEqual("B1", state["E1"][0])
        self.assertEqual("state_a", state["E1"][1].name)
        self.assertEqual("B2", state["E2"][0])
        self.assertEqual("state_a", state["E2"][1].name)

    def test_build_automa(self):
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        start_state = State("start").when("E1").do("B1").go_in(state)
        self.assertEqual(state.name, start_state["E1"][1].name)

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

    def test_state_comparison(self):
        state_a = State("state_a").when("E1").do("B1").when("E2").do("B2")
        state_b = State("state_a").when("E1").do("B1").when("E2").do("B2")
        self.assertEqual(state_a, state_b, "Should be equal")

        self.assertNotEqual(state_a, "not a state", "Should fail because the reference object is not a State obj")

        state_a = State("state_a").when("E1").do("B1").when("E2").do("B2")
        state_b = State("state_b").when("E1").do("B1").when("E2").do("B2")
        self.assertNotEqual(state_a, state_b, "Should fail because of state name")

        state_a = State("state_a").when("E1").do("B1").when("E2").do("B2")
        state_b = State("state_a").when("E3").do("B1").when("E2").do("B2")
        self.assertNotEqual(state_a, state_b, "Should fail because of different event")

        state_c = State("state_c").when("E1").go_in(State("state_x"))
        state_c2 = State("state_c").when("E1").go_in(State("state_z"))
        state_a = State("state_a").when("E1").do("B1").when("E2").do("B2").go_in(state_c)
        state_b = State("state_a").when("E1").do("B1").when("E2").do("B2").go_in(state_c2)
        self.assertNotEqual(state_a, state_b, "Should fail because of different target states")

    def test_dump_state_no_transitions(self):
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        dumped_state = State.dump(state)
        expected_dump = "[ " \
                        '["state_a", "E1", "B1", "state_a"],' \
                        '["state_a", "E2", "B2", "state_a"]' \
                        " ]"
        expected_loaded = json.loads(expected_dump)
        self.assertEqual(expected_loaded, json.loads(dumped_state))

    def test_dump_state_with_transitions(self):
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        start_state = State("start").when("E1").do("B1").go_in(state)
        dumped_state = State.dump(start_state)
        expected_dump = "[ " \
                        '["start", "E1", "B1", "state_a"],' \
                        '["state_a", "E1", "B1", "state_a"],' \
                        '["state_a", "E2", "B2", "state_a"]' \
                        " ]"
        expected_loaded = json.loads(expected_dump)
        self.assertEqual(expected_loaded, json.loads(dumped_state))

    def test_load_state_with_transitions(self):
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        start_state = State("start").when("E1").do("B1").go_in(state)
        dump = "[ " \
               '["start", "E1", "B1", "state_a"],' \
               '["state_a", "E1", "B1", "state_a"],' \
               '["state_a", "E2", "B2", "state_a"]' \
               " ]"
        loaded_state = State.load(dump)
        self.assertEqual(start_state, loaded_state)

    def test_dump_and_load_state(self):
        state = State("state_a").when("E1").do("B1").when("E2").do("B2")
        start_state = State("start").when("E1").do("B1").go_in(state)

        dumped_state = State.dump(start_state)
        restored_state = State.load(dumped_state)
        self.assertEqual(start_state, restored_state)


class AutomatonTestCase(TestCase):
    def test_automaton(self):
        fsm = (
            Automaton()
            .start_from("start")
            .when("E1")
            .go_in("state_a")
            .doing("B1")
            .coming_from("start")
            .when("E2")
            .go_in("state_b")
            .doing("B2")
            .coming_from("state_b")
            .when("E1")
            .go_in("state_a")
            .doing("B1")
        )

        self.assertEqual("start", fsm.get_initial_state().name)
        self.assertEqual("start", fsm.get_current_state().name)
        self.assertEqual("B1", fsm("E1"))
        self.assertEqual("state_a", fsm.get_current_state().name)

    def test_automaton_2(self):
        fsm = (
            Automaton()
            .start_from("start")
            .go_in("state_a")
            .doing("B1")
            .when("E1")
            .coming_from("start")
            .go_in("state_b")
            .doing("B2")
            .when("E2")
            .coming_from("state_b")
            .go_in("state_a")
            .doing("B1")
            .when("E1")
        )

        self.assertEqual("start", fsm.get_initial_state().name)
        self.assertEqual("start", fsm.get_current_state().name)
        self.assertEqual("B1", fsm("E1"))
        self.assertEqual("state_a", fsm.get_current_state().name)

    def test_turnstile_fsm(self):
        fsm = (
            Automaton()
            .start_from("locked")
            .go_in("locked")
            .when("push")
            .coming_from("locked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("locked")
            .when("push")
        )
        fsm("push")
        self.assertEqual("locked", fsm.get_current_state().name)
        fsm("coin")
        self.assertEqual("unlocked", fsm.get_current_state().name)
        fsm("push")
        self.assertEqual("locked", fsm.get_current_state().name)

        with self.assertRaises(IllegalEventError):
            fsm("run")

    def test_automaton_comparison(self):
        fsm1 = (
            Automaton()
            .start_from("locked")
            .go_in("locked")
            .when("push")
            .coming_from("locked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("locked")
            .when("push")
        )
        fsm2 = (
            Automaton()
            .start_from("locked")
            .go_in("locked")
            .when("push")
            .coming_from("locked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("locked")
            .when("push")
        )
        fsm3 = (
            Automaton()
            .start_from("locked")
            .go_in("locked")
            .when("push")
            .coming_from("locked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("jumped")
            .when("push")
        )
        self.assertEqual(fsm1, fsm2)
        self.assertNotEqual(fsm1, fsm3)

    def test_dump_and_load_automaton(self):
        fsm = (
            Automaton()
            .start_from("locked")
            .go_in("locked")
            .when("push")
            .coming_from("locked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("unlocked")
            .when("coin")
            .coming_from("unlocked")
            .go_in("locked")
            .when("push")
        )

        fsm("push")

        dumped = Automaton.dump(fsm)
        restored = Automaton.load(dumped)
        self.assertEqual(fsm, restored)
