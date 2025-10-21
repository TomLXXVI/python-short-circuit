"""
Grainger, J. J., Stevenson, W. D., & Chang, G. W. (2016). Power System Analysis.

Symmetrical faults - The Selection of Circuit Breakers: E/X method - Example 8.7
(p. 324)

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
    convert_per_unit_impedance,
    Network,
    ThreePhaseFault,
    CircuitBreaker
)

Q_ = Quantity

# ==============================================================================
# Per-unit systems for the network

# High-voltage side of the transformer
pu_HV = PerUnitSystem(S_base=Q_(25_000, 'kVA'), U_base=Q_(13.8, 'kV'))

# Low-voltage side of the transformer
pu_LV = PerUnitSystem(S_base=Q_(25_000, 'kVA'), U_base=Q_(6.9, 'kV'))

# Per-unit system in which the per-unit impedance of the synchronous motors is
# orginally expressed:
pu_motor = PerUnitSystem(S_base=Q_(5_000, 'kVA'), U_base=Q_(6.9, 'kVA'))

# ==============================================================================
# Per-unit impedances (subtransient)

Xg = 0.15j
Xt = 0.10j
Xm = convert_per_unit_impedance(0.2j, pu_motor, pu_LV)

# ==============================================================================
# Network

# NOTE!
# Branches which are connected at one end to the reference node (ground), must
# always have the reference node as their **start** node!
# If a branch contains a voltage source (synchronous machine), this must be
# indicated by setting parameter `has_source` to True.

nw = Network()
nw.add_branch(Xg, end_node_ID="2", has_source=True)
nw.add_branch(Xt, start_node_ID="2", end_node_ID="1")
for _ in range(4):
    nw.add_branch(Xm, end_node_ID="1", has_source=True)

print("Bus impedance matrix:")
print(nw)

print("\nNetwork branches:")
for branch in nw.branches:
    print(branch)

# ==============================================================================
# Three-phase fault at bus 1

def run_short_circuit_analysis(nw_: Network):
    fault_3ph = ThreePhaseFault(nw_)

    print("\nThree-phase fault at bus 1:")
    fault_3ph.set_faulted_node("1")

    If_pu = fault_3ph.get_fault_current()
    If = pu_LV.get_actual_current(If_pu)
    print(
        f"short-circuit current in the fault: "
        f"{If_pu:.4g} pu, "
        f"{abs(If.to('A')):~P.0f}"
    )
    # Through breaker A comes the contribution from the generator and three of
    # the four motors.
    I21 = fault_3ph.get_branch_current(2)  # contribution of generator
    I31 = fault_3ph.get_branch_current(3)  # contribution of 1 motor
    I_A_pu = I21 + 3 * I31
    I_A = pu_LV.get_actual_current(I_A_pu)
    print(
        f"short-circuit current in breaker A: "
        f"{I_A_pu:.4g} pu, "
        f"{abs(I_A.to('A')):~P.0f}"
    )
    return I_A

# ------------------------------------------------------------------------------
# Subtransient fault currents (current that the circuit breaker must withstand).
print("\nSubtransient fault currents:")
run_short_circuit_analysis(nw)

# ------------------------------------------------------------------------------
# Symmetrical short-circuit interrupting currents.
# To compute the current to be interrupted by breaker A, the substransient
# reactance of the motors is multiplied by 1.5 to get an approximate value for
# the transient reactance of the motors (i.e. when breaker A starts to interrupt
# the short-circuit current after the tripping delay). The motors were added to
# branches 3 to 6 when building the network.
for i in range(3, 7):
    branch = nw.get_branch(i)
    branch.impedance = 1.5j

# After changing the impedances of the motor branches, the network (and its
# associated bus impedance matrix) needs to be rebuilt.
nw = nw.rebuild()
print("\nBus impedance matrix after rebuild:")
print(nw)

print("\nNetwork branches:")
for branch in nw.branches:
    print(branch)

print("\nSymmetrical short-circuit interrupting currents:")
I_A = run_short_circuit_analysis(nw)

# ==============================================================================
# Circuit breaker
print("\nCircuit breaker:")

cb = CircuitBreaker(
    U_nom=Q_(14.4, 'kV'),
    I_nom=Q_('nan', 'A'),
    U_max=Q_(15.5, 'kV'),
    Isc_nom=Q_(8900, 'A'),
    K=2.67
)
print(
    f"operating voltage range: "
    f"{cb.U_min.to('kV'):~P.1f}..{cb.U_max.to('kV'):~P.1f}"
)
print(
    f"maximum interrupting capability at {cb.U_min.to('kV'):~P.1f}: "
    f"{cb.Isc_max.to('A'):~P.0f}"
)
print(
    f"interrupting capability at 6.9 kV: "
    f"{cb.get_interrupting_capability(Q_(6.9, 'kV')).to('A'):~P.0f}"
)
print(
    f"circuit breaker suitable? {cb.check(I_A, Q_(6.9, 'kV'))}"
)
