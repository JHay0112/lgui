
from .component import Component

class Ground(Component):
    """
    Ground Flag
    """
    
    def __init__(self):

        super().__init__(None)

    def __draw_on__(self, editor, layer):
        pass

    def draw_on(self, editor, layer):
        # no graphical representation
        pass

    