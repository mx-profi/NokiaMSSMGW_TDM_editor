import tkinter as tk

class MainMenu(tk.Menu):
    def signal_open_aboutWindow(self,master=None):pass
    def signal_open_settingsWindow(self,master=None):pass

    def __init__(self,master,**kw):
        tk.Menu.__init__(self,master,**kw)
        master['menu']=self
        self.subMenuFile=tk.Menu(self,tearoff=0)
        self.add_cascade(label='File',menu=self.subMenuFile)
        self.subMenuHelp=tk.Menu(self,tearoff=0)
        self.add_cascade(label='Help',menu=self.subMenuHelp)

        self.subMenuFile.add_command(label=' Settings ',accelerator='Ctrl-s',\
                                     command=lambda: self.signal_open_settingsWindow(master))
        self.subMenuFile.add_command(label=' Exit ',command=master.quit,accelerator='Ctrl-x')
        #master.bind_all('<Control-x>',lambda e: master.quit())
        self.subMenuHelp.add_command(label=' About ',command=lambda: self.signal_open_aboutWindow(master))


if __name__ == '__main__':
    w=tk.Tk()
    menu=MainMenu(w)
    w.mainloop()
