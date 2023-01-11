"""
Defines a grid sheet for laying out lgui components on.
"""

from components import Component
from nodes import Node

class Sheet:

    """
    Schematic sheet.

    Parameters
    ----------

    name: str
        The name of the sheet.
    author: str
        The author who produced the sheet.
    """

    def __init__(self, name: str, author: str):

        self.name: str = name
        self.author: str = author
        self.components: list[Component] = []
        self.nodes: list[Node] = []

    def to_lcapy(self) -> str:
        """
        Produces the contents of the sheet as an lcapy netlist.
        Currently does not provide sufficient styling to be rendered with lcapy.
        """
        ...