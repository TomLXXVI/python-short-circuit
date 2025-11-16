"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Unsymmetrical faults - Example 10.5 (p. 510): Double line-to-ground short-circuit
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
    Quantity,
    PerUnitSystem,
    Network,
    DoubleLineToGroundFault,
    PolarRepresentation,
    transform_to_abc
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

f = DoubleLineToGroundFault([nw0, nw1, nw2], U_prefault=1.05)
f.set_faulted_node("2")

# Fault current
If_012_pu = f.get_fault_current_012()
If_abc_pu = f.get_fault_current_abc()
If_abc = pusys_LV.get_actual_current(If_abc_pu)
In = If_abc[1] + If_abc[2]
print("\nFAULT CURRENT:")
print(
    f"sequence components of fault current (per-unit): "
    f"{CPS.from_complex_vector(If_012_pu)}"
)
print(
    f"3-phase fault current (per-unit): "
    f"{CPS.from_complex_vector(If_abc_pu)}"
)
print(
    f"3-phase fault current (kA): "
    f"{CPS.from_complex_quantity(If_abc.to('kA'))}"
)
print(
    f"neutral fault current (kA): "
    f"{CPS.from_complex_quantity(In.to('kA'))}"
)

# Voltage at the fault
Uf_012_pu = f.get_node_voltage_012("2")
Uf_abc_pu = f.get_node_voltage_abc("2")
print("\nVOLTAGE AT FAULT:")
print(
    f"sequence components of fault voltage (per-unit): "
    f"{CPS.from_complex_vector(Uf_012_pu)}"
)
print(
    f"3-phase fault voltage (per-unit): "
    f"{CPS.from_complex_vector(Uf_abc_pu)}"
)

# Contributions to the fault current from motor and transmission line
I_line_012_pu = f.get_branch_current_012(("1", "2"))       # branch 1 -> 2
I_motor_012_pu = f.get_branch_current_012(("ref", "2"))    # branch ground -> 2
I_line_abc_pu = f.get_branch_current_abc(("1", "2"))
I_motor_abc_pu = f.get_branch_current_abc(("ref", "2"))
I_line_abc = pusys_HV.get_actual_current(I_line_abc_pu)
I_motor_abc = pusys_LV.get_actual_current(I_motor_abc_pu)
print("\nCONTRIBUTIONS TO THE FAULT CURRENT:")
print(
    f"sequence currents in transmission line (per-unit): "
    f"{CPS.from_complex_vector(I_line_012_pu)}"
)
print(
    f"sequence currents in motor (per-unit): "
    f"{CPS.from_complex_vector(I_motor_012_pu)}"
)
print(
    f"three-phase currents in transmission line (per-unit): "
    f"{CPS.from_complex_vector(I_line_abc_pu)}"
)
print(
    f"three-phase currents in motor (per-unit): "
    f"{CPS.from_complex_vector(I_motor_abc_pu)}"
)
print(
    f"three-phase currents in transmission line (kA): "
    f"{CPS.from_complex_quantity(I_line_abc.to('kA'))}"
)
print(
    f"three-phase currents in motor (kA): "
    f"{CPS.from_complex_quantity(I_motor_abc.to('kA'))}"
)

# Alternative way to get all the contributions to the fault current at once:
Ix2_012 = f.get_currents_to_node_012("2")
print("\nCONTRIBUTIONS TO THE FAULT CURRENT (ALTERNATIVE WAY):")
for x, I_012 in Ix2_012:
    I_abc = transform_to_abc(I_012)
    print(
        f"sequence components of current from node '{x}' (per-unit): "
        f"{CPS.from_complex_vector(I_012)}"
    )
    print(
        f"three-phase current from node '{x}' (per-unit): "
        f"{CPS.from_complex_vector(I_abc)}"
    )
