
from .component import Component

class Capacitor(Component):
    """
    Capacitor

    Parameters
    ----------

    value: str | int | float
        The value of the capacitor.
    """

    TYPE = "C"
    NAME = "Capacitor"

    def __init__(self, value: str | int | float):

        super().__init__(self, value)

    def __draw_on__(self, editor, layer):

        start_x, start_y = self.ports[0].position
        end_x, end_y = self.ports[1].position
        
        PLATE_WIDTH = 0.4
        PLATE_SEP = 0.03

        # lead 1
        mid = self.along(0.5 - PLATE_SEP) + (start_x, start_y)
        layer.stroke_line(start_x, start_y, mid[0], mid[1])

        # plate 1
        plate = self.orthog(PLATE_WIDTH)
        shift = mid - 0.5*plate
        layer.stroke_line(shift[0], shift[1], shift[0] + plate[0], shift[1] + plate[1])

        # lead 2
        mid = self.along(0.5 + PLATE_SEP) + (start_x, start_y)
        layer.stroke_line(mid[0], mid[1], end_x, end_y)

        # plate 2
        plate = self.orthog(PLATE_WIDTH)
        shift = mid - 0.5*plate
        layer.stroke_line(shift[0], shift[1], shift[0] + plate[0], shift[1] + plate[1])
