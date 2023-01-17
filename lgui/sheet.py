"""
Defines a grid sheet for laying out lgui components on.
"""

from .components import Component, Node

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

    def to_lcapy(self) -> str:
        """
        Produces the contents of the sheet as an lcapy netlist.
        Currently does not provide sufficient styling to be rendered with lcapy.
        """
        out = "\n"
        ids: dict[tuple[int, int], int] = {}
        next_id = 1

        for component in self.components:
            for port in component.ports:
                x, y = round(port.position[0]), round(port.position[1])
                if (x, y) not in ids.keys():
                    if port.is_ground:
                        # give the ground value
                        ids[(x, y)] = 0
                    else:
                        # if not ground
                        # assign an arbitrary id
                        ids[(x, y)] = next_id
                        next_id += 1
            # netlist formatted string       
            out += f"{component.type}{component.id}"
            for port in component.ports:
                x, y = round(port.position[0]), round(port.position[1])
                out += f" {ids[(x, y)]}"
            if component.value is not None:
                out += f" {{component.value}}"
            out += "\n"

        return out

    def add_component(self, component: Component):
        """
        Adds a component to the sheet
        """
        self.components.append(component)