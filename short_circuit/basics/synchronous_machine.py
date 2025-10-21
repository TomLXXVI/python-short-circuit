from dataclasses import dataclass

import numpy as np

from .RL_circuit import TRange, SourceVoltage


class TerminalVoltage(SourceVoltage):
    pass


@dataclass
class DirectAxisImpedance:
    """
    Represents the time-varying direct axis impedance of an unloaded synchronous
    machine.

    Attributes
    ----------
    subtransient:
        Direct axis subtransient reactance [Ohm] and time constant [s].
    transient:
        Direct axis transient reactance [Ohm] and time constant [s].
    synchronous:
        Direct axis synchronous reactance [Ohm].
    """
    subtransient: tuple[float, float]
    transient: tuple[float, float]
    synchronous: float

    @property
    def subtransient_reactance(self) -> float:
        """Returns subtransient reactance [Ohm]."""
        return self.subtransient[0]

    @property
    def transient_reactance(self) -> float:
        """Returns transient reactance [Ohm]."""
        return self.transient[0]

    @property
    def synchronous_reactance(self) -> float:
        """Returns synchronous reactance [Ohm]."""
        return self.synchronous

    @property
    def subtransient_timeconstant(self) -> float:
        """Returns subtransient time constant [s]."""
        return self.subtransient[1]

    @property
    def transient_timeconstant(self) -> float:
        """Returns transient time constant [s]."""
        return self.transient[1]

    def magnitude(self, t: float | TRange) -> float | TRange:
        """
        Returns the magnitude of the time-varying direct axis impedance at
        a single time moment `t` or at a range of time moments (a 1D Numpy
        array).
        """
        Xds, Tds = self.subtransient
        Xdt, Tdt = self.transient
        Xd = self.synchronous
        Y_subtransient = (1 / Xds - 1 / Xdt) * np.exp(-t / Tds)
        Y_transient = (1 / Xdt - 1 / Xd) * np.exp(-t / Tdt)
        Y_synchronous = 1 / Xd
        return 1.0 / (Y_subtransient + Y_transient + Y_synchronous)


@dataclass
class UnloadedSynchronousMachine:
    """
    Represents an unloaded synchronous machine.

    Attributes
    ----------
    terminal_voltage:
        RMS line-to-neutral prefault terminal voltage of the unloaded
        synchronous machine.
    direct_axis_impedance:
        Direct axis impedance of the unloaded synchronous machine.
    armature_time_constant:
        Armature time constant of the unloaded synchronous machine [s].
    """
    terminal_voltage: TerminalVoltage
    direct_axis_impedance: DirectAxisImpedance
    armature_time_constant: float

    def __post_init__(self):
        self.Eg = self.terminal_voltage.V

    def ac_fault_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the ac fault current [A] in case the short circuit is a solid or
        "bolted" fault (i.e. zero fault impedance).

        Parameters
        ----------
        t:
            Single time moment or a range of times since the occurence of the
            short circuit [seconds]. Note: `TRange` indicates a 1D Numpy array
            of floats.
        """
        omega = self.terminal_voltage.omega
        alpha = self.terminal_voltage.alpha
        Z = self.direct_axis_impedance.magnitude(t)
        Iac = self.Eg / Z
        Iac_max = np.sqrt(2) * Iac
        i_ac = Iac_max * np.sin(omega * t + alpha - np.pi / 2)
        return i_ac

    def max_dc_offset_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the maximum dc-offset current [A].

        Parameters
        ----------
        t:
            Single time moment or a range of times since the occurence of the
            short circuit [seconds]. Note: `TRange` indicates a 1D Numpy array
            of floats.
        """
        Xds = self.direct_axis_impedance.subtransient_reactance
        T_A = self.armature_time_constant
        Idc_max = np.sqrt(2) * self.Eg / Xds
        i_dc_max = Idc_max * np.exp(-t / T_A)
        return i_dc_max

    def asymmetrical_fault_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the total fault current [A] with maximum dc offset.

        Parameters
        ----------
        t:
            Single time moment or a range of times since the occurence of the
            short circuit [seconds]. Note: `TRange` indicates a 1D Numpy array
            of floats.
        """
        i_ac = self.ac_fault_current(t)
        i_dc_max = self.max_dc_offset_current(t)
        return i_ac + i_dc_max

    def rms_subtransient_fault_current(self) -> float:
        """
        Returns the RMS subtransient fault current [A].
        """
        Xds = self.direct_axis_impedance.subtransient_reactance
        return self.Eg / Xds

    def rms_transient_fault_current(self) -> float:
        """
        Returns the RMS transient fault current [A].
        """
        Xdt = self.direct_axis_impedance.transient_reactance
        return self.Eg / Xdt

    def rms_steady_state_fault_current(self) -> float:
        """
        Returns the RMS steady-state fault current [A].
        """
        Xd = self.direct_axis_impedance.synchronous_reactance
        return self.Eg / Xd

    def rms_asymmetrical_current(self, t: float | TRange) -> float | TRange:
        """
        Returns the rms asymmetrical fault current [A] with maximum dc offset.

        Parameters
        ----------
        t:
            Single time moment or a range of times since the occurence of the
            short circuit [seconds]. Note: `TRange` indicates a 1D Numpy array
            of floats.
        """
        Z = self.direct_axis_impedance.magnitude(t)
        Iac = self.Eg / Z
        Idc_max = self.max_dc_offset_current(t)
        I = np.sqrt(Iac ** 2 + Idc_max ** 2)
        return I
