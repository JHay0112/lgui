"""
Defines the components that lgui can simulate
"""

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

    TYPES = ("R", "L", "C")
    """Component types"""
    R = TYPES[0]
    L = TYPES[1]
    C = TYPES[2]

    GRID_HEIGHT = 5
    """Height of components on the editor grid"""

    next_ids = {ctype: 0 for ctype in TYPES}

    def __init__(self, ctype: str, value: int | float | str):

        self.type = ctype
        self.value = value
        self.orientation = Component.N
        self.pos = (0, 0)
        self.id = Component.next_ids[self.type]
        Component.next_ids[self.type] += 1

    def rotate(self):
        """
        Rotates the component by 90 degrees clockwise.
        """
        self.orientation = Component.ORIENTATIONS[
            (Component.ORIENTATIONS.index(self.orientation) + 1) & len(Component.ORIENTATIONS)
        ] # go to next orientation in the orientation list