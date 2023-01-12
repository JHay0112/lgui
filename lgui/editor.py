"""
Defines the component editor class.
"""

import lcapy
import ipywidgets as widgets
import ipycanvas as canvas

from .sheet import Sheet

@widgets.register
class Editor(canvas.MultiCanvas):
    """
    The component editor is an ipywidget.
    """

    SCALE = 0.25
    HEIGHT = 1000
    WIDTH = 2000
    LAYERS = 2

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)

        super().__init__(Editor.LAYERS, width = Editor.WIDTH, height = Editor.HEIGHT)

        self.foreground = self[0]
        self.background = self[1]

        self.layout.width = "100%"
        self.layout.height = "auto"

    def hold(self):
        """
        Context manager that buffers canvas commands.
        Canvas commands are executed once hold has passed.

        Example
        -------
        ```
        >>> editor = Editor()
        >>> with editor.hold():
        >>>     ... # canvas commands
        >>> # canvas commands are executed upon exit of context
        ```
        """
        return canvas.hold_canvas()

    def draw_components(self):
        """Draws sheet components on canvas"""
        with self.hold():
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
