from tkinter import Tk, Text, END


class MessageDialog:

    def __init__(self, message, title=''):

        self.master = Tk()
        self.master.title(title)

        text = Text(self.master)
        text.pack()

        text.insert(END, message)
