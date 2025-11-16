"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Unsymmetrical faults - Example 10.3 (p. 502): Single line-to-ground
short-circuit calculations using sequence networks.

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
    Quantity,
    PerUnitSystem,
    Network,
    LineToGroundFault,
    PolarRepresentation
)

Q_ = Quantity
CPS = PolarRepresentation

pusys_LV = PerUnitSystem(S_base=Q_(100, "MVA"), U_base=Q_(13.8, "kV"))
pusys_HV = PerUnitSystem(S_base=Q_(100, "MVA"), U_base=Q_(138.0, "kV"))

# ==============================================================================
# Sequence networks (per-unit impedances)

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

# ==============================================================================
# Line-to-ground fault at bus 2

f = LineToGroundFault([nw0, nw1, nw2], U_prefault=1.05)
f.set_faulted_node("2")

# Fault current
If_012_pu = f.get_fault_current_012()
If_abc_pu = f.get_fault_current_abc()
If_abc = pusys_LV.get_actual_current(If_abc_pu)
print(f"sequence currents: {CPS.from_complex_vector(If_012_pu)} pu")
print(f"3-phase fault current: {CPS.from_complex_vector(If_abc_pu)} pu")
print(f"3-phase fault current: {CPS.from_complex_quantity(If_abc.to('kA'))} kA")

# Voltage at the fault
Uf_012_pu = f.get_node_voltage_012("2")
Uf_abc_pu = f.get_node_voltage_abc("2")
print(f"sequence voltages: {CPS.from_complex_vector(Uf_012_pu)} pu")
print(f"3-phase fault voltage: {CPS.from_complex_vector(Uf_abc_pu)} pu")
