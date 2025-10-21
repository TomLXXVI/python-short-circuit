from typing import Annotated
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray


TRange = Annotated[NDArray[np.floating | np.integer], "shape: (n,)"]


@dataclass
class SourceVoltage:
    """
    Represents a single-phase AC voltage source.

    Attributes
    ----------
    V:
        RMS AC source voltage [Volt].
    f:
        Frequency of source voltage [Hertz].
    alpha:
        Source angle that determines the source voltage at t = 0 [rad].
    V_max:
        Amplitude of AC source voltage [Volt].
    omega:
        Angular frequency of source voltage [rad/s].
    """
    V: float
    f: float
    alpha: float = 0.0

    def __post_init__(self):
        self.V_max = np.sqrt(2) * self.V
        self.omega = 2 * np.pi * self.f

    def v(self, t: float | TRange) -> float | TRange:
        return self.V_max * np.sin(self.omega * t + self.alpha)


@dataclass
class Impedance:
    """
    Represents a single-phase series impedance.

    Attributes
    ----------
    R:
        Resistance [Ohm].
    L:
        Inductance [Henry].
    C:
        Capacitance [Farad].
    f:
        Frequency [Hertz].
    omega:
        Angular frequency [rad/s].
    mXL:
        Magnitude of inductive reactance [Ohm].
    mXC:
        Magnitude of capacitive reactance [Ohm].
    """
    R: float
    L: float
    C: float
    f: float

    def __post_init__(self):
        self.omega = 2 * np.pi * self.f
        self.mXL = self.omega * self.L
        if self.C > 0.0:
            self.mXC = 1 / (self.omega * self.C)
        else:
            self.mXC = 0.0
        self._real = self.R
        self._imag = self.mXL - self.mXC

    @property
    def magnitude(self) -> float:
        """
        Returns the magnitude of the impedance [Ohm].
        """
        return np.sqrt(self._real ** 2 + self._imag ** 2)

    @property
    def phase(self) -> float:
        """
        Returns the phase angle of the impedance [rad].
        """
        return np.arctan(self._imag / self._real)


def X_to_L(X: float, f: float) -> float:
    """
    Converts inductive reactance [Ohm] to inductance [Henry].
    """
    omega = 2.0 * np.pi *  f
    L = X / omega
    return L


def X_to_C(X: float, f: float) -> float:
    """
    Converts capacitive reactance [Ohm] to capacitance [Farad].
    """
    omega = 2.0 * np.pi * f
    C = 1 / (omega * X)
    return C


@dataclass
class RLCircuit:
    """
    Represents a single-phase R-L circuit.

    Attributes
    ----------
    source_voltage:
        Source voltage of the RL-circuit.
    RL_impedance:
        Impedance of the RL-circuit.
    V:
        RMS AC source voltage [Volt].
    alpha:
        Source angle that determines the source voltage at t = 0 [rad].
    omega:
        Angular frequency of source voltage [rad/s].
    Z:
        Magnitude of the RL-circuit's impedance [Ohm].
    theta:
        Phase angle of the RL-circuit's impedance [rad].
    T:
        Time constant of the RL-circuit's impedance [s].
    Iac:
        RMS value of the ac symmetrical fault current [Ampere].
    Iac_max:
        Amplitude of the ac symmetrical fault current [Ampere].
    """
    source_voltage: SourceVoltage
    RL_impedance: Impedance

    def __post_init__(self):
        self.V = self.source_voltage.V
        self.alpha = self.source_voltage.alpha
        self.omega = self.source_voltage.omega
        self.Z = self.RL_impedance.magnitude
        self.theta = self.RL_impedance.phase
        self.T = self.RL_impedance.L / self.RL_impedance.R
        self.Iac = self.V / self.Z
        self.Iac_max = np.sqrt(2) * self.Iac

    def ac_symmetrical_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the ac fault current (symmetrical or steady-state fault
        current) [A] in the RL-circuit in case the short circuit is a solid or
        "bolted" fault (i.e. zero fault impedance).

        Parameters
        ----------
        t:
            Single time moment or a range of times since the closure of the
            switch [seconds]. Note: `TRange` indicates a 1D Numpy array of
            floats.
        """
        return self.Iac_max * np.sin(self.omega * t + self.alpha - self.theta)

    def dc_offset_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the dc offset current [A] which decays exponentially with time
        constant T = L/R.

        Parameters
        ----------
        t:
            Single time moment or a range of times since the closure of the
            switch [seconds]. Note: `TRange` indicates a 1D Numpy array of
            floats.
        """
        return -self.Iac_max * np.sin(self.alpha - self.theta) * np.exp(-t / self.T)

    def asymmetrical_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the total fault current [A].

        Parameters
        ----------
        t:
            Single time moment or a range of times since the closure of the
            switch [seconds]. Note: `TRange` indicates a 1D Numpy array of
            floats.
        """
        i_ac = self.ac_symmetrical_current(t)
        i_dc = self.dc_offset_current(t)
        return i_ac + i_dc

    def max_dc_offset_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the maximum dc-offset current [A], i.e. the dc-offset current
        when the source angle `alpha` equals the impedance angle `theta` - pi/2.

        Parameters
        ----------
        t:
            Single time moment or a range of times since the closure of the
            switch [seconds]. Note: `TRange` indicates a 1D Numpy array of
            floats.
        """
        return self.Iac_max * np.exp(-t / self.T)

    def rms_asymmetrical_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the rms asymmetrical fault current [A] with maximum dc offset.

        Parameters
        ----------
        t:
            Single time moment or a range of times since the closure of the
            switch [seconds]. Note: `TRange` indicates a 1D Numpy array of
            floats.
        """
        Idc_max = self.max_dc_offset_current(t)
        Irms = np.sqrt(self.Iac ** 2 + Idc_max ** 2)
        return Irms

    def asymmetry_factor(self, tau: float | TRange) -> float | TRange:
        """
        Returns the asymmetry factor with maximum dc offset. The rms
        asymmetrical fault current with maximum dc offset equals the rms ac
        fault current `self.Iac` times the asymmetry factor.

        Parameters
        ----------
        tau:
            Time after the occurence of the short circuit (t=0) expressed as
            number of cycles.
        """
        R = self.RL_impedance.R
        X = self.RL_impedance.mXL
        K = np.sqrt(1 + 2 * np.exp(-4 * np.pi * tau / (X / R)))
        return K
