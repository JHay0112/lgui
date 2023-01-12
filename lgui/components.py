"""
Defines the components that lgui can simulate
"""

import lcapy

from typing import Union

class Node:
    """
    Describes the connection between components.

    Parameters
    ----------

    is_ground: bool = False
        Optional flag if node is grounded.
    """

    # 0 is reserved for the ground node
    next_id: int = 1

    def __init__(self, is_ground: bool = False):

        self.components: set[Component] = set()
        self.is_ground: bool = is_ground

        if self.is_ground:
            self._id: int = 0
        else:
            self._id: int = Node.next_id
            Node.next_id += 1

    def __eq__(self, other: 'Node') -> bool:
        return other.id == self.id
            
    @property
    def id(self):
        """
        The id of the node.
        """
        if self.is_ground:
            self._id = 0
        return self._id

    @id.setter
    def id(self, value: int):
        """
        Sets a new id.
        """
        self._id = value
        if self._id == 0:
            self.is_ground = True

    def connect(self, other: Union['Node', 'Component']):
        """
        Joins two nodes or components together and reassigns ids to lowest if necessary.

        Parameters
        ----------

        other: Node | Component
            The other node or component to be connected with
        """
        if isinstance(other, Node):
            self.components |= other.components
            other.components = self.components
            self.id = min(self.id, other.id)
            other.id = self.id
        elif isinstance(other, Component):
            self.components.add(other)

class Component:

    """
    Describes an lgui component.

    Parameters
    ----------

    ctype: str
        The type of the component selected from Component.TYPES
    """

    ORIENTATIONS = ("N", "E", "S", "W")
    """Component orientations"""
    N = ORIENTATIONS[0]
    E = ORIENTATIONS[1]
    S = ORIENTATIONS[2]
    W = ORIENTATIONS[3]

    TYPES = ("R", "L", "C", "W")
    """Component types"""
    R = TYPES[0]
    L = TYPES[1]
    C = TYPES[2]
    WIRE = TYPES[3]

    GRID_LENGTH = 2
    """Length of components on the editor grid, wires may say otherwise"""

    next_ids = {ctype: 0 for ctype in TYPES}

    def __init__(self, ctype: str, value: int | float | str):

        self.type = ctype
        self.value = value
        self.orientation = Component.S
        self._pos = (0, 0)
        self.length = Component.GRID_LENGTH
        self.ports: list[Node] = [Node(), Node()]
        for port in self.ports:
            port.connect(self)
        self.id = Component.next_ids[self.type]
        Component.next_ids[self.type] += 1

    def __getitem__(self, key: int) -> Node:
        """
        Shorthand for accessing ports.
        """
        return self.ports[key]

    @property
    def position(self, port: int = 0):
        """
        The position of the component on the grid.

        Parameters
        ----------

        port: int = 0
            The port of which to calculate the position from.

        Raises
        ------

        ValueError:
            If orientation is not specified.
        """
        if port == 0:
            pos = self._pos
        else:
            match self.orientation:
                case Component.N:
                    pos = self._pos[0] + self.length, self._pos[1]
                case Component.E:
                    pos = self._pos[0], self._pos[1] + self.length
                case Component.S:
                    pos = self._pos[0] - self.length, self._pos[1]
                case Component.W:
                    pos = self._pos[0], self._pos[1] - self.length
                case _:
                    raise ValueError("Component orientation not defined!")

        return pos

    @position.setter
    def position(self, value: tuple[int, int]):
        """Updates the position of the component on the grid. This is at port 0."""
        self._pos = value

    def rotate(self):
        """
        Rotates the component by 90 degrees clockwise.
        """
        self.orientation = Component.ORIENTATIONS[
            (Component.ORIENTATIONS.index(self.orientation) + 1) & len(Component.ORIENTATIONS)
        ] # go to next orientation in the orientation list

    def to_lcapy(self) -> str:
        """
        Produces the lcapy netlist representation of the component
        """

        match self.orientation:
            case Component.N: 
                direction = "up"
            case Component.E:
                direction = "right"
            case Component.S:
                direction = "down"
            case Component.W:
                direction = "left"
            case _:
                direction = None

        out = f"{self.type}{self.id} {self.ports[0].id} {self.ports[1].id}"
        if self.value is not None:
            out += f" {{{self.value}}}"
        if self.orientation is not None:
            out += f"; {direction}"
        return out

    def draw(self, filepath: str):
        """
        Draws the component as the specified file.
        Uses lcapy as a drawing backend, circuitikz must be installed to work.
        See https://lcapy.readthedocs.io/en/latest/install.html
        """
        lcapy.Circuit("\n" + self.to_lcapy()).draw(
            filename = filepath, 
            label_ids = False, 
            draw_nodes = False, 
            label_nodes = False, 
            label_values = False
        )