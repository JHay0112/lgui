"""
Defines the component editor class.
"""

import ipywidgets
import lcapy

from IPython.display import SVG, display
from tempfile import NamedTemporaryFile

from .components import Component
from .sheet import Sheet

class Editor:

    """
    The component editor is an ipywidget.
    It behaves similarly to the 
    """

    def __init__(self):

        self.sheet: Sheet = Sheet("Untitled", None)

    def display(self):
        """
        Displays the editor.
        """
        netlist = self.sheet.to_lcapy()
        svg_file = NamedTemporaryFile(
            prefix = "lgui_",
            suffix = ".svg"
        )
        lcapy.Circuit("\n" + netlist).draw(
            filename = svg_file.name
        )
        display(SVG(filename = svg_file.name))
        svg_file.close()