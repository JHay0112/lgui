
import numpy as np

from .component import Component

class Wire(Component):
    """
    Wire
    """

    TYPE = "W"
    NAME = "Wire"

    def __init__(self):

        super().__init__(None)

    def __draw_on__(self, editor, layer):

        start_x, start_y = self.ports[0].position
        end_x, end_y = self.ports[1].position
        
        layer.stroke_line(start_x, start_y, end_x, end_y)
