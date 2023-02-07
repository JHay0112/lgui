from .node import Node


class Nodes(list):

    def __init__(self):

        super(Nodes, self).__init__(self)

    def add(self, node):

        if not isinstance(node, Node):
            raise TypeError('Not a Node object')

        if node not in self:
            self.append(node)

    def by_name(self, name):

        for node in self:
            if node.name == name:
                return node
        return None

    def by_position(self, position):

        x, y = position

        for node in self:
            if node.x == x and node.y == y:
                return node
        return None

    def clear(self):

        while self != []:
            self.pop()

    def closest(self, x, y):

        for node in self:
            x1, y1 = node.position
            rsq = (x1 - x)**2 + (y1 - y)**2
            if rsq < 0.1:
                return node
        return None

    def debug(self):

        s = ''
        for node in self:
            s += node.debug()
        return s

    def make(self, x, y, name, cpt):

        node = self.by_position((x, y))
        if node is not None:
            if name is not None and node.name != name:
                raise ValueError('Node name conflict %s and %s' %
                                 (node.name, name))
            node.count += 1
            node.cpts.append(cpt)
            return node

        if name is None:
            num = 1
            while True:
                name = str(num)
                if not self.by_name(name):
                    break
                num += 1

        node = Node(x, y, name)
        node.count += 1
        node.cpts.append(cpt)
        return node

    def remove(self, node, cpt):

        node.count -= 1
        if node.count == 0:
            self.pop(self.index(node))

        node.cpts.pop(node.cpts.index(cpt))
