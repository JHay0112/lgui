from math import sqrt, degrees, atan2


class Components(list):

    def __init__(self):

        super(Components, self).__init__(self)
        self.kinds = {}

    def add(self, cpt, name, *nodes):

        if cpt.TYPE not in self.kinds:
            self.kinds[cpt.TYPE] = []
        self.kinds[cpt.TYPE].append(name)

        # Hack, update component class to have this attribute
        cpt.cname = name

        # Hack for drawing
        cpt.nodes = nodes
        cpt.ports[0].position = nodes[0].position
        cpt.ports[1].position = nodes[1].position

        self.append(cpt)

    def add_auto(self, cpt, *nodes):
        """Enumerate component before adding."""

        if cpt.TYPE not in self.kinds:
            name = cpt.TYPE + '1'
        else:
            num = 1
            while True:
                name = cpt.TYPE + str(num)
                if name not in self.kinds[cpt.TYPE]:
                    break
                num += 1

        self.add(cpt, name, *nodes)

    def clear(self):

        while self != []:
            # TODO erase component?
            self.pop()

    def debug(self):

        s = ''
        for cpt in self:
            s += cpt.cname + ' ' + \
                ' '.join([str(node) for node in cpt.nodes]) + '\n'
        return s + '\n'

    def as_sch(self, step):

        elts = []
        for cpt in self:
            parts = [cpt.cname]
            for node in cpt.nodes:
                parts.append(node.name)

            # Later need to handle schematic kind attributes.
            if cpt.kind is not None:
                parts.append(cpt.kinds[cpt.kind])

            if cpt.value is not None:
                parts.append(cpt.value)

            if cpt.initial_value is not None:
                parts.append(cpt.initial_value)

            x1, y1 = cpt.nodes[0].position
            x2, y2 = cpt.nodes[1].position
            r = sqrt((x1 - x2)**2 + (y1 - y2)**2) / step

            if r == 1:
                size = ''
            else:
                size = '=%s' % r

            if y1 == y2:
                if x1 > x2:
                    attr = 'left' + size
                else:
                    attr = 'right' + size
            elif x1 == x2:
                if y1 > y2:
                    attr = 'down' + size
                else:
                    attr = 'up' + size
            else:
                angle = degrees(atan2(y2 - y1, x2 - x1))
                attr = 'rotate=%s' % angle

            # Add user defined attributes such as color=blue, thick, etc.
            if cpt.attrs != '':
                attr += ', ' + cpt.attrs

            parts.append('; ' + attr)

            elts.append(' '.join(parts))
        return '\n'.join(elts) + '\n'

    def closest(self, x, y):

        for cpt in self:
            x1, y1 = cpt.nodes[0].position
            x2, y2 = cpt.nodes[1].position
            xmid = (x1 + x2) / 2
            ymid = (y1 + y2) / 2
            rsq = (xmid - x)**2 + (ymid - y)**2
            ssq = (x2 - x1)**2 + (y2 - y1)**2
            if rsq < 0.1 * ssq:
                return cpt
        return None

    def remove(self, cptname):

        idx = self.index(cptname)
        if idx is None:
            raise ValueError('Unknown component ' + cptname)

        cpt = self.pop(idx)

        return cpt
