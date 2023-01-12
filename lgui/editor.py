"""
Defines the component editor class.
"""

import lcapy
import ipywidgets as widgets

from ipycanvas import Canvas, hold_canvas

from .sheet import Sheet

@widgets.register
class Editor(Canvas):
    """
    The component editor is an ipywidget.
    """

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)

        super().__init__(width = 1000, height = 800)