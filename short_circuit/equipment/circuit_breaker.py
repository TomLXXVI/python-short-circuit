from typing import Optional
from dataclasses import dataclass, field
from short_circuit import Quantity


@dataclass
class CircuitBreaker:
    """
    Represents a circuit breaker.

    Parameters
    ----------
    U_nom:
        Nominal voltage class of the circuit breaker.
    I_nom:
        Rated continuous current, i.e. the maximum RMS current that the breaker
        can carry continuously while it is in the closed position without
        overheating.
    U_max:
        Rated maximum voltage, i.e. the highest RMS line-to-line voltage for
        which the circuit breaker is designed. The breaker should be used in
        systems with an operating voltage less than or equal to this rating.
    Isc_nom:
        Rated symmetrical interrupting capability or rated symmetrical
        short-circuit current at rated maximum voltage, i.e. the maximum RMS
        symmetrical current that the breaker can safely interrupt at rated
        maximum voltage. The product `sqrt(3) * Isc_nom * U_max` is the maximum
        apparent power that the circuit breaker is capable of interrupting.
    K:
        Voltage range factor, i.e. the ratio of rated maximum voltage `U_max` to
        the lower limit `U_min` of the range of operating voltage.

    Other Attributes
    ----------------
    U_min:
        Minimum allowed line-to-line voltage for interrupting.
    Isc_max:
        Maximum symmetrical interrupting capability at minimum allowed
        line-to-line voltage `U_min`.
    """
    U_nom: Quantity
    I_nom: Quantity
    U_max: Quantity
    Isc_nom: Quantity
    K: float
    Isc_max: Quantity = field(init=False)
    U_min: Quantity = field(init=False)

    def __post_init__(self):
        self.U_min = self.U_max / self.K
        self.Isc_max = self.Isc_nom * self.K

    def get_interrupting_capability(self, U: Quantity) -> Optional[Quantity]:
        """
        Returns the symmetrical interrupting capability of the circuit breaker
        at the given operating voltage. This current `Isc` follows from
        `sqrt(3) * Isc * U = sqrt(3) * Isc_nom * U_max` where
        `sqrt(3) * Isc_nom * U_max` is the maximum apparent power that the
        circuit breaker is capable of interrupting.

        Raises
        ------
        ValueError
            When operating voltage `U` is outside the range `U_min`..`U_max`.
        """
        if self.U_min <= U <= self.U_max:
            return self.Isc_nom * self.U_max / U
        else:
            raise ValueError(
                f"voltage {U.to('kV'):~P.0f} outside operating range "
                f"{self.U_min.to('kV'):~P.0f}..{self.U_max.to('kV'):~P.0f}"
            )

    def check(self, I3ph: Quantity, U: Quantity) -> bool:
        """
        Checks whether the calculated maximum three-phase symmetrical fault
        current `I3ph` is not greater than 80% of the interrupting capability
        of the circuit breaker at the given operating voltage `U`.
        """
        Isc = self.get_interrupting_capability(U)
        if abs(I3ph) <= 0.8 * Isc:
            return True
        return False


__all__ = ["CircuitBreaker"]


if __name__ == '__main__':
    import numpy as np
    from short_circuit.charts import LineChart

    Q_ = Quantity

    circuit_breaker = CircuitBreaker(
        U_nom=Q_(69, 'kV'),
        I_nom=Q_(1_200, 'A'),
        U_max=Q_(72.5, 'kV'),
        K=1.21,
        Isc_nom=Q_(19_000, 'A')
    )
    print(
        f"operating voltage range: "
        f"{circuit_breaker.U_min:~P.0f} - {circuit_breaker.U_max:~P.1f}"
    )
    print(
        f"maximum symmetrical interrupting capability @ "
        f"{circuit_breaker.U_min.to('kV'):~P.1f}: "
        f"{circuit_breaker.Isc_max:~P.0f}"
    )

    U_min = circuit_breaker.U_min.to('kV').m
    U_max = circuit_breaker.U_max.to('kV').m
    U_rng = Q_(np.linspace(U_min, U_max), 'kV')
    Isc_rng = Quantity.from_list([circuit_breaker.get_interrupting_capability(U) for U in U_rng])

    c = LineChart()
    c.add_xy_data(
        label="",
        x1_values=U_rng.m,
        y1_values=Isc_rng.to('A').m
    )
    c.x1.add_title("operating voltage, kV")
    c.y1.add_title("interrupting capability, A")
    c.show()
