"""
Defines the component editor class.
"""

import lcapy
import ipywidgets as widgets
import ipycanvas as canvas

from .sheet import Sheet

@widgets.register
class Editor(canvas.Canvas):
    """
    The component editor is an ipywidget.
    """

    SCALE = 0.1
    HEIGHT = 500
    WIDTH = 800

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)

        super().__init__(width = Editor.WIDTH, height = Editor.HEIGHT)

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
        return canvas.hold_canvas(self)

    def draw_components(self):
        """Draws sheet components on canvas"""
        with self.hold():
            for component in self.sheet.components:
                with open(component.img_path(), "rb") as f:
                    image = widgets.Image(value = f.read(), format = component.IMG_EXT)
                self.draw_image(image, 
                    component.position[0], 
                    component.position[1], 
                    int(component.IMG_WIDTH * Editor.SCALE), 
                    int(component.IMG_HEIGHT * Editor.SCALE)
                )
