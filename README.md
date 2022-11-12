# PyAutomaton

## Description 
PyAutomaton is a simple library implementing Mealy state machines, thus meaning that the events produced by the automaton are determined by the tuple (state, event) and not only on the current state, as happens with Moore state machines. 

## Basic Usage
PyAutomaton offers the possibility of declare State Machines by using a fluent descriptive style.
For example, given the state machine in the following figure: 
![turntile-picture](docs/imgs/turntile.png)

the code implementing this state machine is: 
```python
fsm = Automaton().start_from("locked").go_in("locked").when("push") \
                    .coming_from("locked").go_in("unlocked").when("coin") \
                    .coming_from("unlocked").go_in("unlocked").when("coin") \
                    .coming_from("unlocked").go_in("locked").when("push")
```

And the machine can run by invoking the fsm object as follow: 
```python
fsm('push')
```
each invocation triggers a state transition and returns the corresponding action, if any.

## Dump and restore the state machine 
It is possible to dump a state machine. A state machine dump is self consistent, thus meaning that it emodies both the state machine configuration as well as the current state of the automaton:
```python
dumped_machine = Automaton.dump(fsm)
machine = Automaton.load(dumped_machine)
```
The dump is produced in json format. 