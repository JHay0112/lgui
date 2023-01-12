"""
Defines the components that lgui can simulate
"""

import lcapy

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

        self.connected_to: set[Component] = set()
        self.is_ground: bool = is_ground
        self._id: int = Node.next_id
        Node.next_id += 1

    def __add__(self, node: 'Node') -> 'Node':
        """
        Shorthand for joining nodes.
        """
        return self.join(node)

    @property
    def id(self):
        """
        The id of the node.
        """
        if self.is_ground:
            return 0
        else:
            return self._id

    def connect(self, comp: 'Component'):
        """
        Connects node to a component

        Parameters
        ----------

        comp: Component
            The component to add as a connection
        """
        self.connected_to.add(comp)

    def disconnect(self, comp: 'Component'):
        """
        Removes component from node

        Parameters
        ----------

        comp: Component
            The component to remove
        """
        self.connected_to.discard(comp)

    def join(self, node: 'Node') -> 'Node':
        """
        Produces a new node based on the joined nodes,
        shorthanded with '+'

        Parameters
        ----------

        node: Node
            The node to merge with.
        """
        new_node = Node(is_ground = self.is_ground or node.is_ground)
        new_node = self.connected_to | node.connected_to
        return new_node

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

    GRID_HEIGHT = 5
    """Height of components on the editor grid"""

    next_ids = {ctype: 0 for ctype in TYPES}

    def __init__(self, ctype: str, value: int | float | str):

        self.type = ctype
        self.value = value
        self.orientation = Component.N
        self.pos = (0, 0)
        self.ports: list[Node] = [Node(), Node()]
        for port in self.ports:
            port.connect(self)
        self.id = Component.next_ids[self.type]
        Component.next_ids[self.type] += 1

    def rotate(self):
        """
        Rotates the component by 90 degrees clockwise.
        """
        self.orientation = Component.ORIENTATIONS[
            (Component.ORIENTATIONS.index(self.orientation) + 1) & len(Component.ORIENTATIONS)
        ] # go to next orientation in the orientation list

    def draw(self, filepath: str):
        """
        Draws the component as the specified file.
        Uses lcapy as a drawing backend, circuitikz must be installed to work.
        See https://lcapy.readthedocs.io/en/latest/install.html
        """

        if self.value is None:
            cct = lcapy.Circuit(f"\n{self.type}{self.id} 0 1; down")
        else:
            cct = lcapy.Circuit(f"\n{self.type}{self.id} 0 1 {{{self.value}}}; down")

        cct.draw(
            filename = filepath, 
            label_ids = False, 
            draw_nodes = False, 
            label_nodes = False, 
            label_values = False
        )