# -*- coding: utf-8 -*-
import tkinter as tk



class AboutWindow:
    def __init__(self,master=None,*args,**kw):
        self.master=master
        self.window=tk.Toplevel(master)
        self.window.title('О программе')
        g,x,y=self.master.geometry().split('+')
        x,y,w,h=int(x),int(y),int(g.split('x')[0]),int(g.split('x')[1])
        w1,h1=300,100
        self.window.geometry(newGeometry='%sx%s+%s+%s'%(w1,h1,x+int(w/2-w1/2),y+int(h/2-h1/2)))
        self.window.transient(master)
        self.window.columnconfigure(0,weight=1)
        AboutWindowText='\nПривет\nКак дела?\nЯ думаю тебе подсказки не нужны!'
        self.label=tk.Label(self.window,text=AboutWindowText,anchor=tk.CENTER)
        self.label.grid(row=0,column=0,sticky=tk.W+tk.E)



if __name__ == '__main__':
    root=tk.Tk()
    root.after(100,lambda: AboutWindow(root))
    root.mainloop()
