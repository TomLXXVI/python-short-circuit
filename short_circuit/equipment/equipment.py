from typing import Optional
import math
import cmath
from short_circuit import Quantity

class PowerGrid:

    def __init__(
        self,
        line_voltage: Quantity,
        short_circuit_power: Quantity,
        R_to_X_ratio: float = 0.1,
        voltage_factor: float = 1.0
    ) -> None:
        self.U_line = line_voltage
        self.S_sc = short_circuit_power
        self.c = voltage_factor
        self.R_to_X_ratio = R_to_X_ratio

    @property
    def Z1(self) -> Quantity:
        U_line = self.U_line.to('V').magnitude
        S_sc = self.S_sc.to('VA').magnitude
        Z_mag = self.c * U_line ** 2 / S_sc
        X = Z_mag / math.sqrt(1 + self.R_to_X_ratio ** 2)
        R = self.R_to_X_ratio * X
        Z_ph = math.atan2(X, R)
        Z = cmath.rect(Z_mag, Z_ph)
        return Quantity(Z, 'ohm')


class Transformer:

    def __init__(
        self,
        nominal_voltage: Quantity,
        nominal_power: Quantity,
        percent_short_circuit_voltage: Quantity,
        copper_loss: Optional[Quantity] = None,
        voltage_factor: float = 1.0
    ) -> None:
        self.U_nom = nominal_voltage
        self.S_nom = nominal_power
        self.u_sc = percent_short_circuit_voltage
        self.P_Cu = copper_loss
        self.c = voltage_factor

    @property
    def Z1(self) -> Quantity:
        U_nom = self.U_nom.to('V').magnitude
        S_nom = self.S_nom.to('VA').magnitude
        u_sc = self.u_sc.to('frac').magnitude
        if self.P_Cu is not None:
            P_Cu = self.P_Cu.to('W').magnitude
            R = P_Cu * (U_nom / S_nom) ** 2
        else:
            R = 0.0
        Z_mag = u_sc * U_nom ** 2 / S_nom
        X = math.sqrt(Z_mag ** 2 - R ** 2)
        sin_phi = 0.6
        x = X / (U_nom ** 2 / S_nom)
        Z_mag *= 0.95 * self.c / (1.0 + x * sin_phi)
        Z_ph = math.atan2(X, R)
        Z = cmath.rect(Z_mag, Z_ph)
        return Quantity(Z, 'ohm')


class Generator:

    def __init__(
        self,
        nominal_voltage: Quantity,
        nominal_power: Quantity,
        per_unit_reactance: Quantity,
        power_factor: float = 0.8,
        R_to_X_ratio: float = 0.15,
        voltage_factor: float = 1.0
    ) -> None:
        self.U_nom = nominal_voltage
        self.S_nom = nominal_power
        self.x = per_unit_reactance
        self.cos_phi = power_factor
        self.R_to_X_ratio = R_to_X_ratio
        self.c = voltage_factor

    @property
    def Z1(self) -> Quantity:
        U_nom = self.U_nom.to('V').magnitude
        S_nom = self.S_nom.to('VA').magnitude
        x = self.x.to('frac').magnitude
        Z_nom = U_nom ** 2 / S_nom
        X = x * Z_nom
        R = self.R_to_X_ratio * X
        Z_mag = math.sqrt(R ** 2 + X ** 2)
        sin_phi = math.sqrt(1 - self.cos_phi ** 2)
        Z_mag *= self.c / (1 + x * sin_phi)
        Z_ph = math.atan2(X, R)
        Z = cmath.rect(Z_mag, Z_ph)
        return Quantity(Z, 'ohm')


class SynchronousMotor(Generator):
    pass


class Cable:

    rho_20 = {
        'Cu': Quantity(0.01851, 'ohm * mm ** 2 / m'), 
        'Al': Quantity(0.02941, 'ohm * mm ** 2 / m')
    }
    
    x = {
        'bus_bar': Quantity(0.150e-3, 'ohm / m'),
        'cable': Quantity(0.080e-3, 'ohm / m'),
        'single_core_spaced': Quantity(0.150e-3, 'ohm / m'),
        'single_core_spaced_2r': Quantity(0.145e-3, 'ohm / m'),
        'single_core_spaced_4r': Quantity(0.190e-3, 'ohm / m'),
        'single_core_triangle': Quantity(0.085e-3, 'ohm / m'),
        'single_core_flat': Quantity(0.095e-3, 'ohm / m')
    }

    @classmethod
    def get_resistivity(cls, T: Quantity, material: str = 'Cu'):
        return cls.rho_20[material] * (1.0 + 0.004 * (T.to('K').magnitude - 293.0))

    def __init__(
        self,
        length: Quantity,
        cross_section: Quantity,
        resistivity: Quantity,
        unit_reactance: Quantity
    ) -> None:
        self.L = length
        self.A = cross_section
        self.r = resistivity
        self.x = unit_reactance

    @property
    def Z1(self) -> Quantity:
        r = self.r.to('ohm * mm ** 2 / m').magnitude
        x = self.x.to('ohm / m').magnitude
        L = self.L.to('m').magnitude
        A = self.A.to('mm ** 2').magnitude
        R = r * L / A
        X = x * L
        Z_mag = math.sqrt(R ** 2 + X ** 2)
        Z_ph = math.atan2(X, R)
        Z = cmath.rect(Z_mag, Z_ph)
        return Quantity(Z, 'ohm')


class InductionMotor:

    def __init__(
        self,
        nominal_voltage: Quantity,
        nominal_current: Quantity,
        locked_rotor_current: Quantity,
        P_m: Quantity,
        efficiency: Quantity,
        power_factor: float,
        R_to_X_ratio: float = 0.42
    ) -> None:
        self.U_nom = nominal_voltage
        self.I_nom = nominal_current
        self.I_start = locked_rotor_current
        self.P_m = P_m
        self.e = efficiency
        self.cos_phi = power_factor
        self.R_to_X_ratio = R_to_X_ratio

    @property
    def Z1(self) -> Quantity:
        P_m = self.P_m.to('W').magnitude
        e = self.e.to('frac').magnitude
        I_nom = self.I_nom.to('A').magnitude
        I_start = self.I_start.to('A').magnitude
        U_nom = self.U_nom.to('V').magnitude
        S_nom = (P_m / e) / self.cos_phi
        Z_mag = (I_nom / I_start) * U_nom ** 2 / S_nom
        X = Z_mag / math.sqrt(1 + self.R_to_X_ratio ** 2)
        R = self.R_to_X_ratio * X
        Z_ph = math.atan2(X, R)
        Z = cmath.rect(Z_mag, Z_ph)
        return Quantity(Z, 'ohm')


__all__ = [
    "PowerGrid",
    "Transformer",
    "Generator",
    "SynchronousMotor",
    "Cable",
    "InductionMotor"
]
