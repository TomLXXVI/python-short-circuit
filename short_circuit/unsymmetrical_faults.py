from typing import List, Optional, Union
from abc import ABC, abstractmethod
import math
import cmath
import numpy as np
import numpy.typing as npt


from short_circuit.network import Network, REF_NODE_INDEX, Node, Branch


a = cmath.rect(1.0, math.radians(120.0))

A = np.array([
    [1.0, 1.0, 1.0],
    [1.0, a ** 2, a],
    [1.0, a, a ** 2]
])

A_inv = np.linalg.inv(A)


def transform_to_012(Q_abc: npt.ArrayLike) -> npt.NDArray:
    """Transforms a three-phase quantity `Q_abc` to its symmetrical components 
    `Q_012` (zero sequence, positive sequence, negative sequence).
    
    Parameters
    ----------
    Q_abc:
        Three-phase quantity represented by its individual phase components in
        an array-like structure, e.g. a list like `[a, b, c]` or a Numpy array
        like `np.array([a, b, c])`.
    
    Returns
    -------
    Q_012:
        Symmetrical components of the three-phase quantity ordered in a 1D 
        (flat) Numpy array. 
    """
    if not isinstance(Q_abc, np.ndarray):
        Q_abc = np.array(Q_abc)
    if len(Q_abc.shape) == 1:
        Q_abc = np.reshape(Q_abc, (1, len(Q_abc)))
    Q_abc = np.transpose(Q_abc)
    Q_012 = np.round(A_inv @ Q_abc, 9)
    return Q_012.flatten()


def transform_to_abc(Q_012: npt.ArrayLike) -> npt.NDArray:
    """Transforms the symmetrical components `Q_012` (zero sequence, positive 
    sequence, negative sequence) to its corresponding three-phase quantity 
    `Q_abc`.
    
    Parameters
    ----------
    Q_012:
        Symmetrical components of the three-phase quantity in an array-like 
        structure, e.g. a list like `[0, 1, 2]` or a Numpy array like 
        `np.array([0, 1, 2])`.
    
    Returns
    -------
    Q_abc:
        Three-phase quantity represented by its individual phase components in
        a 1D (flat) Numpy array.
    """
    if not isinstance(Q_012, np.ndarray):
        Q_012 = np.array(Q_012)
    if len(Q_012.shape) == 1:
        Q_012 = np.reshape(Q_012, (1, len(Q_012)))
    Q_012 = np.transpose(Q_012)
    Q_abc = np.round(A @ Q_012, 9)
    return Q_abc.flatten()


class UnSymmetricalFault(ABC):

    def __init__(
        self,
        network_012: List[Network],
        U_phase: Union[float, complex] = 1.0,
        c: float = 1.0
    ) -> None:
        """Creates a `UnSymmetricalFault` object.
        
        Parameters
        ----------
        network_012:
            List of sequence networks, ordered as follows: first zero sequence 
            (0), then positive sequence (1), and finally negative sequence (2).
        U_phase:
            Network voltage before the fault, i.e. the voltage between the 
            reference node of the network and each other network node, assuming 
            the network is unloaded before the fault.    
        c:
            Voltage factor.  
        """
        self._network_0 = network_012[0]
        self._network_1 = network_012[1]
        self._network_2 = network_012[2]
        self._U_phase: Union[float, complex] = c * U_phase
        self._faulted_node_ID: Optional[str] = None
        self._faulted_node_index: Optional[int] = None
        self._Z_f: Union[float, complex] = 0.0
        self._I_f_012: Optional[np.array] = None

    def set_faulted_node(
        self, 
        node_ID: str, 
        Z_fault: Union[float, complex] = 0.0
    ) -> None:
        """Sets the network node where the fault occurs.
        
        Parameters
        ----------
        node_ID:
            ID of the node in the network where the fault occurs.
        Z_fault:
            Impedance of the fault, i.e. the impedance between the node where
            the fault occurs and the reference node of the network.
        """
        self._faulted_node_ID = node_ID
        self._faulted_node_index = self._network_1.get_node_index(node_ID)
        self._Z_f = Z_fault

    @abstractmethod
    def get_fault_current_012(self) -> np.array:
        """Returns the symmetric components of the fault current (zero-sequence,
        positive sequence, and negative sequence component).
        """
        ...

    def get_fault_current_abc(self) -> np.array:
        """Returns the three-phase fault current components in the abc-reference
        frame.
        """
        I_f_012 = self.get_fault_current_012()
        I_f_abc = np.matmul(A, I_f_012)
        return I_f_abc

    def get_node_voltage_012(self, node: Node | int) -> np.array:
        """Returns the symmetric voltage components of the given network node."""
        k = self._faulted_node_index
        if isinstance(node, Node):
            i = node.index
        else:
            i = node
        Z_ik_0 = self._network_0.get_matrix_element(i, k)
        Z_ik_1 = self._network_1.get_matrix_element(i, k)
        Z_ik_2 = self._network_2.get_matrix_element(i, k)
        Z_ik_012 = np.diagflat([Z_ik_0, Z_ik_1, Z_ik_2])
        dU_012 = np.matmul(Z_ik_012, self._I_f_012)
        U_pre_012 = np.array([[0.0, self._U_phase, 0.0]]).transpose()
        U_012 = U_pre_012 - dU_012
        return U_012

    def get_node_voltage_abc(self, node: Node) -> np.array:
        """Returns the voltage components of the specified node in the 
        abc-reference frame.
        """
        U_012 = self.get_node_voltage_012(node)
        U_abc = np.matmul(A, U_012)
        return U_abc

    def get_branch_current_012(self, branch: Branch) -> np.array:
        """Returns the symmetric current components in the specified branch."""
        i = branch.start_node.index
        j = branch.end_node.index
        branch_1 = self._network_1.get_branch(i, j)
        branch_2 = self._network_2.get_branch(i, j)
        branch_0 = self._network_0.get_branch(i, j)
        Z_b_0 = branch_0.impedance
        Z_b_1 = branch_1.impedance
        Z_b_2 = branch_2.impedance
        Y_b_0 = 1 / Z_b_0
        Y_b_1 = 1 / Z_b_1
        Y_b_2 = 1 / Z_b_2
        Y_b_012 = np.diagflat([Y_b_0, Y_b_1, Y_b_2])
        if i == REF_NODE_INDEX:
            if branch_1.has_source:
                U_i_012 = np.array([[0.0, self._U_phase, 0.0]]).transpose()
            else:
                U_i_012 = np.array([[0.0, 0.0, 0.0]]).transpose()
        else:
            U_i_012 = self.get_node_voltage_012(i)
        U_j_012 = self.get_node_voltage_012(j)
        U_ij_012 = U_i_012 - U_j_012
        I_ij_012 = np.matmul(Y_b_012, U_ij_012)
        return I_ij_012

    def get_branch_current_abc(self, branch: Branch) -> np.array:
        """Returns the current components in the specified branch in the 
        abc-reference frame.
        """
        I_ij_012 = self.get_branch_current_012(branch)
        I_ij_abc = np.matmul(A, I_ij_012)
        return I_ij_abc


class LineToGroundFault(UnSymmetricalFault):

    def get_fault_current_012(self) -> np.array:
        k = self._faulted_node_index
        Z_kk_0 = self._network_0.get_matrix_element(k, k)
        Z_kk_1 = self._network_1.get_matrix_element(k, k)
        Z_kk_2 = self._network_2.get_matrix_element(k, k)
        I_f_0 = I_f_1 = I_f_2 = self._U_phase / (3.0 * self._Z_f + Z_kk_0 + Z_kk_1 + Z_kk_2)
        self._I_f_012 = np.array([[I_f_0, I_f_1, I_f_2]]).transpose()
        return self._I_f_012


class LineToLineFault(UnSymmetricalFault):

    def get_fault_current_012(self) -> np.array:
        k = self._faulted_node_index
        Z_kk_1 = self._network_1.get_matrix_element(k, k)
        Z_kk_2 = self._network_2.get_matrix_element(k, k)
        I_f_0 = 0.0
        I_f_1 = self._U_phase / (Z_kk_1 + Z_kk_2 + self._Z_f)
        I_f_2 = -I_f_1
        self._I_f_012 = np.array([[I_f_0, I_f_1, I_f_2]]).transpose()
        return self._I_f_012


class LineToLineToGroundFault(UnSymmetricalFault):

    def get_fault_current_012(self) -> np.array:
        k = self._faulted_node_index
        Z_kk_0 = self._network_0.get_matrix_element(k, k)
        Z_kk_1 = self._network_1.get_matrix_element(k, k)
        Z_kk_2 = self._network_2.get_matrix_element(k, k)

        Z_series = Z_kk_0 + 3 * self._Z_f
        Z_parallel = Z_kk_2 * Z_series / (Z_kk_2 + Z_series)
        Z = Z_kk_1 + Z_parallel

        I_f_1 = self._U_phase / Z
        I_f_2 = Z_series / (Z_kk_2 + Z_series) * (-I_f_1)
        I_f_0 = Z_kk_2 / (Z_kk_2 + Z_series) * (-I_f_1)

        self._I_f_012 = np.array([[I_f_0, I_f_1, I_f_2]]).transpose()
        return self._I_f_012
