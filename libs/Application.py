import tkinter as tk
import libs.MainMenu
import libs.Status
import libs.AboutWindow
import libs.Panel
import libs.Notebook
import libs.TerminalLinux
import libs.MGW_CGR
import libs.TDMNIP
import re




class Application(tk.Tk):
    def saveSettings(self,objects):
        fileContent=open('settings.txt').read()
        for object in objects:
            ss=re.split('</?{}>'.format(object.__class__.__name__),fileContent)
            ss[0]+="<{name}>".format(name=object.__class__.__name__)+'{\n'
            ss[1]=''
            for key in object._settings:
                ss[1]+="\t'{key}':{value},\n".format(key=key,value=object._settings[key])
            ss[1]+="}"+"</{name}>".format(name=object.__class__.__name__)
            fileContent=''.join(ss)
        print(fileContent,end='',file=open('settings.txt','w'))
    def destroy(self):
        self.saveSettings((self.panel,))
        tk.Tk.destroy(self)
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('This is title')
        self.configure(width=1000,height=600)
        self.grid_propagate(0)
        self.createWidgets()
        self.create_connects()
    def createWidgets(self):
        self.rowconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.mainMenu=libs.MainMenu.MainMenu(self)
        self.status=libs.Status.Status(self,bg='green')
        self.status.grid(row=1,column=0,columnspan=2,sticky=tk.W+tk.S+tk.E)
        #self.status.set('hello world!')
        self.panel=libs.Panel.Panel(self)
        self.panel.grid(row=0,column=0,sticky=tk.W+tk.N+tk.S)
        self.notebook=libs.Notebook.Notebook(self)
        #self.notebook.add(tk.Frame(bg='grey'),text='green')
        self.notebook.grid(row=0,column=1,sticky=tk.W+tk.N+tk.S+tk.E)
    def create_connects(self):
        self.mainMenu.signal_open_aboutWindow=lambda master: [libs.AboutWindow.AboutWindow(master)]
        #self.mainMenu.signal_open_settingsWindow=lambda master: [libs.SettingsWindow.SettingsWindow(master)]
        def openSession(sessionName,sessionValues):
            if sessionValues[3]=='ssh':
                self.notebook.slot_add_tab(libs.TerminalLinux.TerminalLinux(sessionValues),sessionName)
        self.panel.signalOpenSession=openSession
        self.panel.signalOpenMGWCGREditor=lambda name,values: self.notebook.slot_add_tab(libs.MGW_CGR.MGW_CGR(values,status=self.status),name)
        self.panel.signalOpenTDMNIP=lambda name,values: self.notebook.slot_add_tab(libs.TDMNIP.TDMNIP(values,status=self.status),name)
        #self.panel.signalOpenSession=lambda sessionName,sessionValues:\
        #    self.notebook.slot_add_tab(libs.TerminalLinux.TerminalLinux(sessionValues),sessionName)




if __name__ == '__main__':
    app=Application()
    app.mainloop()
