"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Symmetrical Faults - Power System Three-Phase Short Circuits - Example 8.3 + 8.4
(p. 415, p. 418).

Assumptions:
1.    Transformers are represented by their leakage reactances. Winding
      resistances, shunt admittances, and delta-Y phase shifts are neglected.
2.    Transmission lines are represented by their equivalent series reactances.
      Series resistances and shunt admittances are neglected.
3.    Synchronous machines are represented by constant-voltage sources behind
      subtransient reactances. Armature resistance, saliency, and saturation
      are neglected.
4.    All nonrotating impedance loads are neglected.
5.    Either induction motors, especially small motors rated less than 50 hp,
      are neglected or represented in the same manner as synchronous machines.
6.    Prefault load currents are neglected.
"""
from short_circuit import (
    Quantity,
    PerUnitSystem,
    Network,
    ThreePhaseFault,
    complex_number_as_polar_string
)

Q_ = Quantity

# ==============================================================================
# Per-unit impedances

pu_LV = PerUnitSystem(S_base=Q_(100, 'MVA'), U_base=Q_(13.8, 'kV'))
pu_HV = PerUnitSystem(S_base=Q_(100, 'MVA'), U_base=Q_(138, 'kV'))

Xpu_gen = 0.15j
Xpu_tr1 = 0.10j
Xpu_line = pu_HV.get_per_unit_impedance(Q_(20j, 'ohm'))
Xpu_tr2 = 0.10j
Xpu_mot = 0.20j

# ==============================================================================
# Network

# NOTE!
# Branches which are connected at one end to the reference node (ground), must
# always have the reference node as their start node!
# If a branch contains a voltage source (synchronous machine), this must be
# indicated by setting parameter `has_source` to True.

nw = Network()
nw.add_branch(Xpu_gen, end_node_ID="1", has_source=True)
nw.add_branch(Xpu_tr1, start_node_ID="1", end_node_ID="2")
nw.add_branch(Xpu_line, start_node_ID="2", end_node_ID="3")
nw.add_branch(Xpu_tr2, start_node_ID="3", end_node_ID="4")
nw.add_branch(Xpu_mot, end_node_ID="4", has_source=True)

print("Bus impedance matrix: ")
print(nw)

# ==============================================================================
# Three-phase fault

fault_3ph = ThreePhaseFault(nw, U_prefault=1.05)

# ------------------------------------------------------------------------------
# Fault at bus 1

print("\nThree-phase fault at bus 1")
fault_3ph.set_faulted_node("1")

If = fault_3ph.get_fault_current()
print(f"subtransient fault current: {If:.4g}")

Ig = fault_3ph.get_branch_current(("ref", "1"))
print(f"subtransient generator current: {Ig:.4g}")

Im = fault_3ph.get_branch_current(("ref", "4"))
print(f"subtransient motor current: {Im:.4g}")

E1 = fault_3ph.get_node_voltage("1")
print(f"voltage at bus 1 during the fault: {E1:.4g}")

E4 = fault_3ph.get_node_voltage("4")
print(f"voltage at bus 4 during the fault: {complex_number_as_polar_string(E4)}")

I23 = fault_3ph.get_branch_current(("2", "3"))
print(f"current through transmission line during the fault: {I23:.4g}")

# ------------------------------------------------------------------------------
# Fault at bus 4

print("\nThree-phase fault at bus 4")
fault_3ph.set_faulted_node("4")

If = fault_3ph.get_fault_current()
print(f"subtransient fault current: {If:.4g}")

Ig = fault_3ph.get_branch_current(("ref", "1"))
print(f"subtransient generator current: {Ig:.4g}")

Im = fault_3ph.get_branch_current(("ref", "4"))
print(f"subtransient motor current: {Im:.4g}")

E1 = fault_3ph.get_node_voltage("1")
print(f"voltage at bus 1 during the fault: {complex_number_as_polar_string(E1)}")

E4 = fault_3ph.get_node_voltage("4")
print(f"voltage at bus 4 during the fault: {complex_number_as_polar_string(E4)}")

I23 = fault_3ph.get_branch_current(("2", "3"))
print(f"current through transmission line during the fault: {I23:.4g}")
