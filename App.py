# -*- coding: utf-8 -*-
import tkinter as tk
import Widgets
import MGWET
import MGWSIG
import MSSMGW


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('MSS MGW TDM Editor')
        self.configure(width=1200,height=600)
        self.grid_propagate(0)
        #self.sessions=eval(re.split('</?Sessions>',open('settings.txt').read())[1])
        self.sessions=eval(open('sessions.txt').read())
        self.createWidgets()
    def destroy(self):
        tk.Tk.destroy(self)
    def createWidgets(self):
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.status=Widgets.Status(self)
        self.status.grid(row=1,column=0,columnspan=2,sticky=tk.W+tk.S+tk.E)
        self.status.set('Select File->Sessions and setup Sessions including Username and Password ')
        self.notebook=Widgets.Notebook(self)
        self.notebook.grid(row=0,column=0,sticky=tk.W+tk.N+tk.S+tk.E)
        menu=Widgets.Menu(self)
        self['menu']=menu
        menu.on_File_Sessions=lambda: self.notebook.add_tab(Widgets.SessionEditor(self),'sessions')
        #menu.on_File_Sessions()
        menu.on_Action_ETSTATE=lambda: self.notebook.add_tab(MGWET.ETSTATE(self),'ET State')
        menu.on_Action_MGW_Signalling=lambda: self.notebook.add_tab(MGWSIG.Signalling(self),'MGW Signalling')
        #menu.on_Action_MGW_CGR=lambda: self.notebook.add_tab(MGW.MGW_CGR(self),'MGW_Ater')
        #menu.on_Action_CGR=lambda: self.notebook.add_tab(MGW.CGR(self),'MGW_CGR')
        menu.on_Action_MSSMGW=lambda: self.notebook.add_tab(MSSMGW.MSSMGW(self),'MSSMGW')
        #menu.on_Action_ETSTATE()
        #menu.on_Action_CGR()
        #menu.on_Action_MGW_CGR()





if __name__ == '__main__':
    app=App()
    app.mainloop()
