import numpy as np
import numpy.typing as npt
from .quantity import Quantity


class PolarRepresentation:

    @staticmethod
    def from_complex_quantity(qty: Quantity, decimals: int = 4) -> str:
        """
        Returns Pint Quantity with complex number as string in polar form.
        """
        if isinstance(qty.magnitude, float):
            return (
                f"{np.abs(qty.magnitude):.{decimals}f} {qty.units:~} "
                f"< {np.angle(qty.magnitude, deg=True):.2f}°"
            )
        if isinstance(qty.magnitude, npt.ArrayLike):
            vector_str = [
                f"{np.abs(q.magnitude):.{decimals}f} {q.units:~} "
                f"< {np.angle(q.magnitude, deg=True):.2f}°"
                for q in qty.flatten()
            ]
            if len(vector_str) == 1:
                return vector_str[0]
            return f"[{vector_str[0]}, {vector_str[1]}, {vector_str[2]}]"
        raise ValueError

    @staticmethod
    def from_complex_number(number: complex | npt.ArrayLike, decimals: int = 4) -> str:
        """
        Returns complex number as string in polar form.
        """
        if isinstance(number, npt.ArrayLike):
            number = number[0]
        return f"{np.abs(number):.{decimals}f} < {np.angle(number, deg=True):.2f}°"

    @staticmethod
    def from_complex_vector(vector: np.ndarray, decimals: int = 4) -> str:
        """
        Returns 3phase vector (numpy 1-column array) of complex numbers as
        string in polar form.
        """
        if len(vector.shape) == 1:
            vector = vector[:, np.newaxis]
        vector_str = [(
                f"{np.abs(vector[i, 0]):.{decimals}f} "
                f"< {np.angle(vector[i, 0], deg=True):.2f}°"
            ) for i in range(3)
        ]
        return f"[{vector_str[0]}, {vector_str[1]}, {vector_str[2]}]"


def complex_from_polar(
    magn: float,
    theta: float,
    theta_units: str = "deg"
) -> complex:
    """
    Creates a complex number from its polar representation.
    """
    if theta_units == "deg":
        theta = np.deg2rad(theta)
    c = magn * np.exp(theta * 1j)
    return c


def complex_quantity_to_polar_string(qty: Quantity, decimals: int = 4) -> str:
    return PolarRepresentation.from_complex_quantity(qty, decimals)

def complex_number_to_polar_string(number: complex, decimals: int = 4) -> str:
    return PolarRepresentation.from_complex_number(number, decimals)

def complex_vector_to_string(vector: np.ndarray, decimals: int = 4) -> str:
    return PolarRepresentation.from_complex_vector(vector, decimals)


__all__ = [
    "PolarRepresentation",
    "complex_quantity_to_polar_string",
    "complex_number_to_polar_string",
    "complex_vector_to_string",
    "complex_from_polar"
]
