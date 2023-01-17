"""
Defines the components that lgui can simulate
"""

import numpy as np
import ipycanvas as canvas
import math

class Node:

    """
    Describes the node that joins components.
    """

    def __init__(self):

        self.position: tuple(int, int) = (0, 0)
        self.is_ground: bool = False

    def __eq__(self, other: 'Node') -> bool:

        return self.position == other.position

class Component:

    """
    Describes an lgui component.

    Parameters
    ----------

    ctype: str
        The type of the component selected from Component.TYPES
    """

    NAMES = (
        "Resistor",
        "Inductor",
        "Capacitor",
        "Wire",
        "Voltage",
        "Current"
    )

    TYPES = ("R", "L", "C", "W", "V", "I")
    """Component types"""
    R, L, C, W, V, I = TYPES

    HEIGHT = 4

    next_ids: dict[str, int] = {ctype: 0 for ctype in TYPES}

    def __init__(self, ctype: str, value: int | float | str):

        self.type = ctype
        self.value = value
        self.ports: list[Node] = [Node(), Node()]
        self.id = Component.next_ids[self.type]
        Component.next_ids[self.type] += 1

    def along(self, p: float) -> np.array:
        """
        Computes the point some proportion along the line of the component.
        This is relative to the position of the zero-th port.

        Parameters
        ----------

        p: float
            Proportion of length along component.
        """
        delta = np.array(self.ports[1].position) - np.array(self.ports[0].position)
        return p*delta

    def orthog(self, p: float) -> np.array:
        """
        Computes the point some proportion to the right (anti-clockwise) of the self.
        This is relative to the position of the zero-th port.

        Parameters
        ----------

        p: float
            Proportion of the length of the component.
        """
        delta = np.array(self.ports[0].position) - np.array(self.ports[1].position) 
        theta = np.pi/2
        rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        return p*np.dot(rot, delta)

    def draw_on(self, editor, layer: canvas.Canvas):
        """
        Draws a single component on a canvas.

        Parameters
        ----------

        editor: Editor
            The editor object to draw on
        layer: Canvas = None
            Layer to draw component on
        """

        start_x, start_y = self.ports[0].position
        end_x, end_y = self.ports[1].position

        with canvas.hold_canvas():

            layer.stroke_style = "#252525"

            match self.type:
                case Component.R: # Resistors
                    ...
                case Component.L: # Inductors
                    ...
                case Component.C: # Capacitors

                    PLATE_WIDTH = 0.4
                    PLATE_SEP = 0.025

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

                case Component.W: # Wires

                    layer.stroke_line(start_x, start_y, end_x, end_y)

                case Component.V: # Voltage supply
                    
                    RADIUS = 0.3
                    OFFSET = 0.05

                    # lead 1
                    mid = self.along(0.5 - RADIUS) + (start_x, start_y)
                    layer.stroke_line(start_x, start_y, mid[0], mid[1])

                    # circle
                    mid = self.along(0.5) + (start_x, start_y)
                    layer.stroke_arc(mid[0], mid[1], RADIUS*Component.HEIGHT*editor.STEP, 0, 2*np.pi)

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

                case Component.I: # Current supply
                    
                    RADIUS = 0.3
                    OFFSET = 0.05

                    # lead 1
                    mid = self.along(0.5 - RADIUS) + (start_x, start_y)
                    layer.stroke_line(start_x, start_y, mid[0], mid[1])

                    # circle
                    mid = self.along(0.5) + (start_x, start_y)
                    layer.stroke_arc(mid[0], mid[1], RADIUS*Component.HEIGHT*editor.STEP, 0, 2*np.pi)

                    # arrow body
                    arrow_start = self.along(0.5 + RADIUS/2) + (start_x, start_y)
                    arrow_end = self.along(0.5 - RADIUS/2) + (start_x, start_y)
                    layer.stroke_line(arrow_start[0], arrow_start[1], arrow_end[0], arrow_end[1])

                    # arrow head
                    arrow_shift = self.along(OFFSET)
                    arrow_orthog = self.orthog(-OFFSET)
                    layer.stroke_line(arrow_end[0], arrow_end[1], 
                        arrow_end[0]+arrow_shift[0]+arrow_orthog[0],
                        arrow_end[1]+arrow_shift[1]+arrow_orthog[1]
                    )
                    layer.stroke_line(arrow_end[0], arrow_end[1], 
                        arrow_end[0]+arrow_shift[0]-arrow_orthog[0],
                        arrow_end[1]+arrow_shift[1]-arrow_orthog[1]
                    )

                    # lead 1
                    mid = self.along(0.5 + RADIUS) + (start_x, start_y)
                    layer.stroke_line(mid[0], mid[1], end_x, end_y)

            # node dots
            layer.fill_arc(start_x, start_y, editor.STEP // 5, 0, 2 * math.pi)
            layer.fill_arc(end_x, end_y, editor.STEP // 5, 0, 2 * math.pi)
        