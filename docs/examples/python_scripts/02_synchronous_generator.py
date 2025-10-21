"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Symmetrical Faults - Three-phase short circuit / Unloaded synchronous machine -
Example 8.2 (p. 412).
"""
import numpy as np
from short_circuit import Quantity, PerUnitSystem
from short_circuit.basics.synchronous_machine import (
    UnloadedSynchronousMachine,
    TerminalVoltage,
    DirectAxisImpedance
)
from short_circuit.charts import LineChart

Q_ = Quantity

# ------------------------------------------------------------------------------
# Given: synchronous generator feeding a network and operating at no-load. A
# bolted three-phase short circuit occurs on the load side of the breaker. The
# breaker interrupts the fault three cycles after fault inception.
# ------------------------------------------------------------------------------

# The voltage and impedance values of the synchronous generator are given in
# per unit, but our classes expect actual values. So, we need to convert per
# unit values to actual values first.
pu_system = PerUnitSystem(S_base=Q_(500, 'MVA'), U_base=Q_(20, 'kV'))

V = TerminalVoltage(
    V=pu_system.get_actual_voltage(1.05).to('V').m / (3.0 ** 0.5),  # (*)
    f=60.0,
    alpha=np.pi / 2
)
# (*): U_base of the per-unit system is a line-to-line voltage, but the
# terminal voltage of the synchronous machine is expected to be passed as a
# line-to-neutral voltage. Therefore, we need to divide by the square root of 3.
Zd = DirectAxisImpedance(
    subtransient=(pu_system.get_actual_impedance(0.15).to('ohm').m, 0.035),
    transient=(pu_system.get_actual_impedance(0.24).to('ohm').m, 2.0),
    synchronous=pu_system.get_actual_impedance(1.1).to('ohm').m
)
sync_generator = UnloadedSynchronousMachine(
    terminal_voltage=V,
    direct_axis_impedance=Zd,
    armature_time_constant=0.2
)

I_sub = Q_(sync_generator.rms_subtransient_fault_current(), 'A')
print(f"subtransient fault current: {I_sub.to('kA'):~P.3f}")
print(f"per unit: {pu_system.get_per_unit_current(I_sub):.3f}")

Idc_max = Q_(sync_generator.max_dc_offset_current(0.0), 'A')
print(f"maximum dc offset current at t=0: {Idc_max.to('kA'):~P.3f}")

# The circuit breaker interrupts the fault three cycles after fault inception.
T = 1 / 60
I = Q_(sync_generator.rms_asymmetrical_current(3 * T), 'A')
print(f"rms asymmetrical fault current at time of interruption: {I.to('kA'):~P.3f}")


# Plot short-circuit currents
t = np.linspace(0.0, 3 * T, 1000)
i_fault_ac = Q_(sync_generator.ac_fault_current(t), 'A')
i_fault_dc_max = Q_(sync_generator.max_dc_offset_current(t), 'A')
i_fault = Q_(sync_generator.asymmetrical_fault_current(t), 'A')
lch = LineChart()
lch.add_xy_data(
    label="i_fault_ac",
    x1_values=t,
    y1_values=i_fault_ac.to('kA').m
)
lch.add_xy_data(
    label="i_fault_dc_max",
    x1_values=t,
    y1_values=i_fault_dc_max.to('kA').m
)
lch.add_xy_data(
    label="i_fault",
    x1_values=t,
    y1_values=i_fault.to('kA').m
)
lch.add_legend(columns=3)
lch.x1.add_title("time, s")
lch.y1.add_title("current, kA")
lch.show()
