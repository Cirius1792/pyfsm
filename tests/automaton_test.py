from unittest import TestCase
from pyfsm.automaton import Automaton, State

class AutomatonTestCase(TestCase):

    def test_build_state(self):
        state = State("start").when("E1").do("B1")
        self.assertEqual("B1", state.get_action("E1"))
        state = State("state_a").when("E1").do("B1") \
            .when("E2").do("B2")
        self.assertEqual("B1", state.get_action("E1"))
        self.assertEqual("B2", state.get_action("E2"))
        
        start_state = State("start").when("E1")\
            .do("B1") \
            .go_in(state)
        self.assertEqual()


    # def test_build_automaton(self):
    #     """
    #              E1/B1
    #      (start) ------> (state_a)
    #          |                ^
    #          |                |  E1/B1
    #          |    E2/B2       |
    #           ----------> (state_b)
    #     """
    #     initial_state = State("start").when("E1").do("B1") \
    #         .when("E2").do("B2")
    #     state_a= State("state_b").when("E1").do("B1")
    #     state_a= State("state_a")

    #     fsm = Automaton().start_from("start") \
    #         .go_in("state_a").because_of("E1").doing("B1") \
    #         .coming_from("start").go_in("state_b").because_of("E2").doing("B2") \
    #         .coming_from("state_b").go_in("state_a").because_of("E1").doing("B1")
        
    #     self.assertEqual("start", fsm.get_initial_state())
    #     self.assertEqual("start", fsm.get_current_state())
    #     self.assertEqual("B1", fsm("E1"))
    #     self.assertEqual("state_a", fsm.get_current_state())
        