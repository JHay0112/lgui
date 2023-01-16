"""
Defines the component editor class.
"""

import lcapy
import threading
import ipywidgets as widgets
import ipycanvas as canvas

from .sheet import Sheet
from .components import Component

class Editor(canvas.MultiCanvas):
    """
    The component editor is an ipywidget.
    """

    SCALE = 0.25
    HEIGHT = 1000
    WIDTH = 2000
    LAYERS = 5
    STEP = 24
    MOVE_DELAY = 0.05

    # capture user interactions
    output = widgets.Output()

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)
        self.active_component: Component = None

        super().__init__(Editor.LAYERS, width = Editor.WIDTH, height = Editor.HEIGHT)

        self.control_layer, \
        self.cursor_layer, \
        self.active_layer, \
        self.component_layer, \
        self.grid_layer \
         = self

        self.layout.width = "100%"
        self.layout.height = "auto"

        super().on_mouse_move(self._handle_mouse_move)
        super().on_mouse_down(self._handle_mouse_down)

        with canvas.hold_canvas():
            self.draw_grid()

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
                abs(x - self.active_component.ports[0].position[0]),
                abs(round(y) - self.active_component.ports[0].position[1])
            )

            if dx > dy:
                self.active_component.ports[1].position = (
                    x - (round(x) % Editor.STEP), 
                    self.active_component.ports[0].position[1]
                )
            else:
                self.active_component.ports[1].position = (
                    self.active_component.ports[0].position[0], 
                    y - (y % Editor.STEP)
                )

            with canvas.hold_canvas():
                self.active_layer.clear()
                self.draw_component(self.active_component, self.active_layer)

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
        if self.active_component is not None:

            self.sheet.add_component(self.active_component)
            self.active_component = None

            with canvas.hold_canvas():
                self.component_layer.clear()
                self.draw_components()

        else:
            
            # no active component
            # this should give the option of what to place??
            # starting with a wire drawing system

            self.active_component = Component(Component.W, None)
            self.active_component.ports[0].position = (x - (round(x) % Editor.STEP), y - (round(y) % Editor.STEP))

    def draw_grid(self):
        """Draws a grid based upon the step size."""
        for i in range(Editor.WIDTH // Editor.STEP):
            for j in range(Editor.HEIGHT // Editor.STEP):
                self.grid_layer.fill_style = "#252525"
                self.grid_layer.fill_rect(i * Editor.STEP, j * Editor.STEP, 1)

    def draw_component(self, component: Component, layer: canvas.Canvas = None):
        """
        Draws a single component on a canvas.

        Paramaters
        ----------

        component: Component
            The component to draw.

        layer: Canvas = None
            Layer to draw component on,
            if none specified it will draw on the component layer.
        """

        if layer is None:
            layer = self.component_layer

        match component.type:
            case Component.W: # Wires

                start_x, start_y = component.ports[0].position
                end_x, end_y = component.ports[1].position

                with canvas.hold_canvas():
                    layer.stroke_style = "#252525"
                    layer.stroke_line(start_x, start_y, end_x, end_y)

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

            self.draw_component(component, layer)