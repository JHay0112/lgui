class Preferences:

    def __init__(self):

        self.label_nodes = 'none'
        self.draw_nodes = 'connections'
        self.label_ids = 'true'
        self.label_values = 'true'
        self.style = 'american'

    def schematic_preferences(self):

        opts = ('draw_nodes', 'label_nodes', 'label_ids',
                'label_values', 'style')

        foo = []
        for opt in opts:
            foo.append(opt + '=' + getattr(self, opt))
        s = ', '.join(foo)
        return s
