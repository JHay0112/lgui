from math import sqrt, degrees, atan2


class Components(list):

    def __init__(self):

        super(Components, self).__init__(self)
        self.kinds = {}

    def add(self, cpt):

        self.append(cpt)

    def add_auto(self, cpt, *nodes):

        if cpt.TYPE not in self.kinds:
            self.kinds[cpt.TYPE] = 0
        self.kinds[cpt.TYPE] += 1

        # Hack, update component class to have this attribute
        cpt.cname = cpt.TYPE + '%d' % self.kinds[cpt.TYPE]

        # Hack for drawing
        cpt.nodes = nodes
        cpt.ports[0].position = nodes[0].position
        cpt.ports[1].position = nodes[1].position

        self.add(cpt)

    def clear(self):

        while self != []:
            # TODO erase component
            self.pop()

    def debug(self):

        s = ''
        for cpt in self:
            # Need to redo Component class to show node names as well.
            s += str(cpt) + '\n'
        return s

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
