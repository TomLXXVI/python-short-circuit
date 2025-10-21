import numpy as np
from .quantity import Quantity


def complex_quantity_as_polar_string(qty: Quantity, decimals: int = 4):
    """Returns Pint Quantity with complex number as string in polar form."""
    return (
        f"{np.abs(qty.magnitude):.{decimals}f} {qty.units:~} "
        f"< {np.angle(qty.magnitude, deg=True):.2f}°"
    )


def complex_number_as_polar_string(number: complex, decimals: int = 4):
    """Returns complex number as string in polar form."""
    # noinspection PyTypeChecker
    return f"{np.abs(number):.{decimals}f} < {np.angle(number, deg=True):.2f}°"


def complex_vector_as_string(vector: np.array, decimals: int = 4):
    """
    Returns 3phase vector (numpy 1-column array) of complex numbers as string in
    polar form.
    """
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


__all__ = [
    "complex_quantity_as_polar_string",
    "complex_number_as_polar_string",
    "complex_vector_as_string",
    "complex_from_polar"
]
