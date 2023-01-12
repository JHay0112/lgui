"""
Defines the component editor class.
"""

import lcapy
import ipywidgets as widgets
import ipycanvas as canvas

from .sheet import Sheet
from .components import Component

@widgets.register
class Editor(canvas.MultiCanvas):
    """
    The component editor is an ipywidget.
    """

    SCALE = 0.25
    HEIGHT = 1000
    WIDTH = 2000
    LAYERS = 2

    # capture user interactions
    output = widgets.Output()

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)
        self.active_component: Component = None

        super().__init__(Editor.LAYERS, width = Editor.WIDTH, height = Editor.HEIGHT)

        self.foreground = self[0]
        self.background = self[1]

        self.layout.width = "100%"
        self.layout.height = "auto"

        super().on_mouse_move(self._on_mouse_move)
        super().on_mouse_down(self._on_mouse_down)

    @output.capture()
    def _on_mouse_move(self, x: int, y: int):
        """
            Handles mouse movements.
            Registered with canvas in __init__
        """
        if self.active_component is not None:
            self.active_component.position = (x, y)
            with canvas.hold_canvas():
                self.clear()
                self.draw_components()

    @output.capture()
    def _on_mouse_down(self, x: int, y: int):
        """
            Handles mouse movements.
            Registered with canvas in __init__
        """
        if self.active_component is not None:
            self.active_component.position = (x, y)
            self.active_component = None
            with canvas.hold_canvas():
                self.clear()
                self.draw_components()

    def draw_components(self):
        """Draws sheet components on canvas"""
        for component in self.sheet.components:

            with open(component.img_path(), "rb") as f:
                image = widgets.Image(value = f.read(), format = component.IMG_EXT)

            width = int(component.IMG_WIDTH * Editor.SCALE)
            height = int(component.IMG_HEIGHT * Editor.SCALE)

            self.background.draw_image(image, 
                component.position[0] - int(width/2), 
                component.position[1], 
                width, 
                height
            )