from typing import Optional, Union
import math
from short_circuit.network import Network, REF_NODE_INDEX, CurrentPath, Branch


class ThreePhaseFault:
    """Represents a three-phase fault in a network."""

    def __init__(
        self, 
        network: Network, 
        U_prefault: Union[float, complex] = 1.0,
        c: float = 1.0
    ) -> None:
        """Creates a `ThreePhaseFault` object.
        
        Parameters
        ----------
        network:
            Positive sequence network.
        U_prefault:
            Nominal system voltage before the fault. It is the line-to-neutral
            voltage between the reference node of the network and every other
            node in the network, assuming that the network is unloaded before
            the fault (neglecting prefault load currents, the internal voltage
            sources of all synchronous machines are equal both in magnitude and
            phase, and can be replaced by one equivalent source).
        c:
            Voltage factor according to IEC 60909-0.
        """
        self._network = network
        self._U_prefault: Union[float, complex] = c * U_prefault
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
        I_k = self._U_prefault / (self._Z_kk + self._Z_fault)
        return I_k

    def get_node_voltage(self, ID: str) -> Union[float, complex]:
        """Returns the steady-state node voltage of the given node during the 
        fault.
        """
        node = self._network.get_node(ID)
        node_index = node.index
        Z_ik = self._network.get_matrix_element(node_index, self._faulted_node_index)
        U = self._U_prefault * (1.0 - Z_ik / self._Z_kk)
        return U

    def get_branch_current(
        self,
        ID: Union[int, tuple[str | int, str]]
    ) -> Union[float, complex] | list[Union[float, complex]]:
        """
        Returns the steady-state branch current in the given branch during
        the fault.

        Parameters
        ----------
        ID:
            In case ID is an int, it is the direct ID of the branch. In case
            ID is a tuple, it contains the start node ID and end node ID of the
            branch. Note however that multiple branches may be present between
            the same two nodes. In the latter case, a list of branch currents
            is returned.
        """
        def _get_branch_current(branch_: Branch) -> Union[float, complex]:
            if branch_.start_node.index == REF_NODE_INDEX:
                if branch_.has_source:
                    U_i = self._U_prefault
                else:
                    U_i = 0.0
            else:
                U_i = self.get_node_voltage(branch_.start_node.ID)  # voltage start node branch
            U_j = self.get_node_voltage(branch_.end_node.ID)        # voltage end node branch
            Z_branch = branch_.impedance
            I_ij = (U_i - U_j) / Z_branch  # current from start node to end node of branch
            if isinstance(ID, tuple) and branch_.start_node.ID == ID[1]:
                # we want current from 1st element of tuple to 2nd element of tuple:
                # if start node of branch is 2nd element of tuple: reverse current sign
                return -I_ij
            return I_ij

        branch = self._network.get_branch(ID)
        if isinstance(branch, list):
            # if ID is tuple (from_node, to_node) and multiple branches are
            # present between from_node and to_node, branch will be a list.
            branch_currents = [_get_branch_current(br) for br in branch]
            return branch_currents
        else:
            return _get_branch_current(branch)

    def get_currents_to_node(self, ID: str) -> list[tuple[str, Union[float, complex]]]:
        """
        Returns the branch currents that flow to the node with the given ID.
        The currents are returned in a list of tuples. First element of the
        tuples are the ID of the node on the other end of the branch.
        """
        node = self._network.get_node(ID)
        currents_to_node = []
        for branch in node.incoming:
            other_node = branch.start_node
            I = self.get_branch_current(branch.ID)
            currents_to_node.append((other_node.ID, I))
        for branch in node.outgoing:
            other_node = branch.end_node
            I = self.get_branch_current(branch.ID)
            currents_to_node.append((other_node.ID, -I))
        return currents_to_node

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


__all__ = ["ThreePhaseFault"]
