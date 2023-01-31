from tkinter import Tk, Text, END


class MessageDialog:

    def __init__(self, message):

        self.master = Tk()

        text = Text(self.master)
        text.pack()

        text.insert(END, message)
