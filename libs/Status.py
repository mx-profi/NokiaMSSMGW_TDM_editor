import tkinter as tk

class Status(tk.Frame):
    def __init__(self,master=None,**kw):
        tk.Frame.__init__(self,master,**kw)
        self.configure(height=20)
        self.label=tk.Label(self,**kw)
        self.label.grid(row=0,column=0)
    def set(self,message=None):
        self.label.configure(text=message)



if __name__ == '__main__':
    root=tk.Tk()
    root.grid_propagate(0)
    root.configure(width=400,height=300)
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)
    status=Status(root)
    status.grid(row=0,column=0,sticky=tk.S+tk.E+tk.W)
    status.set('This is Status frame')
    root.mainloop()
