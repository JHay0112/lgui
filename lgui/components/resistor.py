
from .component import Component

class Resistor(Component):
    """
    Resistor

    Parameters
    ----------

    value: str | int | float
        The value of the resistor.
    """

    TYPE = "R"
    NAME = "Resistor"

    def __init__(self, value: str | int | float):

        super().__init__(self, value)

    def __draw_on__(self, editor, layer):

        start_x, start_y = self.ports[0].position
        end_x, end_y = self.ports[1].position
        
        ZIGS = 6
        LEAD_LENGTH = 0.2
        ZIG_WIDTH = (1 - 2*LEAD_LENGTH)/(ZIGS + 1)
        ZIG_HEIGHT = 0.15

        zig_shift = self.along(ZIG_WIDTH)
        zig_orthog = self.orthog(ZIG_HEIGHT)

        # lead 1
        offset = self.along(LEAD_LENGTH)
        mid = offset + (start_x, start_y)
        layer.stroke_line(start_x, start_y, mid[0], mid[1])
        # flick 1
        layer.stroke_line(mid[0], mid[1], 
            mid[0] - zig_orthog[0] + 0.5*zig_shift[0], 
            mid[1] - zig_orthog[1] + 0.5*zig_shift[1]
        )

        # lead 2
        mid = (end_x, end_y) - offset
        layer.stroke_line(mid[0], mid[1], end_x, end_y)
        # flick 2
        layer.stroke_line(mid[0], mid[1], 
            mid[0] - zig_orthog[0] - 0.5*zig_shift[0], 
            mid[1] - zig_orthog[1] - 0.5*zig_shift[1]
        )

        for z in range(ZIGS):
            mid = self.along(LEAD_LENGTH + (z + 1/2)*ZIG_WIDTH) + (start_x, start_y)
            if z % 2 == 0:
                start = mid - zig_orthog
                end = mid + zig_shift + zig_orthog
            else:
                start = mid + zig_orthog
                end = mid + zig_shift - zig_orthog

            layer.stroke_line(start[0], start[1], end[0], end[1])
