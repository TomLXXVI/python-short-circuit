from typing import Union
import math
from . import Quantity


class PerUnitSystem:

    def __init__(self, S_base: Quantity, U_base: Quantity):
        """Creates a `PerUnitSystem` object.
        
        Parameters
        ----------
        S_base:
            Base power of the per-unit system.
        U_base:
            Base voltage of the per-unit system (line-to-line voltage).
        """
        self.S_base = S_base
        self.U_base = U_base
        self.I_base: Quantity = S_base / (math.sqrt(3) * U_base)
        self.Z_base: Quantity = U_base ** 2 / S_base

    def get_per_unit_impedance(self, Z_act: Quantity) -> Union[float, complex]:
        """Returns the per-unit value of the actual impedance `Z_act`."""
        Z_pu: Quantity = Z_act / self.Z_base
        return Z_pu.to('ohm / ohm').magnitude

    def get_per_unit_current(self, I_act: Quantity) -> Union[float, complex]:
        """Returns the per-unit value of the actual current `I_act`."""
        I_pu: Quantity = I_act / self.I_base
        return I_pu.to('A / A').magnitude

    def get_per_unit_voltage(self, U_act: Quantity) -> Union[float, complex]:
        """Returns the per-unit value of the actual voltage `U_act`."""
        U_pu: Quantity = U_act / self.U_base
        return U_pu.to('V / V').magnitude

    def get_per_unit_power(self, S_act: Quantity) -> Union[float, complex]:
        """Returns the per-unit value of the actual power `S_act`."""
        S_pu: Quantity = S_act / self.S_base
        return S_pu.to('VA / VA').magnitude


def convert_per_unit_impedance(
    Z_pu_1: Union[float, complex],
    per_unit_system_1: PerUnitSystem,
    per_unit_system_2: PerUnitSystem
) -> Union[float, complex]:
    """Converts per-unit impedance from per-unit system 1 to another per-unit 
    system 2

    Parameters
    ----------
    Z_pu_1:
        Per-unit impedance according to per unit system 1.
    per_unit_system_1:
        Per-unit system of given per-unit impedance `Z_pu_1`.
    per_unit_system_2:
        Per-unit system to which the per-unit impedance `Z_pu_1` is to be 
        converted.

    Returns
    -------
    Per-unit impedance according to per-unit system 2.
    """
    Z_pu_2 = Z_pu_1 * per_unit_system_1.Z_base / per_unit_system_2.Z_base
    return Z_pu_2.magnitude
