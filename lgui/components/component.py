"""
Defines the components that lgui can simulate
"""

import numpy as np
import ipycanvas as canvas

from typing import Union
from abc import ABC, abstractmethod


class Node:

    """
    Describes the node that joins components.
    """

    def __init__(self):

        self.position: tuple(int, int) = (0, 0)

    def __eq__(self, other: 'Node') -> bool:

        return self.position == other.position


class Component(ABC):

    """
    Describes an lgui component.
    This is an abstract class, specific components are derived from here.

    Parameters
    ----------

    value: Union[str, int, float]
        The value of the component.
    """

    next_id: int = 0
    kinds = {}

    def __init__(self, value: Union[str, int, float]):

        self.value: str = value
        self.ports: list[Node] = [Node(), Node()]
        self.id = type(self).next_id
        type(self).next_id += 1
        self.kind = None
        self.initial_value = None

    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> str:
        """
        Component type identifer used by lcapy.
        E.g. Resistors have the identifier R.
        """
        ...

    @property
    @classmethod
    @abstractmethod
    def NAME(cls) -> str:
        """
        The full name of the component.
        E.g. Resistor
        """
        ...

    def __str__(self) -> str:

        return self.TYPE + ' ' + '(%s, %s) (%s, %s)' % \
            (self.ports[0].position[0], self.ports[0].position[1],
             self.ports[1].position[0], self.ports[1].position[1])

    @abstractmethod
    def __draw_on__(self, editor, layer: canvas.Canvas):
        """
        Handles drawing specific features of components.
        Component end nodes are handled by the draw_on method, which calls this abstract method.
        """
        ...

    def length(self) -> float:
        """
        Computes the length of the component.
        """
        return np.linalg.norm(np.abs(np.array(self.ports[1].position) - np.array(self.ports[0].position)))

    def along(self) -> np.array:
        """
        Computes a unit vector pointing along the line of the component.
        If the length of the component is zero, this will return the zero vector.
        """
        length = self.length()
        if length == 0:
            return np.array((0, 0))
        else:
            return (np.array(self.ports[1].position) - np.array(self.ports[0].position))/length

    def orthog(self) -> np.array:
        """
        Computes a unit vector pointing anti-clockwise to the line of the component.
        """
        delta = self.along()
        theta = np.pi/2
        rot = np.array([[np.cos(theta), -np.sin(theta)],
                       [np.sin(theta), np.cos(theta)]])
        return np.dot(rot, delta)

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

        # abstract method for drawing components
        self.__draw_on__(editor, layer)

        # node dots
        start = self.ports[0].position
        end = self.ports[1].position
        layer.fill_arc(start[0], start[1], editor.STEP // 5, 0, 2 * np.pi)
        layer.fill_arc(end[0], end[1], editor.STEP // 5, 0, 2 * np.pi)
