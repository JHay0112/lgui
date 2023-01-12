"""
Defines the components that lgui can simulate
"""

from .flags import Power
import lcapy

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
        self.ports: list[Component | Power | None] = [None, None]
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