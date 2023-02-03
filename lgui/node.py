class Node:

    def __init__(self, x, y, name):

        self.x = x
        self.y = y
        self.name = name
        self.count = 0

    @property
    def position(self):

        return self.x, self.y

    def __str__(self):

        return '%s@(%s, %s)' % (self.name, self.x, self.y)
