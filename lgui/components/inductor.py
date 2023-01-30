
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

        length = self.length()

        start = self.ports[0].position
        end = self.ports[1].position
        mid = 0.5 * self.along() * length + start
        
        LOOPS = 4
        LOOP_RADIUS = 0.4 * editor.STEP

        angle_offset = np.arccos(
            np.dot(np.array([1, 0]), self.along())
        )

        # lead 1
        shift = mid + 2 * (-LOOPS//2) * LOOP_RADIUS * self.along()
        layer.stroke_line(start[0], start[1], shift[0], shift[1])

        # lead 2
        shift = mid + 2 * (LOOPS//2) * LOOP_RADIUS * self.along()
        layer.stroke_line(shift[0], shift[1], end[0], end[1])

        # offset correction sign
        # flips offset angle if the end is lower than the start
        sign = 1 if (end[1] - start[1]) > 0 else -1

        # loops
        for l in range(-LOOPS // 2, LOOPS // 2):
            centre = (2 * l + 1) * LOOP_RADIUS * self.along() + mid
            layer.stroke_arc(
                centre[0], centre[1], 
                LOOP_RADIUS, 
                np.pi + sign * angle_offset, sign * angle_offset
            )
