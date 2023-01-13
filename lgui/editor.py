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
    LAYERS = 4
    STEP = 12
    MOVE_DELAY = 0.05

    # capture user interactions
    output = widgets.Output()

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)
        self.active_component: Component = None

        super().__init__(Editor.LAYERS, width = Editor.WIDTH, height = Editor.HEIGHT)

        self.control_layer = self[0]
        self.active_layer = self[1]
        self.component_layer = self[2]
        self.grid_layer = self[3]

        self.layout.width = "100%"
        self.layout.height = "auto"

        super().on_mouse_move(self._handle_mouse_move)
        super().on_mouse_down(self._handle_mouse_down)

        with canvas.hold_canvas():
            self.draw_grid()

        self.mouse_position = [0, 0]
        self._update_active_component()

    def _update_active_component(self):
        """
        Updates the current active component.
        """
        if self.active_component is not None:
            x, y = self.mouse_position
            self.active_component.position[0] = x - (x % Editor.STEP)
            self.active_component.position[1] = y - (y % Editor.STEP)

            with canvas.hold_canvas():
                self.active_layer.clear()
                self.draw_component(self.active_component, self.active_layer)

        threading.Timer(Editor.MOVE_DELAY, self._update_active_component).start()

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

            self.active_component.position[0] = x - (round(x) % Editor.STEP)
            self.active_component.position[1] = y - (round(y) % Editor.STEP)

            self.sheet.add_component(self.active_component)
            self.active_component = None

            with canvas.hold_canvas():
                self.component_layer.clear()
                self.draw_components()

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

        with open(component.img_path(), "rb") as f:
            image = widgets.Image(value = f.read(), format = component.IMG_EXT)

        width = int(component.IMG_WIDTH * Editor.SCALE)
        height = int(component.IMG_HEIGHT * Editor.SCALE)

        layer.draw_image(image, 
            component.position[0] - int(round((Editor.SCALE * component.IMG_WIDTH / 2))), 
            component.position[1], 
            width, 
            height
        )

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