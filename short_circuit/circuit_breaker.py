from typing import Optional
from dataclasses import dataclass, field
from short_circuit import Quantity


@dataclass
class CircuitBreaker:
    U_nom: Quantity                          # nominal voltage class
    I_nom: Quantity                          # rated continuous current
    U_max: Quantity                          # maximum allowed operating voltage
    K: Quantity                              # voltage range factor (ratio of maximum to minimum allowed operating voltage)
    I_sc_nom: Quantity                       # rated interrupting capability at maximum operating voltage
    I_sc_max: Quantity = field(init=False)   # maximum interrupting capability at minimum allowed operating voltage
    U_min: Quantity = field(init=False)      # minimum allowed interrupting voltage

    def __post_init__(self):
        self.U_min = self.U_max / self.K
        self.I_sc_max = self.I_sc_nom * self.K

    def get_interrupting_capability(self, U: Quantity) -> Optional[Quantity]:
        """Get symmetrical interrupting capability at given operating voltage."""
        if self.U_min <= U <= self.U_max:
            return self.I_sc_nom * self.U_max / U
        else:
            raise ValueError(
                'operating voltage U outside boundaries of circuit breaker'
            )

    def check(self, I_k: Quantity, U: Quantity) -> bool:
        """Check if calculated short-circuit current `I_k` is equal or less than 
        80% of the interrupting capability of the circuit breaker at the given 
        operating voltage `U`.
        """
        I_sc = self.get_interrupting_capability(U)
        if abs(I_k) <= 0.8 * I_sc:
            return True
        return False
