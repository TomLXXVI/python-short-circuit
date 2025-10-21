"""
Glover, J. D., Sarma, M. S., & Overbye, T. (2022). Power System Analysis and
Design, SI Edition.

Symmetrical Faults - Series R-L Circuit Transients - Example 8.1 (p. 409).
"""

import numpy as np

from short_circuit import Quantity
from short_circuit.basics.RL_circuit import SourceVoltage, Impedance, X_to_L, RLCircuit
from short_circuit.charts import LineChart

Q_ = Quantity

# ------------------------------------------------------------------------------
# Given: A bolted short circuit occurs in a series R-L circuit. The circuit
# breaker opens 3 cycles after fault inception.
# ------------------------------------------------------------------------------

V = Q_(20, 'kV').to('V').magnitude
f = 60.0
source_voltage = SourceVoltage(V, f)
impedance = Impedance(R=0.8, L=X_to_L(8.0, f), C=0.0, f=f)
circuit = RLCircuit(source_voltage, impedance)

print(f"rms ac fault current: {Q_(circuit.Iac, 'A').to('kA'):~P.3f}")

Irms = circuit.asymmetry_factor(0.5) * circuit.Iac
print(f"rms momentary current: {Q_(Irms, 'A').to('kA'):~P.3f}")

Irms = circuit.asymmetry_factor(3) * circuit.Iac
print(f"rms breaking current: {Q_(Irms, 'A').to('kA'):~P.3f}")

# Plot fault currents
T = 1 / source_voltage.f  # time duration of 1 cycle
tau = 4.0  # number of cycles
t = np.linspace(0.0, tau * T, 1000)
i_ac = circuit.ac_symmetrical_current(t)
i_dc = circuit.max_dc_offset_current(t)
i = circuit.asymmetrical_current(t)
lch = LineChart()
lch.add_xy_data(
    label="i_ac",  # ac symmetrical current
    x1_values=t,
    y1_values=Q_(i_ac, 'A').to('kA').m
)
lch.add_xy_data(
    label="i_dc",  # dc offset current
    x1_values=t,
    y1_values=Q_(i_dc, 'A').to('kA').m
)
lch.add_xy_data(
    label="i",  # resulting asymmetrical fault current
    x1_values=t,
    y1_values=Q_(i, 'A').to('kA').m
)
lch.add_legend(columns=3)
lch.x1.add_title("time, s")
lch.y1.add_title("current, kA")
lch.show()
