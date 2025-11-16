from typing import List, Tuple, Optional, Union, Dict, Iterator
from dataclasses import dataclass, field
from enum import IntEnum
import math
import pandas as pd


TImpedanceValue = Union[float, complex]
TImpedanceMatrix = List[List[TImpedanceValue]]
TImpedanceMatrixColumn = TImpedanceMatrixRow = List[TImpedanceValue]
REF_NODE_INDEX = -1


@dataclass
class MatrixShape:
    rows: int = 0
    columns: int = 0

    def __str__(self):
        return f"({self.rows}, {self.columns})"


@dataclass
class Branch:
    ID: int
    start_node: 'Node'
    end_node: 'Node'
    impedance: TImpedanceValue
    has_source: bool = False

    @property
    def nodes(self) -> tuple['Node', 'Node']:
        return self.start_node, self.end_node

    def __str__(self):
        return (
            f"Branch {self.ID} "
            f"[{self.start_node.ID}->{self.end_node.ID}]: "
            f"Z = {self.impedance}"
        )


class Direction(IntEnum):
    """
    IntEnum-class that defines the reference current direction of the branch as 
    seen from a network node.
    """
    INCOMING = 1
    OUTGOING = -1


@dataclass
class Node:
    ID: str = ''
    index: int = 0
    _incoming: Dict[int, Branch] = field(init=False)
    _outgoing: Dict[int, Branch] = field(init=False)

    def __post_init__(self):
        self._incoming = {}
        self._outgoing = {}

    def connect(self, branch: Branch, direction: Direction):
        """Connects a branch with the node."""
        if direction == Direction.INCOMING:
            self._incoming.setdefault(branch.ID, branch)
        if direction == Direction.OUTGOING:
            self._outgoing.setdefault(branch.ID, branch)

    @property
    def incoming(self) -> List[Branch]:
        return list(self._incoming.values())

    @property
    def outgoing(self) -> List[Branch]:
        return list(self._outgoing.values())

    @property
    def branches(self) -> List[Branch]:
        return self.incoming + self.outgoing

    def __str__(self):
        return f"Node {self.ID} [{self.index}]"


class CurrentPath(List[Branch]):

    def __str__(self):
        return 'Path ' + '>'.join(str(branch.ID) for branch in self)

    @property
    def impedance(self) -> TImpedanceValue:
        """Get series impedance along current path."""
        return sum(branch.impedance for branch in self)

    @property
    def kappa(self) -> float:
        """Get withstand ratio of current path."""
        Z_path = self.impedance
        R_path = Z_path.real
        X_path = Z_path.imag
        kappa = 1.02 + 0.98 * math.exp(-3.0 * R_path / X_path)
        return kappa


class Network:

    def __init__(self):
        self._matrix: TImpedanceMatrix = []
        self.shape: MatrixShape = MatrixShape()
        self._branches: Dict[int, Branch] = {}
        self._branch_cnt: int = 0
        self._ref_node = Node('ref', REF_NODE_INDEX)
        self._nodes_IDs: Dict[str, Node] = {self._ref_node.ID: self._ref_node}
        self._nodes_indexes: Dict[int, Node] = {self._ref_node.index: self._ref_node}
        self._node_index_cnt: int = -1
    
    def _append_column(
        self, 
        column: Optional[TImpedanceMatrixColumn] = None
    ) -> None:
        for i, row in enumerate(self._matrix):
            if column is None:
                row.append(0.0)
            else:
                try:
                    row.append(column[i])
                except IndexError:
                    row.append(0.0)
        self.shape.columns += 1

    def _append_row(
        self, 
        row: Optional[TImpedanceMatrixRow] = None
    ) -> None:
        if row is None:
            new_row = [0.0] * self.shape.columns
        else:
            if len(row) > self.shape.columns:
                new_row = row[:self.shape.columns]
            elif len(row) < self.shape.columns:
                new_row = row + [0.0] * (self.shape.columns - len(row))
            else:
                new_row = row
        self._matrix.append(new_row)
        self.shape.rows += 1

    def _set_element(
        self, 
        row_index: int, 
        column_index: int, 
        Z: TImpedanceValue
    ) -> None:
        row = self._matrix[row_index]
        row[column_index] = Z

    def get_matrix_element(
        self, 
        row_index: int, 
        column_index: int
    ) -> TImpedanceValue:
        """Get impedance value at given row and column index."""
        row = self._matrix[row_index]
        return row[column_index]

    def _get_row(self, row_index: int) -> TImpedanceMatrixRow:
        return self._matrix[row_index]

    def _get_column(self, column_index: int) -> TImpedanceMatrixColumn:
        return [row[column_index] for row in self._matrix]

    def matrix_elements(self) -> Iterator[Tuple[TImpedanceValue, int, int]]:
        """Generator function for iterating over the matrix elements.

        Yields
        ------
        Tuple containing the element (impedance value), its row index and column
        index.
        """
        for i, row in enumerate(self._matrix):
            for j in range(len(row)):
                yield self.get_matrix_element(i, j), i, j

    def _add_impedance_case1(
        self, 
        Z: TImpedanceValue, 
        has_source: bool
    ) -> None:
        """Adds branch impedance between reference node and new node."""
        # update impedance matrix
        self._append_row()
        self._append_column()
        self._set_element(-1, -1, Z)
        # add branch
        self._create_branch(REF_NODE_INDEX, self.shape.rows - 1, Z, has_source)

    def _add_impedance_case2(
        self, 
        Z: TImpedanceValue, 
        k: int, 
        has_source: bool
    ) -> None:
        """Adds branch impedance between existing node `k` and new node."""
        # update impedance matrix
        row = self._get_row(k)
        new_row = list(row)
        Z_kk = self.get_matrix_element(k, k)
        Z_new = Z_kk + Z
        new_row.append(Z_new)
        new_column = list(row)
        self._append_column(new_column)
        self._append_row(new_row)
        # add branch
        self._create_branch(k, self.shape.rows - 1, Z, has_source)

    def _add_impedance_case3a(
        self, 
        Z: TImpedanceValue, 
        k: int, 
        has_source: bool
    ) -> None:
        """Adds branch impedance between existing node `k` and reference node."""
        # update impedance matrix
        new_matrix = [
            [0.0 for _ in range(self.shape.columns)] 
            for _ in range(self.shape.rows)
        ]
        Z_kk = self.get_matrix_element(k, k)
        for Z_ij, i, j in self.matrix_elements():
            Z_ik = self.get_matrix_element(i, k)
            Z_kj = self.get_matrix_element(k, j)
            new_matrix[i][j] = Z_ij - (Z_ik * Z_kj) / (Z_kk + Z)
        self._matrix = new_matrix
        # add branch
        self._create_branch(k, REF_NODE_INDEX, Z, has_source)

    def _add_impedance_case3b(
        self, 
        Z: TImpedanceValue, 
        k: int, 
        has_source: bool
    ) -> None:
        """Adds branch impedance between reference node and existing node `k`."""
        # update impedance matrix
        new_matrix = [
            [0.0 for _ in range(self.shape.columns)] 
            for _ in range(self.shape.rows)
        ]
        Z_kk = self.get_matrix_element(k, k)
        for Z_ij, i, j in self.matrix_elements():
            Z_ik = self.get_matrix_element(i, k)
            Z_kj = self.get_matrix_element(k, j)
            new_matrix[i][j] = Z_ij - (Z_ik * Z_kj) / (Z_kk + Z)
        self._matrix = new_matrix
        # add branch
        self._create_branch(REF_NODE_INDEX, k, Z, has_source)

    def _add_impedance_case4(
        self, 
        Z: TImpedanceValue, 
        k: int, 
        j: int, 
        has_source: bool
    ) -> None:
        """Adds branch impedance between existing node `k` and existing node `j`."""
        # update impedance matrix
        new_matrix = [
            [0.0 for _ in range(self.shape.columns)] 
            for _ in range(self.shape.rows)
        ]
        Z_kk = self.get_matrix_element(k, k)
        Z_jj = self.get_matrix_element(j, j)
        for Z_mn, m, n in self.matrix_elements():
            Z_jm = self.get_matrix_element(j, m)
            Z_km = self.get_matrix_element(k, m)
            Z_jn = self.get_matrix_element(j, n)
            Z_kn = self.get_matrix_element(k, n)
            Z_jk = self.get_matrix_element(j, k)
            new_matrix[m][n] = (
                Z_mn 
                - (Z_jm - Z_km) * (Z_jn - Z_kn) 
                / (Z_jj + Z_kk - 2 * Z_jk + Z)
            )
        self._matrix = new_matrix
        # add branch
        self._create_branch(k, j, Z, has_source)

    def _create_branch(
        self,
        start_node_index: int,
        end_node_index: int,
        impedance: TImpedanceValue,
        has_source: bool = False
    ) -> Branch:
        # get the start and end node of the branch
        start_node = self._nodes_indexes[start_node_index]
        end_node = self._nodes_indexes[end_node_index]
        # create new branch and add it to the dict of branches.
        self._branch_cnt += 1
        new_branch = Branch(self._branch_cnt, start_node, end_node, impedance, has_source)
        self._branches[self._branch_cnt] = new_branch
        # connect the branch with its start and end node
        start_node.connect(new_branch, Direction.OUTGOING)
        end_node.connect(new_branch, Direction.INCOMING)
        return new_branch
    
    def _get_node_index(self, node_ID: str | None) -> int | None:
        if node_ID is None:
            # reference node is asked
            return self._ref_node.index
        else:
            node = self._nodes_IDs.get(node_ID)
            if node is None:
                # new node
                self._node_index_cnt += 1
                new_node = Node(node_ID, self._node_index_cnt)
                self._nodes_IDs[node_ID] = new_node
                self._nodes_indexes[self._node_index_cnt] = new_node
                return None  # indicates a new node has been created
            else:
                return node.index  # already existing node
        
    def add_branch(
        self, 
        Z: TImpedanceValue, 
        start_node_ID: str | None = None,
        end_node_ID: str | None = None,
        has_source: bool = False
    ) -> None:
        """
        Adds a branch with impedance `Z` to network.

        Parameters
        ----------
        Z :
            Value of branch impedance.
        start_node_ID : optional
            Name of the start node of the branch. If `None` (default), the 
            reference network node is assumed.
        end_node_ID : optional
            Name of the end node of the branch. If `None` (default), the 
            reference network node is assumed.
        has_source : optional
            Boolean to indicate if the branch contains a voltage source. Default
            is `False`.

        Notes
        -----
        Newly added nodes are assigned a successive index (integer number) in 
        the order they are added, starting from index 0.
        """
        start_node_index = self._get_node_index(start_node_ID)
        end_node_index = self._get_node_index(end_node_ID)
        if (start_node_index == REF_NODE_INDEX) and (end_node_index is None):
            # case 1: branch between reference node and new node
            self._add_impedance_case1(Z, has_source)
        elif (0 <= start_node_index < self.shape.rows) and (end_node_index is None):
            # case 2: branch between existing node and new node
            self._add_impedance_case2(Z, start_node_index, has_source)
        elif (0 <= start_node_index < self.shape.rows) and (end_node_index == REF_NODE_INDEX):
            # case 3a: branch between existing node and reference node
            self._add_impedance_case3a(Z, start_node_index, has_source)
        elif (start_node_index == REF_NODE_INDEX) and (0 <= end_node_index < self.shape.rows):
            # case 3b: branch between reference node and existing node
            self._add_impedance_case3b(Z, end_node_index, has_source)
        elif (0 <= start_node_index < self.shape.rows) and (0 <= end_node_index < self.shape.rows):
            # case 4: branch between two existing nodes
            self._add_impedance_case4(Z, start_node_index, end_node_index, has_source)
        else:
            raise ValueError('cannot add impedance to network')

    def get_branch(
        self, 
        ID: Union[int, tuple[str | int, str]],
    ) -> Branch | List[Branch]:
        """
        Returns the network branch with the given ID in case ID is an int.
        Otherwise, ID must be a tuple with the IDs of the start node and the end
        node of the branch.

        If the ID is a tuple, it may also be possible that there are multiple
        branches between the same start node and end node. In that case a list
        of these branches will be returned.

        If the ID is a tuple, but the branch does not exist, a new branch with
        infinite impedance (resistance) is returned. The start and end node of
        this branch are set to the indicated start and end node in the call.
        This is provided for zero sequence networks, where branches can be open.
        Such branches aren't included in the impedance matrix of the zero
        sequence network, but their corresponding, closed branches do exist in
        the positive and negative sequence networks.
        """
        if isinstance(ID, int):
            return self._branches.get(ID)

        ID_list = []
        for branch in self._branches.values():
            start_node, end_node = branch.nodes
            if (start_node.ID, end_node.ID) == ID or (end_node.ID, start_node.ID) == ID:
                ID_list.append(branch.ID)

        branches = []
        for ID in ID_list:
            branch = self._branches.get(ID)
            branches.append(branch)

        if branches:
            if len(branches) == 1:
                return branches[0]
            else:
                return branches
        else:
            start_node = self.get_node(ID[0])
            end_node = self.get_node(ID[1])
            open_branch = self._create_branch(
                start_node.index, end_node.index,
                math.inf
            )
            return open_branch

    def get_paths(self, node_ID: str) -> List[CurrentPath]:
        """Returns all current paths between the reference node and the node
        with the specified ID.
        """
        
        def _search(
            present_node: Node, 
            present_path: CurrentPath, 
            previous_branch: Optional[Branch] = None
        ) -> None:
            while present_node.index != REF_NODE_INDEX:
                # skip previous branch on the path to prevent to go back on the 
                # same path
                if previous_branch:
                    present_branches = [
                        branch for branch in present_node.branches 
                        if branch is not previous_branch
                    ]
                else:
                    present_branches = present_node.branches
                if len(present_branches) > 1:
                    for branch in present_branches[1:]:
                        new_path = CurrentPath(present_path)
                        paths.append(new_path)
                        new_path.append(branch)
                        next_node = (
                            branch.end_node 
                            if branch.end_node.index != present_node.index 
                            else branch.start_node
                        )
                        _search(next_node, new_path, branch)
                branch_0 = present_branches[0]
                present_path.append(branch_0)
                present_node = (
                    branch_0.end_node 
                    if branch_0.end_node.index != present_node.index 
                    else branch_0.start_node
                )
                previous_branch = branch_0

        paths = []
        initial_path = CurrentPath()
        paths.append(initial_path)
        initial_node = self._nodes_IDs[node_ID]
        _search(initial_node, initial_path)
        return paths

    def __str__(self):
        index = [
            self._nodes_indexes[i].ID
            for i in range(self.shape.rows)
        ]
        columns = index
        df = pd.DataFrame(
            data=self._matrix,
            index=index,
            columns=columns
        )
        with pd.option_context(
                'display.max_rows', None,
                'display.max_columns', None,
                'display.width', 320
        ):
            return str(df)

    def show_impedance_matrix(self) -> None:
        """Prints the bus impedance matrix of the network to screen."""
        print(str(self))

    def get_node_index(self, node_ID: str) -> int:
        """Returns the index of the node whose ID is given."""
        node_index = self._nodes_IDs[node_ID].index
        return node_index

    def get_node(self, node_ID: str) -> Node:
        """Returns the `Node` object whose ID is given."""
        return self._nodes_IDs[node_ID]

    @property
    def nodes(self) -> Iterator[Node]:
        """Returns an iterator over the nodes in the network."""
        return iter(node for node in self._nodes_indexes.values() if node.index != -1)
    
    @property
    def branches(self) -> Iterator[Branch]:
        """Returns an iterator over the branches in the network."""
        return iter(self._branches.values())

    def rebuild(self) -> 'Network':
        """
        Rebuilds the network, e.g. after changing the impedance value of a
        network branch.
        """
        new_network = self.__class__()
        for branch in self.branches:
            new_network.add_branch(
                branch.impedance,
                branch.start_node.ID,
                branch.end_node.ID,
                branch.has_source
            )
        return new_network


__all__ = [
    "Branch",
    "Node",
    "CurrentPath",
    "Network",
    "REF_NODE_INDEX"
]
