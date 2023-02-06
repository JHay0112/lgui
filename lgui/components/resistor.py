
from typing import Union

from .component import Component

class Resistor(Component):
    """
    Resistor

    Parameters
    ----------

    value: Union[str, int, float]
        The value of the resistor.
    """

    TYPE = "R"
    NAME = "Resistor"

    def __init__(self, value: Union[str, int, float]):

        super().__init__(value)

    def __draw_on__(self, editor, layer):

        length = self.length()

        start = self.ports[0].position
        end = self.ports[1].position
        mid = 0.5 * self.along() * length + start
        
        ZIGS = 6
        ZIG_WIDTH = 0.35 * editor.STEP * editor.SCALE
        ZIG_HEIGHT = 0.7 * editor.STEP * editor.SCALE

        zig_shift = ZIG_WIDTH * self.along()
        zig_orthog = ZIG_HEIGHT * self.orthog()

        # lead 1
        centre = (-ZIGS//2 - 1/2) * ZIG_WIDTH * self.along() + mid
        layer.stroke_line(start[0], start[1], centre[0], centre[1])
        layer.stroke_line(
            centre[0], centre[1], 
            centre[0] + zig_shift[0]/2 + zig_orthog[0], centre[1] + zig_shift[1]/2 + zig_orthog[1]
        )

        # lead 2
        centre = (ZIGS//2 + 1/2) * ZIG_WIDTH * self.along() + mid
        layer.stroke_line(centre[0], centre[1], end[0], end[1])
        layer.stroke_line(
            centre[0], centre[1], 
            centre[0] - zig_shift[0]/2 + zig_orthog[0], centre[1] - zig_shift[1]/2 + zig_orthog[1]
        )

        for z in range(-ZIGS//2, ZIGS//2):
            centre = z * ZIG_WIDTH * self.along() + mid
            if z % 2 == 0:
                start = centre - zig_orthog
                end = centre + zig_shift + zig_orthog
            else:
                start = centre + zig_orthog
                end = centre + zig_shift - zig_orthog

            layer.stroke_line(start[0], start[1], end[0], end[1])
