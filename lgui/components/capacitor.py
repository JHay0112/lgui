
from typing import Union

from .component import Component


class Capacitor(Component):
    """
    Capacitor

    Parameters
    ----------

    value: Union[str, int, float]
        The value of the capacitor.
    """

    TYPE = "C"
    NAME = "Capacitor"

    def __init__(self, value: Union[str, int, float]):

        super().__init__(value)

    def __draw_on__(self, editor, layer):

        length = self.length()

        start = self.ports[0].position
        end = self.ports[1].position

        mid = 0.5 * length * self.along() + start

        PLATE_WIDTH = 2.4 * editor.STEP
        PLATE_SEP = 0.4 * editor.STEP

        # lead 1
        shift = 0.5 * self.along() * PLATE_SEP
        layer.stroke_line(
            start[0], start[1],
            mid[0] - shift[0], mid[1] - shift[1]
        )

        # plate 1
        plate = 0.5 * self.orthog() * PLATE_WIDTH
        layer.stroke_line(
            mid[0] + plate[0] + shift[0], mid[1] + plate[1] + shift[1],
            mid[0] - plate[0] + shift[0], mid[1] - plate[1] + shift[1]
        )

        # lead 2
        layer.stroke_line(
            mid[0] + shift[0], mid[1] + shift[1],
            end[0], end[1]
        )

        # plate 2
        plate = 0.5 * self.orthog() * PLATE_WIDTH
        layer.stroke_line(
            mid[0] + plate[0] - shift[0], mid[1] + plate[1] - shift[1],
            mid[0] - plate[0] - shift[0], mid[1] - plate[1] - shift[1]
        )
