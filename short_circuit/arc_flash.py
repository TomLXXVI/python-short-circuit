"""
Arc-Flash calculation according to IEEE 1584 (2018)
"""
from typing import List, Type, Dict, Optional
from abc import ABC, abstractmethod
from enum import Enum
import math
from short_circuit import Quantity, unit_registry

u = unit_registry


class EnclosureType(Enum):
    SHALLOW = 'shallow'
    TYPICAL = 'typical'


class ElectrodeConfiguration(ABC):
    """
    Class that holds the equation coefficients that depend on the electrode 
    configuration, i.e. the arrangement of the electrodes used in the testing 
    performed for the IEEE 1584 (2018) model development.
    """
    I_arc: Dict[int, List[float]]
    E: Dict[int, List[float]]
    varCF: List[float]
    enclosure_constants: Optional[List[float]] = None
    enclosure_coefficients: Optional[Dict[EnclosureType, List[float]]]


class VCB(ElectrodeConfiguration):
    """
    Vertical conductors/electrodes inside a metal box/enclosure.
    """
    I_arc = {
        600: [
            -0.04287, 1.035, -0.083, 0, 0, -4.783E-09, 
            1.962E-06, -0.000229, 0.003141, 1.092
        ],
        2700: [
            0.0065, 1.001, -0.024, -1.557E-12, 4.556E-10, -4.186E-08, 
            8.346E-07, 5.482E-05, -0.003191, 0.9729
        ],
        14300: [
            0.005795, 1.015, -0.011, -1.557E-12, 4.556E-10, -4.186E-08, 
            8.346E-07, 5.482E-05, -0.003191, 0.9729
        ]
    }

    E = {
        600: [
            0.753364, 0.566, 1.752636, 0, 0, -4.783E-09, 0.000001962, 
            -0.000229, 0.003141, 1.092, 0, -1.598, 0.957
        ],
        2700: [
            2.40021, 0.165, 0.354202, -1.557E-12, 4.556E-10, -4.186E-08, 
            8.346E-07, 5.482E-05, -0.003191, 0.9729, 0, -1.569, 0.9778
        ],
        14300: [
            3.825917, 0.11, -0.999749, -1.557E-12, 4.556E-10, -4.186E-08, 
            8.346E-07, 5.482E-05, -0.003191, 0.9729, 0, -1.568, 0.99
        ]
    }

    varCF = [
        0, -0.0000014269, 0.000083137, -0.0019382, 
        0.022366, -0.12645, 0.30226
    ]

    enclosure_constants = [4.0, 20.0]

    enclosure_coefficients = {
        EnclosureType.TYPICAL: [-0.000302, 0.03441, 0.4325],
        EnclosureType.SHALLOW: [0.002222, -0.02556, 0.6222],
    }


class VCBB(ElectrodeConfiguration):
    """
    Vertical conductors/electrodes terminated in an insulating barrier inside a 
    metal box/enclosure.
    """
    I_arc = {
        600: [
            -0.017432, 0.98, -0.05, 0, 0, -5.767E-09, 
            2.524E-06, -0.00034, 0.01187, 1.013
        ],
        2700: [
            0.002823, 0.995, -0.0125, 0, -9.204E-11, 
            2.901E-08, -3.262E-06, 0.0001569, -0.004003, 0.9825
        ],
        14300: [
            0.014827, 1.01, -0.01, 0, -9.204E-11, 2.901E-08, 
            -3.262E-06, 0.0001569, -0.004003, 0.9825
        ]
    }

    E = {
        600: [
            3.068459, 0.26, -0.098107, 0, 0, -5.767E-09, 0.000002524, 
            -0.00034, 0.01187, 1.013, -0.06, -1.809, 1.19
        ],
        2700: [
            3.870592, 0.185, -0.736618, 0, -9.204E-11, 2.901E-08, 
            -3.262E-06, 0.0001569, -0.004003, 0.9825, 0, -1.742, 1.09
        ],
        14300: [
            3.644309, 0.215, -0.585522, 0, -9.204E-11, 2.901E-08, 
            -3.262E-06, 0.0001569, -0.004003, 0.9825, 0, -1.677, 1.06
        ]
    }

    varCF = [
        1.138e-06, -6.0287e-05, 0.0012758, -0.013778, 
        0.080217, -0.24066, 0.33524
    ]

    enclosure_constants = [10.0, 24.0]

    enclosure_coefficients = {
        EnclosureType.TYPICAL: [-0.0002976, 0.032, 0.479],
        EnclosureType.SHALLOW: [-0.002778, 0.1194, -0.2778],
    }


class HCB(ElectrodeConfiguration):
    """
    Horizontal conductors/electrodes inside a metal box/enclosure.
    """
    I_arc = {
        600: [
            0.054922, 0.988, -0.11, 0, 0, -5.382E-09, 
            2.316E-06, -0.000302, 0.0091, 0.9725
        ],
        2700: [
            0.001011, 1.003, -0.0249, 0, 0, 4.859E-10, 
            -1.814E-07, -9.128E-06, -0.0007, 0.9881
        ],
        14300: [
            0.008693, 0.999, -0.02, 0, -5.043E-11, 2.233E-08, 
            -3.046E-06, 0.000116, -0.001145, 0.9839
        ],
    }

    E = {
        600: [
            4.073745, 0.344, -0.370259, 0, 0, -5.382E-09, 
            0.000002316, -0.000302, 0.0091, 0.9725, 0, -2.03, 1.036
        ],
        2700: [
            3.486391, 0.177, -0.193101, 0, 0, 4.859E-10, -1.814E-07, 
            -9.128E-06, -0.0007, 0.9881, 0.027, -1.723, 1.055
        ],
        14300: [
            3.044516, 0.125, 0.245106, 0, -5.043E-11, 2.233E-08, 
            -3.046E-06, 0.000116, -0.001145, 0.9839, 0, -1.655, 1.084
        ]
    }

    varCF = [
        0.0, -3.097e-06, 0.00016405, -0.0033609, 
        0.033308, -0.16182, 0.34627
    ]

    enclosure_constants = [10.0, 22.0]

    enclosure_coefficients = {
        EnclosureType.TYPICAL: [-0.0001923, 0.01935, 0.6899],
        EnclosureType.SHALLOW: [-0.0005556, 0.03722, 0.4778],
    }


class VOA(ElectrodeConfiguration):
    """
    Vertical conductors/electrodes in open air.
    """
    I_arc = {
        600: [
            0.043785, 1.04, -0.18, 0, 0, -4.783E-09, 
            1.962E-06, -0.000229, 0.003141, 1.092
        ],
        2700: [
            -0.02395, 1.006, -0.0188, -1.557E-12, 4.556E-10, 
            -4.186E-08, 8.346E-07, 5.482E-05, -0.003191, 0.9729
        ],
        14300: [
            0.005371, 1.0102, -0.029, -1.557E-12, 4.556E-10, 
            -4.186E-08, 8.346E-07, 5.482E-05, -0.003191, 0.9729
        ],
    }

    E = {
        600: [
            0.679294, 0.746, 1.222636, 0, 0, -4.783E-09, 0.000001962, 
            -0.000229, 0.003141, 1.092, 0, -1.598, 0.997
        ],
        2700: [
            3.880724, 0.105, -1.906033, -1.557E-12, 4.556E-10, -4.186E-08, 
            8.346E-07, 5.482E-05, -0.003191, 0.9729, 0, -1.515, 1.115
        ],
        14300: [
            3.405454, 0.12, -0.93245, -1.557E-12, 4.556E-10, -4.186E-08, 
            8.346E-07, 5.482E-05, -0.003191, 0.9729, 0, -1.534, 0.979
        ],
    }

    varCF = [
        9.5606E-07, -5.1543E-05, 0.0011161, 
        -0.01242, 0.075125, -0.23584, 0.33696
    ]


class HOA(ElectrodeConfiguration):
    """
    Horizontal conductors/electrodes in open air.
    """
    I_arc = {
        600: [
            0.111147, 1.008, -0.24, 0, 0, -3.895E-09, 
            1.641E-06, -0.000197, 0.002615, 1.1
        ],
        2700: [
            0.000435, 1.006, -0.038, 0, 0, 7.859E-10, 
            -1.914E-07, -9.128E-06, -0.0007, 0.9981
        ],
        14300: [
            0.000904, 0.999, -0.02, 0, 0, 7.859E-10, 
            -1.914E-07, -9.128E-06, -0.0007, 0.9981
        ],
    }

    E = {
        600: [
            3.470417, 0.465, -0.261863, 0, 0, -3.895E-09, 
            0.000001641, -0.000197, 0.002615, 1.1, 0, 
            -1.99, 1.04
        ],
        2700: [
            3.616266, 0.149, -0.761561, 0, 0, 7.859E-10, -1.914E-07, 
            -9.128E-06, -0.0007, 0.9981, 0, -1.639, 1.078
        ],
        14300: [
            2.04049, 0.177, 1.005092, 0, 0, 7.859E-10, -1.914E-07, 
            -9.128E-06, -0.0007, 0.9981, -0.05, -1.633, 1.151
        ]
    }

    varCF = [
        0.0, -3.1555e-06, 0.0001682, -0.0034607, 
        0.034124, -0.1599, 0.34629
    ]


class Enclosure:

    def __init__(
        self,
        width: Quantity,
        height: Quantity,
        depth: Optional[Quantity],
        V_oc: Quantity,
        electrode_configuration: Type[ElectrodeConfiguration]
    ):
        self._width = width
        self._height = height
        self._depth = depth if depth is not None else Quantity(60, 'cm')
        self._V_oc = V_oc
        self._electrode_configuration = electrode_configuration
        self._enclosure_type = self._get_enclosure_type()

    def _get_enclosure_type(self) -> EnclosureType:
        condition_1 = self._V_oc < 600 * u.V
        condition_2 = self._width < 508 * u.mm
        condition_3 = self._height < 508 * u.mm
        condition_4 = self._depth <= 203.2 * u.mm
        if condition_1 and condition_2 and condition_3 and condition_4:
            return EnclosureType.SHALLOW
        else:
            return EnclosureType.TYPICAL

    def _calculate_width_1(self, width: float) -> float:
        V_oc = self._V_oc.to('kV').magnitude
        A = self._electrode_configuration.enclosure_constants[0]
        B = self._electrode_configuration.enclosure_constants[1]
        width_1 = (660.4 + (width - 660.4) * (V_oc + A) / B) / 25.4
        return width_1

    def _calculate_height_1(self, height: float) -> float:
        V_oc = self._V_oc.to('kV').magnitude
        A = self._electrode_configuration.enclosure_constants[0]
        B = self._electrode_configuration.enclosure_constants[1]
        height_1 = (660.4 + (height - 660.4) * (V_oc + A) / B) / 25.4
        return height_1

    def _get_width_1(self) -> float | None:
        width = self._width.to('mm').magnitude
        if width < 508.0:
            if self._enclosure_type == EnclosureType.TYPICAL:
                return 20.0
            else:
                return 0.03937 * width
        if 508.0 <= width <= 660.4:
            return 0.03937 * width
        if 660.4 < width <= 1244.6:
            return self._calculate_width_1(width)
        if width > 1244.6:
            return self._calculate_width_1(width=1244.6)

    def _get_height_1(self) -> float | None:
        height = self._height.to('mm').magnitude
        if self._electrode_configuration is VCB:
            if height < 508.0:
                if self._enclosure_type == EnclosureType.TYPICAL:
                    return 20.0
                else:
                    return 0.03937 * height
            if 508.0 <= height <= 660.4:
                return 0.03937 * height
            if 660.4 < height <= 1244.6:
                return 0.03937 * height
            if height > 1244.6:
                return 49
        else:
            if height < 508.0:
                if self._enclosure_type == EnclosureType.TYPICAL:
                    return 20.0
                else:
                    return 0.03937 * height
            if 508.0 <= height <= 660.4:
                return 0.03937 * height
            if 660.4 < height <= 1244.6:
                return self._calculate_height_1(height)
            if height > 1244.6:
                return self._calculate_height_1(height=1244.6)

    def _get_equivalent_enclosure_size(self):
        width_1 = self._get_width_1()
        height_1 = self._get_height_1()
        EES = (width_1 + height_1) / 2.0
        return EES

    def get_CF_enclosure(self) -> float | None:
        """
        Get enclosure size correction factor.
        """
        EES = self._get_equivalent_enclosure_size()
        if self._enclosure_type == EnclosureType.TYPICAL:
            b = self._electrode_configuration.enclosure_coefficients[EnclosureType.TYPICAL]
            CF = b[0] * EES ** 2 + b[1] * EES + b[2]
            return CF
        if self._enclosure_type == EnclosureType.SHALLOW:
            b = self._electrode_configuration.enclosure_coefficients[EnclosureType.SHALLOW]
            CF = 1.0 / (b[0] * EES ** 2 + b[1] * EES + b[2])
            return CF


class ArcFlashModel(ABC):
    """
    Base class that holds the equations for calculating (predicting) the arcing 
    current, the incident thermal energy and the arc-flash boundary.
    """
    lower_limit = None
    upper_limit = None

    def __init__(
        self,
        V_oc: Quantity,
        I_bf: Quantity,
        electrode_configuration: Type[ElectrodeConfiguration],
        gap: Quantity,
        working_distance: Quantity,
        CF_enclosure: float = 1.0
    ) -> None:
        """
        Initialize `ArcFlashModel` object.

        Parameters
        ----------
        V_oc :
            Three phase system open (unloaded) circuit voltage 
            (line-to-line, RMS).
        I_bf :
            Bolted three-phase fault current (RMS).
        electrode_configuration :
            Child class of `ElectrodeConfiguration` class: VCB, VCBB, HCB, VOA, 
            or HOA.
        gap :
            Gap distance between electrodes (see IEEE 1584, table 8).
        working_distance :
            Distance between electrodes and calorimeters = working distance 
            (see IEEE 1584, table 10).
        CF_enclosure : optional
            Correction factor for enclosure size (CF = 1 for VOA and HOA 
            configurations).
        """
        if self.lower_limit < V_oc <= self.upper_limit:
            self._V_oc = V_oc
        else:
            raise ValueError("open circuit voltage ´V_oc´ outside of boundaries")
        self._I_bf = I_bf
        self._electrode_configuration = electrode_configuration
        self._G = gap
        self._D = working_distance
        self._CF_enclosure = CF_enclosure
        self._T: Optional[Quantity] = None

    def set_arc_duration(self, T: Quantity = Quantity(2.0, 's')):
        """
        Arc duration (= total protective device clearing time); depends on the 
        arcing current. Default is 2 s (under the assumption that clearing 
        time > 2 s, this is the time it takes for a person to move away from the
        location of the arc flash).
        """
        self._T = T

    @staticmethod
    def _intermediate_arcing_current(
        I_bf: Quantity, 
        G: Quantity, 
        k: List[float]
    ) -> float:
        I_bf = I_bf.to('kA').magnitude
        G = G.to('mm').magnitude
        f1 = math.pow(10, k[0] + k[1] * math.log10(I_bf) + k[2] * math.log10(G))
        f2 = k[3] * (I_bf ** 6)
        f2 += k[4] * (I_bf ** 5)
        f2 += k[5] * (I_bf ** 4)
        f2 += k[6] * (I_bf ** 3)
        f2 += k[7] * (I_bf ** 2)
        f2 += k[8] * I_bf
        f2 += k[9]
        I_arc = f1 * f2
        return I_arc

    @staticmethod
    def _intermediate_incident_energy(
        T: Quantity,
        G: Quantity,
        I_bf: Quantity,
        D: Quantity,
        I_arc_im: float,  # intermediate arc current
        CF: float,
        k: List[float],
        I_arc: Optional[Quantity] = None  # final arc current
    ) -> float:
        T = T.to('ms').magnitude
        G = G.to('mm').magnitude
        I_bf = I_bf.to('kA').magnitude
        D = D.to('mm').magnitude
        if I_arc is None:
            I_arc = I_arc_im
        else:
            I_arc = I_arc.to('kA').magnitude
        f1 = 12.552 / 50 * T
        e1 = k[0]
        e2 = k[1] * math.log10(G)
        e3_n = k[2] * I_arc_im
        e3_d = k[3] * (I_bf ** 7)
        e3_d += k[4] * (I_bf ** 6)
        e3_d += k[5] * (I_bf ** 5)
        e3_d += k[6] * (I_bf ** 4)
        e3_d += k[7] * (I_bf ** 3)
        e3_d += k[8] * (I_bf ** 2)
        e3_d += k[9] * I_bf
        e4 = k[10] * math.log10(I_bf)
        e5 = k[11] * math.log10(D)
        e6 = k[12] * math.log10(I_arc)
        e7 = math.log10(1 / CF)
        e = e1 + e2 + e3_n / e3_d + e4 + e5 + e6 + e7
        f2 = math.pow(10, e)
        E = f1 * f2
        return E

    @staticmethod
    def _intermediate_arc_flash_boundary(
        T: Quantity,
        G: Quantity,
        I_bf: Quantity,
        I_arc_im: float,  # intermediate arc current
        CF: float,
        k: List[float],
        I_arc: Optional[Quantity] = None  # final arc current
    ) -> float:
        T = T.to('ms').magnitude
        G = G.to('mm').magnitude
        I_bf = I_bf.to('kA').magnitude
        if I_arc is None:
            I_arc = I_arc_im
        else:
            I_arc = I_arc.to('kA').magnitude
        e1 = k[0]
        e2 = k[1] * math.log10(G)
        e3_n = k[2] * I_arc_im
        e3_d = k[3] * (I_bf ** 7)
        e3_d += k[4] * (I_bf ** 6)
        e3_d += k[5] * (I_bf ** 5)
        e3_d += k[6] * (I_bf ** 4)
        e3_d += k[7] * (I_bf ** 3)
        e3_d += k[8] * (I_bf ** 2)
        e3_d += k[9] * I_bf
        e4 = k[10] * math.log10(I_bf)
        e5 = k[12] * math.log10(I_arc)
        e6 = math.log10(1 / CF)
        e7 = -math.log10(20 / T)
        e8 = -k[11]
        e = (e1 + e2 + e3_n / e3_d + e4 + e5 + e6 + e7) / e8
        AFB = math.pow(10, e)
        return AFB

    @abstractmethod
    def arcing_current(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        """
        Get average or reduced arcing current.

        Parameters
        ----------
        CF_reduced : optional
            Correction factor for calculating the reduced arcing current: see 
            method `get_CF_reduced()`. Default value is 1.0 (i.e. without 
            correction); in that case the average arcing current is returned.
        """
        ...

    @abstractmethod
    def incident_energy(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        """
        Get average or reduced incident energy at given working distance.

        Parameters
        ----------
        CF_reduced : optional
            Correction factor for calculating the reduced arcing current: see 
            method `get_CF_reduced()`. Default value is 1.0 (i.e. without 
            correction); in that case the average arcing current is returned.
        """
        ...

    @abstractmethod
    def arc_flash_boundary(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        """
        Get average or reduced arc flash boundary, i.e. distance from arc source
        where incident energy is 5.0 J/cm², or 1.2 cal/cm², which may cause a 
        2nd degree burn to bare skin (note: 4 cal/cm² may ignite a cotton shirt 
        and 8 cal/cm² causes 3rd degree burn to bare skin).

        Parameters
        ----------
        CF_reduced : optional
            Correction factor for calculating the reduced arcing current: 
            see method `get_CF_reduced()`. Default value is 1.0 (i.e. without 
            correction); in that case the average arcing current is returned.
        """
        ...

    @abstractmethod
    def get_CF_reduced(self) -> float:
        """
        Get correction factor for calculating the reduced arcing current.
        """
        ...


class HighVoltageArcFlashModel(ArcFlashModel):
    """
    Arc-flash model applicable for three-phase system voltages between 600 V and
    15 kV included.
    """
    lower_limit = 600 * u.V
    upper_limit = 15.0 * u.kV

    def arcing_current(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        I_arc_600 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[600]
        )
        I_arc_2700 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[2700]
        )
        I_arc_14300 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[14300]
        )

        I_arc_600 = CF_reduced * I_arc_600
        I_arc_2700 = CF_reduced * I_arc_2700
        I_arc_14300 = CF_reduced * I_arc_14300

        V_oc = self._V_oc.to('kV').magnitude

        I_arc_1 = (I_arc_2700 - I_arc_600) / 2.1 * (V_oc - 2.7) + I_arc_600
        I_arc_2 = (I_arc_14300 - I_arc_2700) / 11.6 * (V_oc - 14.3) + I_arc_14300
        I_arc_3 = (I_arc_1 * (2.7 - V_oc) + I_arc_2 * (V_oc - 0.6)) / 2.1

        if 0.6 < V_oc <= 2.7:
            I_arc = I_arc_3
        else:
            I_arc = I_arc_2
        return Quantity(I_arc, 'kA')

    def incident_energy(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        I_arc_600 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[600]
        )
        I_arc_2700 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[2700]
        )
        I_arc_14300 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[14300]
        )

        I_arc_600 = CF_reduced * I_arc_600
        I_arc_2700 = CF_reduced * I_arc_2700
        I_arc_14300 = CF_reduced * I_arc_14300

        E_600 = self._intermediate_incident_energy(
            self._T, self._G, self._I_bf, self._D, I_arc_600,
            self._CF_enclosure, self._electrode_configuration.E[600]
        )
        E_2700 = self._intermediate_incident_energy(
            self._T, self._G, self._I_bf, self._D, I_arc_2700,
            self._CF_enclosure, self._electrode_configuration.E[2700]
        )
        E_14300 = self._intermediate_incident_energy(
            self._T, self._G, self._I_bf, self._D, I_arc_14300,
            self._CF_enclosure, self._electrode_configuration.E[14300]
        )

        V_oc = self._V_oc.to('kV').magnitude
        E_1 = (E_2700 - E_600) / 2.1 * (V_oc - 2.7) + E_2700
        E_2 = (E_14300 - E_2700) / 11.6 * (V_oc - 14.3) + E_14300
        E_3 = (E_1 * (2.7 - V_oc) + E_2 * (V_oc - 0.6)) / 2.1
        if 0.6 < V_oc <= 2.7:
            E = E_3
        else:
            E = E_2
        return Quantity(E, 'J / cm ** 2')
    
    def arc_flash_boundary(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        I_arc_600 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[600]
        )
        I_arc_2700 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[2700]
        )
        I_arc_14300 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[14300]
        )

        I_arc_600 = CF_reduced * I_arc_600
        I_arc_2700 = CF_reduced * I_arc_2700
        I_arc_14300 = CF_reduced * I_arc_14300

        AFB_600 = self._intermediate_arc_flash_boundary(
            self._T, self._G, self._I_bf, I_arc_600, 
            self._CF_enclosure, self._electrode_configuration.E[600]
        )
        AFB_2700 = self._intermediate_arc_flash_boundary(
            self._T, self._G, self._I_bf, I_arc_2700, 
            self._CF_enclosure, self._electrode_configuration.E[2700]
        )
        AFB_14300 = self._intermediate_arc_flash_boundary(
            self._T, self._G, self._I_bf, I_arc_14300, 
            self._CF_enclosure, self._electrode_configuration.E[14300]
        )

        V_oc = self._V_oc.to('kV').magnitude
        AFB_1 = (AFB_2700 - AFB_600) / 2.1 * (V_oc - 2.7) + AFB_2700
        AFB_2 = (AFB_14300 - AFB_2700) / 11.6 * (V_oc - 14.3) + AFB_14300
        AFB_3 = (AFB_1 * (2.7 - V_oc) + AFB_2 * (V_oc - 0.6)) / 2.1
        if 0.6 < V_oc <= 2.7:
            AFB = AFB_3
        else:
            AFB = AFB_2
        return Quantity(AFB, 'mm')

    def get_CF_reduced(self) -> float:
        V_oc = self._V_oc.to('kV').magnitude
        k = self._electrode_configuration.varCF
        varCF = k[0] * (V_oc ** 6)
        varCF += k[1] * (V_oc ** 5)
        varCF += k[2] * (V_oc ** 4)
        varCF += k[3] * (V_oc ** 3)
        varCF += k[4] * (V_oc ** 2)
        varCF += k[5] * V_oc
        varCF += k[6]
        CF_reduced = 1 - 0.5 * varCF
        return CF_reduced


class LowVoltageArcFlashModel(ArcFlashModel):
    """
    Arc-flash model applicable for three-phase system voltages between 208 V 
    and 600 V included.
    """
    lower_limit = 208 * u.V
    upper_limit = 600 * u.V

    def arcing_current(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        I_arc_600 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[600]
        )
        V_oc = self._V_oc.to('kV').magnitude
        I_bf = self._I_bf.to('kA').magnitude
        f1 = (0.6 / V_oc) ** 2
        f2 = (1.0 / I_arc_600 ** 2) - (0.6 ** 2 - V_oc ** 2) / (0.6 ** 2 * I_bf ** 2)
        I_arc = 1.0 / math.sqrt(f1 * f2)
        I_arc = CF_reduced * I_arc
        return Quantity(I_arc, 'kA')

    def incident_energy(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        I_arc_600 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[600]
        )
        I_arc = self.arcing_current(CF_reduced)
        E_600 = self._intermediate_incident_energy(
            self._T, self._G, self._I_bf, self._D, I_arc_600, 
            self._CF_enclosure, self._electrode_configuration.E[600], 
            I_arc
        )
        E = E_600
        return Quantity(E, 'J / cm ** 2')

    def arc_flash_boundary(self, CF_reduced: Optional[float] = 1.0) -> Quantity:
        I_arc_600 = self._intermediate_arcing_current(
            self._I_bf, self._G, 
            self._electrode_configuration.I_arc[600]
        )
        I_arc = self.arcing_current(CF_reduced)
        AFB_600 = self._intermediate_arc_flash_boundary(
            self._T, self._G, self._I_bf, I_arc_600, 
            self._CF_enclosure, self._electrode_configuration.E[600], 
            I_arc
        )
        AFB = AFB_600
        return Quantity(AFB, 'mm')

    def get_CF_reduced(self) -> float:
        k = self._electrode_configuration.varCF
        V_oc = self._V_oc.to('kV').magnitude
        varCF = k[0] * (V_oc ** 6)
        varCF += k[1] * (V_oc ** 5)
        varCF += k[2] * (V_oc ** 4)
        varCF += k[3] * (V_oc ** 3)
        varCF += k[4] * (V_oc ** 2)
        varCF += k[5] * V_oc
        varCF += k[6]
        CF_reduced = 1 - 0.5 * varCF
        return CF_reduced
