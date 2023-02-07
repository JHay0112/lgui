from math import sqrt, degrees, atan2


class Components(list):

    def __init__(self):

        super(Components, self).__init__(self)
        self.kinds = {}

    def add(self, cpt, name, *nodes):

        if cpt.TYPE not in self.kinds:
            self.kinds[cpt.TYPE] = []
        self.kinds[cpt.TYPE].append(name)

        cpt.name = name
        cpt.value = name
        cpt.nodes = nodes

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
            s += cpt.name + ' ' + \
                ' '.join([str(node) for node in cpt.nodes]) + '\n'
        return s + '\n'

    def as_sch(self, step):

        elts = []
        for cpt in self:
            parts = [cpt.name]
            for node in cpt.nodes:
                parts.append(node.name)

            if cpt.TYPE in ('E', 'F', 'G', 'H') and cpt.control is None:
                raise ValueError(
                    'Control component not defined for ' + cpt.name)

            if cpt.TYPE in ('E', 'G'):
                idx = self.find_index(cpt.control)
                parts.append(self[idx].nodes[0].name)
                parts.append(self[idx].nodes[1].name)
            elif cpt.TYPE in ('F', 'H'):
                parts.append(cpt.control)

            # Later need to handle schematic kind attributes.
            if cpt.kind is not None and cpt.kinds[cpt.kind] != '':
                parts.append(cpt.kinds[cpt.kind])

            if cpt.TYPE not in ('W', 'P', 'O') and cpt.value is not None:
                if cpt.initial_value is None and cpt.name != cpt.value:
                    if cpt.value.isalnum():
                        parts.append(cpt.value)
                    else:
                        parts.append('{' + cpt.value + '}')

            if cpt.initial_value is not None:
                if cpt.initial_value.isalnum():
                    parts.append(cpt.initial_value)
                else:
                    parts.append('{' + cpt.initial_value + '}')

            x1, y1 = cpt.nodes[0].position
            x2, y2 = cpt.nodes[1].position
            r = sqrt((x1 - x2)**2 + (y1 - y2)**2) / step

            if r == 1:
                size = ''
            else:
                size = '=' + str(r).rstrip('0').rstrip('.')

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

            elts.append(' '.join(parts) + '; ' + attr)
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

    def find_index(self, name):

        for m, cpt in enumerate(self):
            if cpt.name == name:
                return m
        raise ValueError('Unknown component ' + name)

    def remove(self, cpt):

        idx = self.index(cpt)
        if idx is None:
            raise ValueError('Unknown component ' + cpt.name)

        cpt = self.pop(idx)

        return cpt
