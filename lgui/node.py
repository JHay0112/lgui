from .components import Port


class Node:

    def __init__(self, x, y, name):

        self.x = x
        self.y = y
        self.name = name
        self.count = 0
        self.cpts = []

    @property
    def position(self):

        return self.x, self.y

    @position.setter
    def position(self, pos):

        self.x = pos[0]
        self.y = pos[1]

    def __str__(self):

        x = str(self.x).rstrip('0').rstrip('.')
        y = str(self.y).rstrip('0').rstrip('.')

        return '%s@(%s, %s)' % (self.name, x, y)

    @property
    def is_primary(self):

        name = self.name
        parts = name.split('_')
        return (name[0] != '_' and len(parts) <= 2) \
            and not (name[0].isdigit() and len(parts) != 1)

    @property
    def port(self):

        for cpt in self.cpts:
            if isinstance(cpt, Port):
                return True
        return False

    def debug(self):

        s = str(self) + ', count=%s' % self.count

        cnames = [cpt.cname for cpt in self.cpts]

        s += ', cpts=[%s]' % ', '.join(cnames) + '\n'

        return s
