"""
Defines the component editor class.
"""

import lcapy
import threading
import ipywidgets as widgets
import ipycanvas as canvas
import logging
import math
import numpy as np

from IPython.display import display

from .sheet import Sheet
from .components import Component

logging.basicConfig(filename = "out.log", level = logging.INFO)

class Editor(canvas.MultiCanvas):
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

        super().__init__(Editor.LAYERS, width = Editor.WIDTH, height = Editor.HEIGHT)

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

        with canvas.hold_canvas():
            self.draw_grid()

        self.component_selector = widgets.ToggleButtons(
            options = dict(zip(Component.NAMES, Component.TYPES)),
            value = Component.W,
            disabled = False
        )

        self.mouse_position = (0, 0)
        self._refresh()

    def _refresh(self):
        """
        Refreshes the canvas
        """

        x, y = self.mouse_position

        # deal with active component rendering
        if self.active_component is not None:

            dx, dy = (
                x - self.active_component.ports[0].position[0],
                round(y) - self.active_component.ports[0].position[1]
            )

            if self.active_component.type == Component.W:
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
            else:
                # limit other components to set heights
                if abs(dx) > abs(dy):
                    self.active_component.ports[1].position = (
                        self.active_component.ports[0].position[0] + np.sign(dx)*Editor.STEP*Component.HEIGHT,
                        self.active_component.ports[0].position[1]
                    )
                else:
                    self.active_component.ports[1].position = (
                        self.active_component.ports[0].position[0],
                        self.active_component.ports[0].position[1] + np.sign(dx)*Editor.STEP*Component.HEIGHT
                    )

            with canvas.hold_canvas():
                self.active_layer.clear()
                self.active_component.draw_on(self, self.active_layer)

        # draw a cursor for the user
        with canvas.hold_canvas():
            self.cursor_layer.clear()
            self.cursor_layer.stroke_rect(
                (x - (round(x) % Editor.STEP)) - Editor.STEP // 2, 
                (y - (round(y) % Editor.STEP)) - Editor.STEP // 2,
                Editor.STEP
            )

        threading.Timer(Editor.MOVE_DELAY, self._refresh).start()

    @output.capture()
    def _handle_mouse_move(self, x: int, y: int):
        """
        Handles mouse movements.
        Registered with canvas in __init__
        """
        self.mouse_position = (x, y)

    @output.capture()
    def _handle_mouse_down(self, x: int, y: int):
        """
        Handles mouse movements.
        Registered with canvas in __init__
        """

        x, y = round(x), round(y)

        if self.active_component is not None:
            self.sheet.add_component(self.active_component)
            self.active_component = None

            with canvas.hold_canvas():
                self.active_layer.clear()
                self.component_layer.clear()
                self.draw_components()
        else:
            # no active component
            # set component from selector
            self.active_component = Component(self.component_selector.value, None)
            self.active_component.ports[0].position = (x - (round(x) % Editor.STEP), y - (round(y) % Editor.STEP))

    @output.capture()
    def _handle_key(self, key, shift_key, ctrl_key, meta_key):
        """
        Handles presses of keys
        """

        logging.info(key)
        
        if str(key) == "Escape" and self.active_component is not None:
            # ESC
            if self.active_component is not None:
                self.active_component = None
                self.active_layer.clear()

        elif ctrl_key and str(key) == "z":
            # CTRL + Z
            self.active_component = None
            self.active_layer.clear()
            self.sheet.components.pop()
            with canvas.hold_canvas():
                self.component_layer.clear()
                self.draw_components()

    def display(self):
        """
        Displays self in IPython or Jupyter.
        """
        # show canvas
        display(self)
        # show buttons
        display(self.component_selector)

    def draw_grid(self):
        """Draws a grid based upon the step size."""
        for i in range(Editor.WIDTH // Editor.STEP):
            for j in range(Editor.HEIGHT // Editor.STEP):
                self.grid_layer.fill_style = "#252525"
                self.grid_layer.fill_rect(i * Editor.STEP, j * Editor.STEP, 1)

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