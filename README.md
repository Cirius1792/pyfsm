# PyFSM

## Description 
PyFSM is a simple library implementing Mealy state machines, thus meaning that the events produced by the automaton are determined by the tuple (state, event) and not only on the current state, as happens with Moore state machines. 

## Usage
PyFSM offers the possibility of declare State Machines by using a fluent descriptive style.
For example, given the state machine in the following figure: 
![turntile-picture](docs/imgs/turntile.png)

the code implementing this state machine is: 
```python
fsm = Automaton().start_from("locked").go_in("locked").when("push") \
                    .coming_from("locked").go_in("unlocked").when("coin") \
                    .coming_from("unlocked").go_in("unlocked").when("coin") \
                    .coming_from("unlocked").go_in("locked").when("push")
```