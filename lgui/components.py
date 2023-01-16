"""
Defines the components that lgui can simulate
"""

import lcapy
import os

from typing import Union

DIR = os.path.dirname(__file__)

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
    WIRE = TYPES[3]

    next_ids = {ctype: 0 for ctype in TYPES}

    def __init__(self, ctype: str, value: int | float | str):

        self.type = ctype
        self.value = value
        self.ports: list[tuple[int, int]] = [(0, 0)] * 2
        self.id = Component.next_ids[self.type]

    def to_lcapy(self) -> str:
        """
        Produces the lcapy netlist representation of the component
        """

        out = f"{self.type}{self.id} {self.ports[0].id} {self.ports[1].id}"
        if self.value is not None:
            out += f" {{{self.value}}}"
        return out

    def img_path(self) -> str:
        """Gives the path to an image representation of the component"""
        return os.path.join(DIR, Component.IMG_PATH + self.type + "." + Component.IMG_EXT)