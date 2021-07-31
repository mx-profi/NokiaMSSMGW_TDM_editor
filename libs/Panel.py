import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import askyesno
import re,random



class Panel(tk.Frame):
    #def signalDoubleClickOnSession(self,event=None):
    #    print(self.treeView.selection())

    def signalOpenSession(self,sessionName,sessionValues):
        print(sessionName,sessionValues)
    def signalOpenMGWCGREditor(self,sessionName,sessionValues):
        print('Panel.signalOpenMGWCGREditor(sessionName,sessionValues)',sessionName,sessionValues)
    def signalOpenTDMNIP(self,sessionName,sessionValues):
        print('Panel.signalOpenMGWCGREditor(sessionName,sessionValues)',sessionName,sessionValues)
    def __init__(self,master=None,**kw):
        tk.Frame.__init__(self,master)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self._settings=eval(re.split('</?Panel>',open('settings.txt').read())[1])
        self.readSessionsFromFile()
        self.createWidgets()
        self.updateTreeView(self._settings['lastSeeItemID'])

    def createWidgets(self):
        leftFrame=tk.Frame(self,width=15,bg='grey')
        leftFrame.grid(row=0,column=0,sticky=tk.W+tk.N+tk.S)
        centerFrame=tk.Frame(self,bg='red',width=self._settings['centerFrameWidth'])
        centerFrame.grid(row=0,column=1,sticky=tk.N+tk.E+tk.S+tk.W)
        centerFrame.grid_propagate(0)
        centerFrame.rowconfigure(1,weight=1)
        centerFrame.columnconfigure(0,weight=1)
        rightFrame=tk.Frame(centerFrame,width=3,cursor='sb_h_double_arrow',bg='grey')
        rightFrame.grid(row=0,column=1,rowspan=2,sticky=tk.E+tk.N+tk.S)
        topFrame=tk.Frame(centerFrame,height=20)
        topFrame.grid(row=0,column=0,sticky=tk.N+tk.W+tk.E)
        self.treeView=ttk.Treeview(centerFrame,columns=('group','session','ip','protocol','type','login','password'),displaycolumns=(2,3,4,5))
        self.treeView.grid(row=1,column=0,sticky=tk.N+tk.E+tk.S+tk.W)
        self.treeView.heading('#0',text='session')
        self.treeView.heading('#1',text='ip address')
        self.treeView.heading('#2',text='protocol')
        self.treeView.heading('#3',text='type')
        self.treeView.heading('#4',text='username')
        self.treeView.column('#0',width=self._settings['sessionColumnWidth'],stretch=False,anchor='e')
        self.treeView.column('#1',width=self._settings['ipColumnWidth'],stretch=False,anchor='e')
        self.treeView.column('#2',width=self._settings['protocolColumnWidth'],stretch=False,anchor='c')
        self.treeView.column('#3',width=self._settings['typeColumnWidth'],stretch=False,anchor='c')
        self.treeView.column('#4',width=self._settings['usernameColumnWidth'],stretch=True)
        self.treeView.tag_bind('session','<Double-1>',lambda e:\
            [self.signalOpenSession(self.treeView.item(self.treeView.selection()[0],option='values')[1],\
                                   self.treeView.item(self.treeView.selection()[0],option='values')),
             #set_settings('lastSeeItemID',self.treeView.item(self.treeView.selection()[0])['iid'])\
             ])
        self.treeView.bind('<Delete>',self.deleteSession)
        b1=tk.Button(topFrame,text='+',padx=1,pady=1,width=4,height=1,command=self.createSession)
        b2=tk.Button(topFrame,text='-',padx=1,pady=1,width=4,height=1,command=self.deleteSession)
        b1.grid(row=0,column=0)
        b2.grid(row=0,column=2)
        #make Panel resize by right frame click and motion
        rightFrame.bind('<Button-1>',lambda e: rightFrame.bind(\
            '<Motion>',lambda event: centerFrame.configure(width=centerFrame['width']+event.x)))
        def set_settings(key,value): self._settings[key]=value
        rightFrame.bind('<ButtonRelease-1>',lambda e: [rightFrame.unbind('<Motion>'),\
                                                       set_settings('centerFrameWidth',centerFrame['width'])])
        #show or hide panel by click on leftFrame
        def showhidePanel(event=None):
            if centerFrame['width']<2:centerFrame['width']=self._settings['centerFrameWidth']
            else:
                self._settings['centerFrameWidth']=centerFrame['width']
                centerFrame['width']=1
        leftFrame.bind('<1>',showhidePanel)
        #bind right click on session with sessionMenu callback function
        def itemMenu(event):
            for child in self.treeView.winfo_children():child.destroy()
            menu=tk.Menu(self.treeView,tearoff=0)
            menu.add_command(label='open terminal',command=lambda:\
                [self.signalOpenSession(self.treeView.item(iid,option='values')[1],\
                    self.treeView.item(iid,option='values')) for iid in self.treeView.selection()])
            def set_credentials(iids):
                tw=tk.Toplevel(self.winfo_toplevel())
                tw.title('Create new session')
                tw.withdraw()
                username,password=tk.StringVar(),tk.StringVar()
                tk.Label(tw,text='Username').grid(row=0,column=0)
                entryUser=tk.Entry(tw,textvariable=username)
                entryUser.grid(row=0,column=1)
                tk.Label(tw,text='Password').grid(row=1,column=0)
                tk.Entry(tw,textvariable=password,show='*').grid(row=1,column=1)
                def buttonSaveClicked():
                    for iid in iids:
                        group,session=self.treeView.item(iid,option='values')[0:2]
                        self._sessions[group][session][3]=username.get()
                        self._sessions[group][session][4]=password.get()
                    self.saveSessionsToFile()
                    self.updateTreeView(iids[0])
                tk.Button(tw,text='Save',command=buttonSaveClicked).grid(row=2,column=1)
                tw.deiconify()
                entryUser.focus_set()
                tw.wait_visibility()
                tw.wait_window()
            menu.add_command(label='set credentials',command=lambda: set_credentials(self.treeView.selection()))
            values=self.treeView.item(self.treeView.selection()[0],option='values')
            if values[4]=='mgw':
                def MGW_CGR_Editor(iids):
                    for iid in iids:
                        values=self.treeView.item(iid,option='values')
                        if values[4]!='mgw':continue
                        self.signalOpenMGWCGREditor(values[1],values)
                menu.add_command(label='CGR editor',command=lambda: MGW_CGR_Editor(self.treeView.selection()))
                def MGW_TDMNIP(iids):
                    for iid in iids:
                        values=self.treeView.item(iid,option='values')
                        if values[4]!='mgw':continue
                        self.signalOpenTDMNIP(values[1],values)
                menu.add_command(label='TDMNIP',command=lambda: MGW_TDMNIP(self.treeView.selection()))
            menu.post(event.x_root-4,event.y_root-4)
            menu.bind('<Leave>',lambda e: menu.destroy())
        self.treeView.tag_bind('session','<3>',itemMenu)

    def updateTreeView(self,iid=None):#iid - which "iid" will be see after update
        self.readSessionsFromFile()
        #clear treeView
        for group in self.treeView.get_children():
            for session in self.treeView.get_children(group):
                self.treeView.delete(session)
            self.treeView.delete(group)
        #insert data from self._session to treeView
        for group in self._sessions:
            self.treeView.insert('','end',iid=group,text=group,tags=('group','item'),values=(group,))
            for session in self._sessions[group]:
                ip, protocol, netype, username, password=self._sessions[group][session]
                self.treeView.insert(group,'end',iid=group+session,text=session,tags=('session','item',netype),\
                                     values=(group,session,ip,protocol,netype,username,password))
        #select and see active "iid"
        try:
            if self.treeView.item(iid)['tags'][0]=='session':
                self.treeView.see(iid)
                self.treeView.selection_set(iid)
                self._settings['lastSeeItemID']="'{}'".format(iid)
        except:pass

    def saveSessionsToFile(self):#save self._sessions to file "settings.txt" in tag <Sessions>
        before,sessions,after=re.split('</?Sessions>',open('settings.txt').read())
        try:
            f=open('settings.txt','w')
            print(before+'<Sessions>{\n',end='',file=f)
            groupKeys=list(self._sessions.keys())
            groupKeys.sort()
            for group in groupKeys:
                print("\t'{group}':".format(group=group)+'{\n',end='',file=f)
                sessionKeys=list(self._sessions[group])
                sessionKeys.sort()
                for session in sessionKeys:
                    v=self._sessions[group][session]
                    print("\t\t'{}':['{}','{}','{}','{}','{}'],\n".\
                          format(session,*v[:-2],self.encode(v[-2]),self.encode(v[-1])),end='',file=f)
                print("\t},\n",end='',file=f)
            print('}</Sessions>'+after,end='',file=f)
        except:
            f=open('settings.txt','w')
            f.write(before+'<Sessions>'+sessions+'</Sessions>'+after)
            f.close()
    def readSessionsFromFile(self):
        self._sessions=eval(re.split('</?Sessions>',open('settings.txt').read())[1])
        for group in self._sessions:
            for session in self._sessions[group]:
                self._sessions[group][session][-2]=self.decode(self._sessions[group][session][-2])
                self._sessions[group][session][-1]=self.decode(self._sessions[group][session][-1])

    def createSession(self): #start when you press "+" button
        #create topLevel window (tw) for create or edit session
        tw=tk.Toplevel(self.winfo_toplevel())
        tw.title('Create new session')
        tw.withdraw()
        #define variables with empty string
        group,session,ip,protocol,netype,username,password=[tk.StringVar() for i in range(7)]
        #define default values to variables
        group.set('newGroup')
        protocol.set('ssh')
        netype.set('mss')
        #set values of variables as it in selected session in treeView
        try:
            selection=self.treeView.selection()[0]
            group.set(self.treeView.item(selection)['values'][0])
            if self.treeView.item(selection)['tags'][0]=='session':
                session.set(self.treeView.item(selection)['values'][1])
                ip.set(self.treeView.item(selection)['values'][2])
                protocol.set(self.treeView.item(selection)['values'][3])
                netype.set(self.treeView.item(selection)['values'][4])
                username.set(self.treeView.item(selection)['values'][5])
                password.set(self.treeView.item(selection)['values'][6])
        except:pass
        #create widgets and connect variables to widgets
        tk.Label(tw,text='Group').grid(row=0,column=0)
        tk.Entry(tw,textvariable=group).grid(row=0,column=1,sticky=tk.W)
        if len(self._sessions)>0:tk.OptionMenu(tw,group,*self._sessions.keys()).grid(row=0,column=2,sticky=tk.W)
        else: tk.OptionMenu(tw,group,'newGroup').grid(row=0,column=2,sticky=tk.W)
        tk.Label(tw,text='Session').grid(row=1,column=0)
        tk.Entry(tw,textvariable=session).grid(row=1,column=1)
        tk.Label(tw,text='IP').grid(row=2,column=0)
        tk.Entry(tw,textvariable=ip).grid(row=2,column=1)
        tk.Label(tw,text='protocol').grid(row=3,column=0)
        tk.OptionMenu(tw,protocol,'ssh','telnet').grid(row=3,column=1,sticky=tk.W)
        tk.Label(tw,text='type').grid(row=4,column=0)
        tk.OptionMenu(tw,netype,'mss','mgw').grid(row=4,column=1,sticky=tk.W)
        tk.Label(tw,text='username').grid(row=5,column=0)
        tk.Entry(tw,textvariable=username).grid(row=5,column=1)
        tk.Label(tw,text='password').grid(row=6,column=0)
        tk.Entry(tw,textvariable=password,show='*').grid(row=6,column=1,sticky=tk.W)
        # call if "Save" button pressed
        def saveAndExit(group,session,values):
            if group.get()=='':return
            if self.treeView.item(self.treeView.selection()[0])['tags'][0]=='group':
                old_group=self.treeView.item(self.treeView.selection()[0])['values'][0]
                if self._sessions.get(group.get())==None:
                    self._sessions[group.get()]=self._sessions.pop(old_group)
                else:
                    for i in self._sessions[old_group]:
                        self._sessions[group.get()][i]=self._sessions[old_group][i]
                    self._sessions.pop(old_group)
                self.saveSessionsToFile()
                self.updateTreeView(group.get()+session.get())
                return
            if session.get()=='':return
            try:
                self._sessions[group.get()][session.get()]=[k.get() for k in values]
            except:
                self._sessions[group.get()]={}
                self._sessions[group.get()][session.get()]=[k.get() for k in values]
            self.saveSessionsToFile()
            self.updateTreeView(group.get()+session.get())
        tk.Button(tw,text='Save',command=lambda:\
            saveAndExit(group,session,(ip,protocol,netype,username,password))).grid(row=7,column=1)
        #show topLevel window
        tw.deiconify()
        tw.wait_visibility()
        tw.wait_window()

    def deleteSession(self,event=None):#start when you press "-" button
        try:
            selected_iid=self.treeView.selection()[0]
            if askyesno('Yes or No?'," Delete {}??? ".format(self.treeView.item(selected_iid)['values'][0:2])):
                values=self.treeView.item(selected_iid)['values']
                if self.treeView.item(selected_iid)['tags'][0]=='session':
                    del self._sessions[values[0]][values[1]]
                    self.treeView.delete(selected_iid)
                if self.treeView.item(selected_iid)['tags'][0]=='group' \
                        and len(self.treeView.get_children(selected_iid))==0:
                    del self._sessions[values[0]]
                    self.treeView.delete(selected_iid)
                self.saveSessionsToFile()
        except:pass
    def encode(self,string):
        string=string.encode('UTF-8')
        s=b''
        for i in string:
            r=int(random.random()*110)
            s+=bytes([i+r,r])
        return s.hex()
    def decode(self,encodedString):
        string=bytes().fromhex(encodedString)
        s=b''
        for i in range(0,len(string),2):
            s+=bytes([string[i]-string[i+1]])
        return s.decode('UTF-8')





if __name__ == '__main__':
    root=tk.Tk()
    root.grid_propagate(0)
    #root.geometry('600x400+0+0')
    panel=Panel(root)
    panel.configuration={'b':2}
    root.rowconfigure(0,weight=1)
    #root.columnconfigure(0,weight=1)
    panel.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
    root.mainloop()
