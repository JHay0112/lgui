"""
Defines nodes for interconnecting components
"""

from components import Component

class Node:
    """
    Defines a node where components can be connected.
    """
    
    def __init__(self):

        self.components: list[Component] = []