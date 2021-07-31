import tkinter as tk
import tkinter.ttk as ttk


class Notebook(tk.Frame):
    def __init__(self,master,**kw):
        tk.Frame.__init__(self,master,**kw)
        self.configure(bg='brown')
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.notebook=ttk.Notebook(self)
        self.notebook.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.notebook.bind('<3>',self.menu)
        self.frames=[]

    def menu(self,event):#delete frame
        try:
            tab="@{x},{y}".format(x=event.x,y=event.y)
            frame=self.frames.pop(self.notebook.index(tab))
            self.notebook.forget(self.notebook.index(tab))
            frame.destroy()
        except:pass
    def slot_add_tab(self,frame,sessionName):
        self.notebook.add(frame,text=sessionName)
        self.notebook.select(self.notebook.tabs()[-1])
        self.frames.append(frame)




if __name__ == '__main__':
    root=tk.Tk()
    root.grid_propagate(0)
    root.configure(width=400,height=300)
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)
    nb=Notebook(root)
    nb.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
    nb.add(tk.Frame(bg='green'),text='green')
    nb.add(tk.Frame(bg='red'),text='red')
    root.mainloop()
