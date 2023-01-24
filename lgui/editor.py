"""
Defines the component editor class.
"""

import threading
import ipywidgets as widgets
import ipycanvas as canvas
import numpy as np

from typing import Callable
from functools import wraps
from IPython.display import display

from .sheet import Sheet
from .components import *


class NotebookEditor(canvas.MultiCanvas):
    """
    The component editor is an ipywidget.
    """

    SCALE = 0.25
    HEIGHT = 1000
    WIDTH = 2000
    LAYERS = 4
    STEP = 24
    MOVE_DELAY = 0.05

    # capture user interactions
    output = widgets.Output()

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)
        self.active_component: Component = None

        super().__init__(Editor.LAYERS, width=Editor.WIDTH, height=Editor.HEIGHT)

        # layer stackup
        self.cursor_layer,   \
            self.active_layer,    \
            self.component_layer,  \
            self.grid_layer         \
            = self

        self.layout.width = "100%"
        self.layout.height = "auto"

        super().on_mouse_move(self._handle_mouse_move)
        super().on_mouse_down(self._handle_mouse_down)
        super().on_key_down(self._handle_key)

        self.component_selector = widgets.ToggleButtons(
            options={
                Resistor.NAME: Resistor,
                Capacitor.NAME: Capacitor,
                Inductor.NAME: Inductor,
                Wire.NAME: Wire,
                VoltageSupply.NAME: VoltageSupply,
                CurrentSupply.NAME: CurrentSupply,
                Ground.NAME: Ground
            },
            value=Wire
        )

        self.discard_buffer: list[Component] = []
        """
        When a component is removed from the board with CTRL+Z it is added to the discard buffer.
        It can then be returned with CTRL+Y.
        """

        self.on_client_ready(self._draw_grid)
        self.mouse_position = (0, 0)
        self.on_client_ready(self._refresh)

    def _draws(f: Callable) -> Callable:
        """
        Wrapper for methods that involve canvas operations.
        """
        @wraps(f)
        def inner(self, *args, **kwargs):
            with canvas.hold_canvas():
                f(self, *args, **kwargs)
        return inner

    def _refresh(self):
        """
        Refreshes the canvas
        """

        super().on_mouse_move(self._handle_mouse_move, True)
        x, y = self.mouse_position

        with canvas.hold_canvas():
            # deal with active component rendering
            if self.active_component is not None:

                dx, dy = (
                    x - self.active_component.ports[0].position[0],
                    y - self.active_component.ports[0].position[1]
                )

                if self.active_component.TYPE == Wire.TYPE:
                    # permit variable wire length
                    if abs(dx) > abs(dy):
                        self.active_component.ports[1].position = (
                            x - (round(x) % Editor.STEP),
                            self.active_component.ports[0].position[1]
                        )
                    else:
                        self.active_component.ports[1].position = (
                            self.active_component.ports[0].position[0],
                            y - (y % Editor.STEP)
                        )
                elif self.active_component.TYPE != Ground.TYPE:
                    # limit other components to set heights
                    if abs(dx) > abs(dy):
                        self.active_component.ports[1].position = (
                            self.active_component.ports[0].position[0] +
                            np.sign(dx)*Editor.STEP*Component.HEIGHT,
                            self.active_component.ports[0].position[1]
                        )
                    else:
                        self.active_component.ports[1].position = (
                            self.active_component.ports[0].position[0],
                            self.active_component.ports[0].position[1] +
                            np.sign(dy)*Editor.STEP*Component.HEIGHT
                        )

                self.active_layer.clear()
                self.active_component.draw_on(self, self.active_layer)

            else:
                if self.component_selector.value.TYPE == Ground.TYPE:
                    self.active_component = Ground()

            # draw a cursor for the user
            self.cursor_layer.clear()
            self.cursor_layer.stroke_rect(
                (x - (round(x) % Editor.STEP)) - Editor.STEP // 2,
                (y - (round(y) % Editor.STEP)) - Editor.STEP // 2,
                Editor.STEP
            )

        super().on_mouse_move(self._handle_mouse_move, False)
        threading.Timer(Editor.MOVE_DELAY, self._refresh).start()

    def _handle_mouse_move(self, x: int, y: int):
        """
        Handles mouse movements.
        Registered with canvas in __init__
        """
        self.mouse_position = (x, y)

    @_draws
    def _handle_mouse_down(self, x: int, y: int):
        """
        Handles mouse movements.
        Registered with canvas in __init__
        """

        x, y = round(x), round(y)

        if self.active_component is not None:

            if self.active_component.TYPE != Ground.TYPE:
                self.sheet.add_component(self.active_component)
            else:
                port = self.active_component.ports[0]
                port.position = (x - (round(x) % Editor.STEP),
                                 y - (round(y) % Editor.STEP))
                x, y = round(port.position[0]), round(port.position[1])
                self.sheet.nodes[(x, y)] = 0

            if self.active_component.TYPE == Wire.TYPE:
                last_component = self.active_component
                self.active_component = Wire()
                self.active_component.ports[0] = last_component.ports[1]
            else:
                self.active_component = None

            self.active_layer.clear()
            self.component_layer.clear()
            self.draw_components()
        else:
            # no active component
            # set component from selector
            # valueless components
            if self.component_selector.value.TYPE in (Wire.TYPE, Ground.TYPE):
                self.active_component = self.component_selector.value()
            else:
                self.active_component = self.component_selector.value(None)
            self.active_component.ports[0].position = (
                x - (round(x) % Editor.STEP), y - (round(y) % Editor.STEP))

    @_draws
    def _handle_key(self, key: str, shift_key: bool, ctrl_key: bool, meta_key: bool):
        """
        Handles presses of keys
        """

        if str(key) == "Escape" and self.active_component is not None:
            # ESC
            if self.active_component is not None:
                self.active_component = None
                self.active_layer.clear()

        elif ctrl_key:

            if str(key) == "z":
                # CTRL + Z
                self.active_component = None
                self.active_layer.clear()
                self.discard_buffer.append(self.sheet.components.pop())
                self.component_layer.clear()
                self.draw_components()
            elif str(key) == "y":
                # CTRL + Y
                if len(self.discard_buffer) > 0:
                    self.sheet.add_component(self.discard_buffer.pop())
                    self.component_layer.clear()
                    self.draw_components()

    @_draws
    def _draw_grid(self):
        """Draws a grid based upon the step size."""
        for i in range(Editor.WIDTH // Editor.STEP):
            for j in range(Editor.HEIGHT // Editor.STEP):
                self.grid_layer.fill_style = "#252525"
                self.grid_layer.fill_rect(i * Editor.STEP, j * Editor.STEP, 1)

    def display(self):
        """
        Displays self in IPython or Jupyter.
        """
        # show canvas
        display(self)
        # show buttons
        display(self.component_selector)

    def draw_components(self, layer: canvas.Canvas = None):
        """
        Draws sheet components on canvas.

        Parameters
        ----------

        layer: Canvas = None
            Layer to draw sheet components on,
            if none specified it will draw on the component layer.
        """

        if layer is None:
            layer = self.component_layer

        for component in self.sheet.components:
            component.draw_on(self, layer)
