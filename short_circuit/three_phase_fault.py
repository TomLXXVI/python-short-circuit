from typing import Optional, Union
import math
from short_circuit.network import Network, REF_NODE_INDEX, CurrentPath, Node


class ThreePhaseFault:
    """Represents a three-phase fault in a network."""

    def __init__(
        self, 
        network: Network, 
        U_phase: Union[float, complex] = 1.0, 
        c: float = 1.0
    ) -> None:
        """Creates a `ThreePhaseFault` object.
        
        Parameters
        ----------
        network:
            Positive sequence network.
        U_phase:
            Nominal system voltage at the fault location before the fault. It is 
            the phase voltage between the reference node of the network and 
            every other node in the network, assuming that the network is 
            unloaded before the fault.   
        c:
            Voltage factor according to IEC 60909-0.
        """
        self._network = network
        self._U_phase: Union[float, complex] = c * U_phase
        self._Z_kk: Optional[Union[float, complex]] = None
        self._faulted_node_ID: Optional[str] = None
        self._faulted_node_index: Optional[int] = None
        self._Z_fault: Union[float, complex] = 0.0

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
        self._faulted_node_index = k = self._network.get_node_index(node_ID)
        self._Z_kk = self._network.get_matrix_element(k, k)
        self._Z_fault = Z_fault

    def get_fault_current(self) -> Union[float, complex]:
        """Returns the steady-state fault current at the faulted node."""
        I_k = self._U_phase / (self._Z_kk + self._Z_fault)
        return I_k

    def get_node_voltage(self, node: Node) -> Union[float, complex]:
        """Returns the steady-state node voltage of the given node during the 
        fault.
        """
        node_index = node.index
        Z_ik = self._network.get_matrix_element(node_index, self._faulted_node_index)
        U = self._U_phase * (1.0 - Z_ik / self._Z_kk)
        return U

    def get_branch_current(self, branch_ID: int) -> Union[float, complex]:
        """Returns the steady-state branch current in the given branch during 
        the fault.
        """
        branch = self._network.get_branch(branch_ID)
        if branch.start_node.index == REF_NODE_INDEX:
            if branch.has_source:
                U_i = self._U_phase
            else:
                U_i = 0.0
        else:
            U_i = self.get_node_voltage(branch.start_node)
        U_j = self.get_node_voltage(branch.end_node)
        Z_branch = branch.impedance
        I_ij = (U_i - U_j) / Z_branch
        return I_ij

    def get_peak_short_circuit_current(self) -> Union[float, complex]:
        """Returns the peak short-circuit current at the faulted node."""
        paths = self._network.get_paths(self._faulted_node_ID)
        i_p = sum(self.get_path_peak_short_circuit_current(path) for path in paths)
        return i_p

    def get_path_peak_short_circuit_current(
        self, 
        path: CurrentPath
    ) -> Union[float, complex]:
        """Returns the peak short-circuit current in the given current path 
        during the fault.
        """
        branch = path[-1]
        # get the initial branch connected to the reference node
        I_branch = self.get_branch_current(branch.ID)
        i_p = path.kappa * math.sqrt(2) * I_branch
        return i_p
