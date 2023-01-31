class Annotations(list):

    def __init__(self):

        super(Annotations, self).__init__(self)

    def add(self, annotation):

        self.append(annotation)

    def remove(self):

        while self != []:
            self.pop().remove()
