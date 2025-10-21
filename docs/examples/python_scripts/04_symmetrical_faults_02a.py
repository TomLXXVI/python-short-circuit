"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Symmetrical Faults - Power System Three-Phase Short Circuits - Example 8.5
(p. 422).

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
from short_circuit import Quantity, Network, ThreePhaseFault

Q_ = Quantity

# ==============================================================================
# Per-unit impedances

X_sm1 = 0.045j   # synchronous machine bus 1
X_sm3 = 0.0225j  # synchronous machine bus 3

X_l24 = 0.1j     # line bus 2 - bus 4
X_l25 = 0.05j    # line bus 2 - bus 5
X_l45 = 0.025j   # line bus 4 - bus 5

X_t15 = 0.02j    # transformator between bus 1 and bus 5
X_t34 = 0.01j    # transformator between bus 3 and bus 4


# ==============================================================================
# Network

# NOTE!
# Branches which are connected at one end to the reference node (ground), must
# always have the reference node as their start node!
# If a branch contains a voltage source (synchronous machine), this must be
# indicated by setting parameter `has_source` to True.

nw = Network()
nw.add_branch(X_sm1, end_node_ID="1", has_source=True)
nw.add_branch(X_sm3, end_node_ID="3", has_source=True)
nw.add_branch(X_t15, start_node_ID="1", end_node_ID="5")
nw.add_branch(X_t34, start_node_ID="3", end_node_ID="4")
nw.add_branch(X_l24, start_node_ID="4", end_node_ID="2")
nw.add_branch(X_l25, start_node_ID="5", end_node_ID="2")
nw.add_branch(X_l45, start_node_ID="5", end_node_ID="4")

print(nw)  # prints the bus impedance matrix

# ==============================================================================
# Three-phase fault
fault_3ph = ThreePhaseFault(nw, U_prefault=1.05)

# ------------------------------------------------------------------------------
# Fault at bus 1
print("\nthree-phase fault at bus 1")
fault_3ph.set_faulted_node("1")

If1 = fault_3ph.get_fault_current()
print(f"fault current: {If1:.5g}")

Ix1 = fault_3ph.get_currents_to_node("1")
for k, v in Ix1:
    print(f"branch current between bus {k} and bus 1: {v:.5g}")

print(f"node voltages during fault at bus 1:")
for node in nw.nodes:
    print(f"bus {node.ID}:", f"{fault_3ph.get_node_voltage(node.ID):.5g}")

# ------------------------------------------------------------------------------
# Fault at bus 2
print("\nthree-phase fault at bus 2")
fault_3ph.set_faulted_node("2")

If2 = fault_3ph.get_fault_current()
print(f"fault current: {If2:.5g}")

Ix2 = fault_3ph.get_currents_to_node("2")
for k, v in Ix2:
    print(f"branch current between bus {k} and bus 2: {v:.5g}")

print(f"node voltages during fault at bus 2:")
for node in nw.nodes:
    print(f"bus {node.ID}:", f"{fault_3ph.get_node_voltage(node.ID):.5g}")

# ------------------------------------------------------------------------------
# Fault at bus 3
print("\nthree-phase fault at bus 3")
fault_3ph.set_faulted_node("3")

If3 = fault_3ph.get_fault_current()
print(f"fault current: {If3:.5g}")

Ix3 = fault_3ph.get_currents_to_node("3")
for k, v in Ix3:
    print(f"branch current between bus {k} and bus 3: {v:.5g}")

print(f"node voltages during fault at bus 3:")
for node in nw.nodes:
    print(f"bus {node.ID}:", f"{fault_3ph.get_node_voltage(node.ID):.5g}")

# ------------------------------------------------------------------------------
# Fault at bus 4
print("\nthree-phase fault at bus 4")
fault_3ph.set_faulted_node("4")

If4 = fault_3ph.get_fault_current()
print(f"fault current: {If4:.5g}")

Ix4 = fault_3ph.get_currents_to_node("4")
for k, v in Ix4:
    print(f"branch current between bus {k} and bus 4: {v:.5g}")

print(f"node voltages during fault at bus 4:")
for node in nw.nodes:
    print(f"bus {node.ID}:", f"{fault_3ph.get_node_voltage(node.ID):.5g}")

# ------------------------------------------------------------------------------
# Fault at bus 5
print("\nthree-phase fault at bus 5")
fault_3ph.set_faulted_node("5")

If5 = fault_3ph.get_fault_current()
print(f"fault current: {If5:.5g}")

Ix5 = fault_3ph.get_currents_to_node("5")
for k, v in Ix5:
    print(f"branch current between bus {k} and bus 5: {v:.5g}")

print(f"node voltages during fault at bus 5:")
for node in nw.nodes:
    print(f"bus {node.ID}:", f"{fault_3ph.get_node_voltage(node.ID):.5g}")
