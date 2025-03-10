from typing import List, Optional, Union
from abc import ABC, abstractmethod
import numpy as np
from short_circuit.network import Network, REF_NODE_INDEX, Branch
from short_circuit.unsymmetrical_faults import A


class OpenConductorFault(ABC):

    def __init__(self, network_012: List[Network], U_phase: Union[float, complex] = 1.0):
        self._network_012 = network_012
        self._U_phase = U_phase
        self._faulted_branch: Optional[Branch] = None
        self._U_pq_012: Optional[np.array] = None
        self._I_mn_012: Optional[np.array] = None

    def set_faulted_branch(self, branch_ID: int, I_pre_fault: Union[float, complex]):
        self._faulted_branch = self._network_012[1].get_branch(branch_ID)
        Z_Th_pq_012 = [self._calculate_thevenin_impedance(seq) for seq in range(3)]
        U_Th_pq_1 = Z_Th_pq_012[1] * I_pre_fault
        self._calculate_symmetric_components(Z_Th_pq_012, U_Th_pq_1)

    def _calculate_thevenin_impedance(self, sequence: int) -> Union[float, complex]:
        m = self._faulted_branch.start_node.index
        n = self._faulted_branch.end_node.index
        Z_mm = self._network_012[sequence].get_matrix_element(m, m)
        Z_nn = self._network_012[sequence].get_matrix_element(n, n)
        Z_mn = self._network_012[sequence].get_matrix_element(m, n)
        Z_Th_mn = Z_mm + Z_nn - 2 * Z_mn

        branch_mn = self._network_012[sequence].get_branch(self._faulted_branch.ID, m, n)
        Z_l = branch_mn.impedance

        Z_Th_pq = -(Z_l ** 2) / (Z_Th_mn - Z_l)
        return Z_Th_pq

    @abstractmethod
    def _calculate_symmetric_components(self, Z_Th_pq_012, U_Th_pq_1):
        ...

    def get_node_voltage_012(self, node: int, U_pre_fault: Union[float, complex] = 1.0) -> np.array:
        i = node
        m = self._faulted_branch.start_node.index
        n = self._faulted_branch.end_node.index
        Z_im_012 = np.array([self._network_012[seq].get_matrix_element(i, m) for seq in range(3)])
        Z_in_012 = np.array([self._network_012[seq].get_matrix_element(i, n) for seq in range(3)])
        Z_l_012 = np.array(
            [self._network_012[seq].get_branch(self._faulted_branch.ID, m, n) for seq in range(3)]
        )
        dU_012 = (Z_im_012 - Z_in_012) / Z_l_012 * self._U_pq_012
        U_012 = np.array([0.0, U_pre_fault, 0.0]) + dU_012
        return U_012

    def get_node_voltage_abc(self, node: int) -> np.array:
        U_012 = self.get_node_voltage_012(node)
        U_abc = np.matmul(A, U_012)
        return U_abc

    def get_branch_current_012(self, branch_ID: int) -> np.array:
        branch_1 = self._network_012[1].get_branch(branch_ID)
        branch_2 = self._network_012[2].get_branch(branch_ID)
        branch_0 = self._network_012[0].get_branch(branch_ID, branch_1.start_node.index, branch_1.end_node.index)
        Z_b_0 = branch_0.impedance
        Z_b_1 = branch_1.impedance
        Z_b_2 = branch_2.impedance
        Y_b_0 = 1 / Z_b_0
        Y_b_1 = 1 / Z_b_1
        Y_b_2 = 1 / Z_b_2
        Y_b_012 = np.diagflat([Y_b_0, Y_b_1, Y_b_2])
        if branch_1.start_node.index == REF_NODE_INDEX:
            if branch_1.has_source:
                U_i_012 = np.array([[0.0, self._U_phase, 0.0]]).transpose()
            else:
                U_i_012 = np.array([[0.0, 0.0, 0.0]]).transpose()
        else:
            U_i_012 = self.get_node_voltage_012(branch_1.start_node.index)
        U_j_012 = self.get_node_voltage_012(branch_1.end_node.index)
        U_ij_012 = U_i_012 - U_j_012
        I_ij_012 = np.matmul(Y_b_012, U_ij_012)
        return I_ij_012

    def get_branch_current_abc(self, branch_ID: int) -> np.array:
        I_ij_012 = self.get_branch_current_012(branch_ID)
        I_ij_abc = np.matmul(A, I_ij_012)
        return I_ij_abc


class OneOpenConductorFault(OpenConductorFault):

    def _calculate_symmetric_components(self, Z_Th_pq_012, U_Th_pq_1):
        Z_parallel = Z_Th_pq_012[2] * Z_Th_pq_012[0] / (Z_Th_pq_012[2] + Z_Th_pq_012[0])
        I_mn_1 = U_Th_pq_1 / (Z_Th_pq_012[1] + Z_parallel)
        U_pq_0 = U_pq_1 = U_pq_2 = Z_parallel * I_mn_1
        I_mn_2 = -U_pq_2 / Z_Th_pq_012[2]
        I_mn_0 = -U_pq_0 / Z_Th_pq_012[0]
        self._U_pq_012 = np.array([U_pq_0, U_pq_1, U_pq_2])
        self._I_mn_012 = np.array([I_mn_0, I_mn_1, I_mn_2])


class TwoOpenConductorFault(OpenConductorFault):

    def _calculate_symmetric_components(self, Z_Th_pq_012, U_Th_pq_1):
        Z_series = Z_Th_pq_012[0] + Z_Th_pq_012[1] + Z_Th_pq_012[2]
        I_mn_0 = I_mn_1 = I_mn_2 = U_Th_pq_1 / Z_series
        U_pq_0 = -Z_Th_pq_012[0] * I_mn_0
        U_pq_1 = U_Th_pq_1 - Z_Th_pq_012[1] * I_mn_1
        U_pq_2 = -Z_Th_pq_012[2] * I_mn_2
        self._U_pq_012 = np.array([U_pq_0, U_pq_1, U_pq_2])
        self._I_mn_012 = np.array([I_mn_0, I_mn_1, I_mn_2])
