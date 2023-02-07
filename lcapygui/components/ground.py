from .component import Component


class Ground(Component):
    """
    Ground Flag
    """

    # this is a possible indicator that ground should not be a component!
    # the type field makes little sense!
    TYPE = "G"
    NAME = "Ground"

    def __init__(self):

        super().__init__(None)

    def __draw_on__(self, editor, layer):
        pass

    def draw_on(self, editor, layer):
        # no graphical representation
        pass
