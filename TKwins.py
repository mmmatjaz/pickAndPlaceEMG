from Tkinter import *

class IntroWin(object):

    def __init__(self):
        self.root = Tk()
        logo = PhotoImage(file="./pics/intro.gif")
        w1 = Label(self.root, image=logo).pack()
        self.root.bind('<space>', self.spaceKey)
        # frame.pack()
        #self.root.geometry('1356x654+2000+100')
        #self.root.after(500, self.later)
        self.root.mainloop()

    def spaceKey(self, event):
        self.root.destroy()

    def later(self):
        self.root.focus_force()
        self.root.geometry('1356x654+2000+100')


class PopUp(object):

    def __init__(self,title):
        self.root = Tk()
        Label(self.root,
               text=title,
               font=("Helvetica", 36),
               padx=50, pady=50).pack()
        self.root.bind('<space>', self.spaceKey)
        # frame.pack()
        #self.root.geometry('1356x654+2000+100')
        #self.root.after(500, self.later)
        self.root.mainloop()

    def spaceKey(self, event):
        self.root.destroy()

    def later(self):
        self.root.focus_force()
        self.root.geometry('1356x654+2000+100')

if __name__ == "__main__":
    IntroWin()