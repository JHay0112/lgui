"""
Defines the components that lgui can simulate
"""

import os

DIR = os.path.dirname(__file__)

class Node:

    """
    Describes the node that joins components.
    """

    def __init__(self):

        self.position: list[int, int] = [0, 0]
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

    def along(self, p: float) -> tuple[float, float]:
        """
        Computes the point some proportion along the line of the component.

        Parameters
        ----------

        p: float
            Proportion of length along component.
        """
        start_x, start_y = self.ports[0].position
        end_x, end_y = self.ports[1].position

        dx = end_x - start_x
        dy = end_y - start_y

        return p*dx + start_x, p*dy + start_y
        