"""
Defines the components that lgui can simulate
"""

import os

DIR = os.path.dirname(__file__)

class Node:

    """
    Describes the node that joins components.

    Parameters
    ----------

    id: int = 0
        The id of the node, 0 implies ground.
    """

    def __init__(self, id: int = 0):

        self.position = [0, 0]
        self.id = id

class Component:

    """
    Describes an lgui component.

    Parameters
    ----------

    ctype: str
        The type of the component selected from Component.TYPES
    """

    TYPES = ("R", "L", "C", "W")
    """Component types"""
    R = TYPES[0]
    L = TYPES[1]
    C = TYPES[2]
    W = TYPES[3]

    next_ids = {ctype: 0 for ctype in TYPES}
    next_node_id = 0

    def __init__(self, ctype: str, value: int | float | str):

        self.type = ctype
        self.value = value
        self.ports: list[Node] = [Node(Component.next_node_id), Node(Component.next_node_id+1)]
        self.id = Component.next_ids[self.type]

        Component.next_node_id += 2

    def to_lcapy(self) -> str:
        """
        Produces the lcapy netlist representation of the component
        """

        # TODO: assign port ids based on position
        out = f"{self.type}{self.id} {self.ports[0].id} {self.ports[1].id}"
        if self.value is not None:
            out += f" {{{self.value}}}"
        return out