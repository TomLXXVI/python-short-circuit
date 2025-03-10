import math
from abc import ABC, abstractmethod
from short_circuit import Quantity


class Gas(ABC):
    B: float = 0.0  # V / (kPa.cm)

    @staticmethod
    @abstractmethod
    def _calculate_k(P: float, d: float) -> float:
        ...

    def breakdown_voltage(self, d: Quantity, P: Quantity = Quantity(101.325, 'kPa')):
        P = P.to('kPa').magnitude
        d = d.to('cm').magnitude

        k = self._calculate_k(P, d)

        V_b = self.B * P * d / (math.log(P * d) + k)

        return Quantity(V_b, 'V')


class Air(Gas):
    B: float = 2737.5  # V / (kPa.cm)

    @staticmethod
    def _calculate_k(P: float, d: float) -> float:
        if 0.0133 <= P * d < 0.2:
            k = 2.0583 * math.pow(P * d, -0.1724)
        elif 0.2 <= P * d < 100.0:
            k = 3.5134 * math.pow(P * d, 0.0599)
        elif 100.0 <= P * d <= 1400.0:
            k = 4.6295
        else:
            raise ValueError('Product `P * d` lies outside valid range')
        return k


class Nitrogen(Gas):  # N2
    B: float = 2565.00  # V / (kPa.cm)

    @staticmethod
    def _calculate_k(P: float, d: float) -> float:
        if 0.0313 <= P * d < 3.0:
            k = 2.5819 * math.pow(P * d, -0.0514)
        elif 3.0 <= P * d < 100.0:
            k = 2.4043 * math.pow(P * d, 0.1030)
        elif 100.0 <= P * d <= 1400.0:
            k = 3.8636
        else:
            raise ValueError('Product `P * d` lies outside valid range')
        return k


class SF6(Gas):
    B: float = 2189.25

    @staticmethod
    def _calculate_k(P: float, d: float) -> float:
        if 0.3 <= P * d < 3.0:
            k = math.log(4.1227 * math.pow(P * d, -0.4331))
        elif 3.0 <= P * d < 1200.0:
            k = math.log(6.4541 * math.pow(P * d, -0.8374))
        else:
            raise ValueError('Product `P * d` lies outside valid range')
        return k
