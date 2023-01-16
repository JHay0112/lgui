"""
Defines the components that lgui can simulate
"""

import numpy as np

class Node:

    """
    Describes the node that joins components.
    """

    def __init__(self):

        self.position: np.array = np.array([0, 0])
        self.is_ground: bool = False

    def __eq__(self, other: 'Node') -> bool:

        return self.position == other.position

class Component:

    """
    Describes an lgui component.

    Parameters
    ----------

    ctype: str
        The type of the component selected from Component.TYPES
    """

    NAMES = (
        "Resistor",
        "Inductor",
        "Capacitor",
        "Wire"
    )

    TYPES = ("R", "L", "C", "W")
    """Component types"""
    R = TYPES[0]
    L = TYPES[1]
    C = TYPES[2]
    W = TYPES[3]

    HEIGHT = 4

    next_ids: dict[str, int] = {ctype: 0 for ctype in TYPES}

    def __init__(self, ctype: str, value: int | float | str):

        self.type = ctype
        self.value = value
        self.ports: list[Node] = [Node(), Node()]
        self.id = Component.next_ids[self.type]
        Component.next_ids[self.type] += 1

    def along(self, p: float) -> np.array:
        """
        Computes the point some proportion along the line of the component.
        This is relative to the position of the zero-th port.

        Parameters
        ----------

        p: float
            Proportion of length along component.
        """
        delta = np.array(self.ports[1].position) - np.array(self.ports[0].position)
        return p*delta

    def orthog(self, p: float) -> np.array:
        """
        Computes the point some proportion to the right (anti-clockwise) of the component.
        This is relative to the position of the zero-th port.

        Parameters
        ----------

        p: float
            Proportion of the length of the component.
        """
        delta = np.array(self.ports[0].position) - np.array(self.ports[1].position) 
        theta = np.pi/2
        rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        return p*np.dot(rot, delta)
        