"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Unsymmetrical faults - Example 10.2 (p. 499): Three-phase short-circuit
calculations using sequence networks.

Assumptions:
1.  The power system operates under balanced steady-state conditions before the
    fault occurs. Thus, the zero-, positive-, and negative-sequence networks are
    uncoupled before the fault occurs. During unsymmetrical faults, they are
    interconnected only at the fault location.
2.  Prefault load current is neglected. Because of this, the positive-sequence
    internal voltages of all machines are equal to the prefault voltage.
3.  Transformer winding resistances and shunt admittances are neglected.
4.  Transmission-line series resistances and shunt admittances are neglected.
5.  Synchronous machine armature resistance, saliency, and saturation are
    neglected.
6.  All nonrotating impedance loads are neglected.
7.  Induction motors are either neglected (especially for motors rated 50 hp or
    less) or represented in the same manner as synchronous machines.
"""
from short_circuit import (
    Network,
    ThreePhaseFault,
    transform_to_abc,
    PolarRepresentation
)

nw0 = Network()
nw0.add_branch(0.05j, end_node_ID="1")
nw0.add_branch(0.25j, end_node_ID="2")
nw0.show_impedance_matrix()

nw1 = Network()
nw1.add_branch(0.15j, end_node_ID="1", has_source=True)
nw1.add_branch(0.2j, end_node_ID="2", has_source=True)
nw1.add_branch(0.305j, start_node_ID="1", end_node_ID="2")
nw1.show_impedance_matrix()

nw2 = Network()
nw2.add_branch(0.17j, end_node_ID="1")
nw2.add_branch(0.21j, end_node_ID="2")
nw2.add_branch(0.305j, start_node_ID="1", end_node_ID="2")
nw2.show_impedance_matrix()

fault3ph = ThreePhaseFault(nw1, U_prefault=1.05)
fault3ph.set_faulted_node("2")
If3ph = fault3ph.get_fault_current()
print(If3ph)

I_abc = transform_to_abc([0.0, If3ph, 0.0])
print(PolarRepresentation.from_complex_vector(I_abc))
