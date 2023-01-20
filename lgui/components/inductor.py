
import numpy as np

from typing import Union

from .component import Component

class Inductor(Component):
    """
    Inductor

    Parameters
    ----------

    value: Union[str, int, float]
        The value of the inductor.
    """

    TYPE = "L"
    NAME = "Inductor"

    def __init__(self, value: Union[str, int, float]):

        super().__init__(value)

    def __draw_on__(self, editor, layer):

        start_x, start_y = self.ports[0].position
        end_x, end_y = self.ports[1].position
        
        LOOPS = 4
        LEAD_LENGTH = 0.2
        LOOP_RADIUS = (1 - 2*LEAD_LENGTH)/(2*LOOPS)

        # leads
        offset = self.along(LEAD_LENGTH)
        mid = offset + (start_x, start_y)
        layer.stroke_line(start_x, start_y, mid[0], mid[1])
        mid = (end_x, end_y) - offset
        layer.stroke_line(mid[0], mid[1], end_x, end_y)

        angle_offset = np.arccos(
            np.clip(
                np.dot(
                    offset/np.linalg.norm(offset), np.array([1, 0])
                ), 
            -1.0, 1.0)
        ) % np.pi

        # loops
        for l in range(LOOPS):
            mid = self.along(LEAD_LENGTH + (2*l + 1)*LOOP_RADIUS) + (start_x, start_y)
            layer.stroke_arc(
                mid[0], mid[1], 
                LOOP_RADIUS*editor.STEP/editor.SCALE, 
                np.pi - angle_offset, -angle_offset 
            )
