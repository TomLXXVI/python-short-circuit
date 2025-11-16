"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Unsymmetrical faults - Example 10.8 (p. 517): Double line-to-ground short-circuit
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