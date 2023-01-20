
import numpy as np

from .component import Component

class VoltageSupply(Component):
    """
    VoltageSupply

    Parameters
    ----------

    value: str | int | float
        The value of the voltage supply.
    """

    TYPE = "V"
    NAME = "Voltage Supply"

    def __init__(self, value: str | int | float):

        super().__init__(value)

    def __draw_on__(self, editor, layer):

        start_x, start_y = self.ports[0].position
        end_x, end_y = self.ports[1].position
        
        RADIUS = 0.3
        OFFSET = 0.05

        # lead 1
        mid = self.along(0.5 - RADIUS) + (start_x, start_y)
        layer.stroke_line(start_x, start_y, mid[0], mid[1])

        # circle
        mid = self.along(0.5) + (start_x, start_y)
        layer.stroke_arc(mid[0], mid[1], RADIUS*type(self).HEIGHT*editor.STEP, 0, 2*np.pi)

        # positive symbol
        mid = self.along(0.5 - RADIUS/2) + (start_x, start_y)
        shift = self.along(OFFSET)
        orthog = self.orthog(OFFSET)

        start = mid - shift
        end = mid + shift
        layer.stroke_line(start[0], start[1], end[0], end[1])
        start = mid - orthog
        end = mid + orthog
        layer.stroke_line(start[0], start[1], end[0], end[1])

        # negative symbol
        mid = self.along(0.5 + RADIUS/2) + (start_x, start_y)
        start = mid - orthog
        end = mid + orthog
        layer.stroke_line(start[0], start[1], end[0], end[1])

        # lead 1
        mid = self.along(0.5 + RADIUS) + (start_x, start_y)
        layer.stroke_line(mid[0], mid[1], end_x, end_y)
