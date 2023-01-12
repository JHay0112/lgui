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

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)

        super().__init__(width = 500, height = 500)

        self.draw_components()

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
                image = widgets.Image(component.svg_path())
                self.draw_image(image, component.position[0] + 250, component.position[1] + 250)
