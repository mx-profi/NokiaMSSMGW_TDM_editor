# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import askyesno
import re,random









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
    def add_tab(self,frame,sessionName):
        self.notebook.add(frame,text=sessionName)
        self.notebook.select(self.notebook.tabs()[-1])
        self.frames.append(frame)












class SessionEditor(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        self.master=master
        self.rowconfigure(19,weight=1)
        self.columnconfigure(0,weight=1)
        self.treeView=ttk.Treeview(self,columns=('group','session','ip','protocol','type','username','password'),displaycolumns=(2,3,4,5))
        self.treeView.grid(row=0,column=0,rowspan=20,sticky=tk.N+tk.E+tk.S+tk.W)
        self.treeView.heading('#0',text='session')
        self.treeView.heading('#1',text='ip address')
        self.treeView.heading('#2',text='protocol')
        self.treeView.heading('#3',text='type')
        self.treeView.heading('#4',text='username',anchor='w')
        self.treeView.column('#0',width=200,stretch=False,anchor='w')
        self.treeView.column('#1',width=100,stretch=False,anchor='w')
        self.treeView.column('#2',width=70,stretch=False,anchor='c')
        self.treeView.column('#3',width=70,stretch=False,anchor='c')
        self.treeView.column('#4',width=100,stretch=True)
        tk.Label(self,text='group:',width=9,anchor='e').grid(row=1,column=1)
        tk.Label(self,text='session:',width=9,anchor='e').grid(row=2,column=1)
        tk.Label(self,text='ip:',width=9,anchor='e').grid(row=3,column=1)
        tk.Label(self,text='protocol:',width=9,anchor='e').grid(row=4,column=1)
        tk.Label(self,text='type:',width=9,anchor='e').grid(row=5,column=1)
        tk.Label(self,text='username:',width=9,anchor='e').grid(row=6,column=1)
        tk.Label(self,text='password:',width=9,anchor='e').grid(row=7,column=1)
        group,session,ip,protocol,type,username,password=[tk.StringVar() for i in range(7)]
        tk.Entry(self,textvariable=group).grid(row=1,column=2)
        tk.Entry(self,textvariable=session).grid(row=2,column=2)
        tk.Entry(self,textvariable=ip).grid(row=3,column=2)
        tk.OptionMenu(self,protocol,'ssh','telnet').grid(row=4,column=2)
        tk.OptionMenu(self,type,'mgw','mss').grid(row=5,column=2)
        tk.Entry(self,textvariable=username).grid(row=6,column=2)
        tk.Entry(self,textvariable=password,show='*').grid(row=7,column=2)

        self.treeView.tag_bind('group','<1>',lambda e: [group.set(self.treeView.item(self.treeView.identify_row(e.y),option='text'))])
        self.treeView.tag_bind('session','<1>',lambda e:\
            [group.set(self.treeView.item(self.treeView.identify_row(e.y),option='values')[0]),
             session.set(self.treeView.item(self.treeView.identify_row(e.y),option='values')[1]),
             ip.set(self.treeView.item(self.treeView.identify_row(e.y),option='values')[2]),
             protocol.set(self.treeView.item(self.treeView.identify_row(e.y),option='values')[3]),
             type.set(self.treeView.item(self.treeView.identify_row(e.y),option='values')[4]),
             username.set(self.treeView.item(self.treeView.identify_row(e.y),option='values')[5]),
             password.set(self.treeView.item(self.treeView.identify_row(e.y),option='values')[6]),
             ])
        def save_only_username_password():
            selected=self.treeView.selection()
            for iid in selected:
                if self.treeView.item(iid,option='tags')[0]!='session':continue
                group1,name1,ip1,protocol1,type1,*others=self.treeView.item(iid,option='values')
                sessions=eval(open('sessions.txt').read())
                sessions[group1][name1]=[ip1,protocol1,type1, cipher(username.get()),cipher(password.get())]
                print(str(sessions).replace('{','{\n').replace('},','},\n').replace('],','],\n\t\t'),file=open('sessions.txt.','w'))
            self.update_treeView(*selected)
        def save_session():
            if [x.get()!='' for x in (group,session,ip,protocol,type,username,password)]!=[True for i in range(7)]:
                master.status.set('Warning: Not saved, because there are empty fields!!!')
                return
            sessions=eval(open('sessions.txt').read())
            sessions[group.get()][session.get()]=[x.get() for x in (ip,protocol,type)]+[cipher(username.get()),cipher(password.get())]
            print(str(sessions).replace('{','{\n').replace('},','},\n').replace('],','],\n\t\t'),file=open('sessions.txt.','w'))
            master.status.set('Saved to sessions.txt')
            self.update_treeView(group.get()+session.get())
        def save_group():
            if group.get()=='':return
            sessions=eval(open('sessions.txt').read())
            try: sessions[group.get()]
            except: sessions[group.get()]={}
            print(str(sessions).replace('{','{\n').replace('},','},\n').replace('],','],\n\t\t'),file=open('sessions.txt.','w'))
            self.update_treeView()
        def delete_session():
            sessions=eval(open('sessions.txt').read())
            for iid in self.treeView.selection():
                g,s=self.treeView.item(iid,option='values')[:2]
                sessions[g].pop(s)
            print(str(sessions).replace('{','{\n').replace('},','},\n').replace('],','],\n\t\t'),file=open('sessions.txt.','w'))
            try:
                prev=self.treeView.prev(self.treeView.selection()[0])
                self.update_treeView(prev)
            except: self.update_treeView()
        def delete_group():
            sessions=eval(open('sessions.txt').read())
            for iid in self.treeView.selection():
                g=self.treeView.item(iid,option='text')
                sessions.pop(g)
            print(str(sessions).replace('{','{\n').replace('},','},\n').replace('],','],\n\t\t'),file=open('sessions.txt.','w'))
            self.update_treeView()
        tk.Button(self,text='add session',command=save_session).grid(row=8,column=2)
        tk.Button(self,text='add group',command=save_group).grid(row=8,column=1)
        tk.Button(self,text='delete group',command=delete_group).grid(row=9,column=1)
        tk.Button(self,text='delete session',command=delete_session).grid(row=9,column=2)
        tk.Button(self,text='set only username and password',command=save_only_username_password).grid(row=11,column=1,columnspan=2)
        self.update_treeView()
    def update_treeView(self,*current_items):
        self.treeView.delete(*self.treeView.get_children())
        sessions=eval(open('sessions.txt').read())
        group_keys=list(sessions.keys())
        group_keys.sort()
        for group in group_keys:
            self.treeView.insert('','end',iid=group,text=group,tags=('group'))
            session_keys=list(sessions[group])
            session_keys.sort()
            for name in session_keys:
                ip,protocol,type,username,password=sessions[group][name]
                username,password=decipher(username),decipher(password)
                self.treeView.insert(group,'end',iid=group+name,text=name,tags=('session',type),values=(group,name,ip,protocol,type,username,password))
        self.treeView.selection_set()
        for current_item in current_items:
            self.treeView.see(current_item)
            self.treeView.selection_add(current_item)








class Status(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        self.configure(height=20)
        self.label=tk.Label(self)
        self.label.grid(row=0,column=0)
    def set(self,message=None):
        self.message=message
        self.label.configure(text=self.message)
        self.label.update()
    def append(self,s):
        self.message+=s
        self.label.configure(text=self.message)
        self.label.update()








class Menu(tk.Menu):
    def on_File_Sessions(self):pass
    def on_Action_MGW_CGR(self):pass
    def on_Action_CGR(self):pass
    def on_Action_ETSTATE(self):pass
    def on_Action_MGW_Signalling(self):pass
    def on_Action_MSSMGW(self):pass
    def __init__(self,master):
        tk.Menu.__init__(self,master)
        mFile=tk.Menu(self,tearoff=0)
        mFile.add_command(label=' Sessions ', command=lambda:self.on_File_Sessions())
        mFile.add_command(label=' Exit ',command=master.quit)
        mHelp=tk.Menu(self,tearoff=0)
        mHelp.add_command(label=' About ',command=lambda:about_window(master))
        mAction=tk.Menu(self,tearoff=0)
        mAction.add_command(label=' ET State ',command=lambda: self.on_Action_ETSTATE())
        mAction.add_command(label=' MGW Signalling ',command=lambda: self.on_Action_MGW_Signalling())
        #mAction.add_command(label=' Ater ', command=lambda: self.on_Action_MGW_CGR())
        #mAction.add_command(label=' CGR ',command=lambda: self.on_Action_CGR())
        mAction.add_command(label=' MSS and MGW Circuits ',command=lambda: self.on_Action_MSSMGW())
        self.add_cascade(label='File',menu=mFile)
        self.add_cascade(label='Action',menu=mAction)
        self.add_cascade(label='Help',menu=mHelp)




def about_window(master):
    window=tk.Toplevel(master)
    window.title('О программе')
    g,x,y=master.geometry().split('+')
    x,y,w,h=int(x),int(y),int(g.split('x')[0]),int(g.split('x')[1])
    w1,h1=600,150
    window.geometry(newGeometry='%sx%s+%s+%s'%(w1,h1,x+int(w/2-w1/2),y+int(h/2-h1/2)))
    window.transient(master)
    window.columnconfigure(0,weight=1)
    AboutWindowText='\nПозволяет работать с:\n ЕТ - lock,unlock,framing, обновлять состояние, показывать только выбранные ЕТ;\nMGW cигнализация - смотреть и менять точки,линки,линксеты,руты;\nMSS,MGW каналы - все возможные действия отображаются при нажатии правой кнопкой мыши;\nВозможность работать сразу с неcксолькими позициями(PCM,ET).'
    label=tk.Label(window,text=AboutWindowText,anchor=tk.CENTER)
    label.grid(row=0,column=0,sticky=tk.W+tk.E)
    window.focus_set()








def cipher(string):
    string=string.encode('UTF-8')
    s=b''
    for i in string:
        r=int(random.random()*110)
        s+=bytes([i+r,r])
    return s.hex()
def decipher(cipheredString):
    string=bytes().fromhex(cipheredString)
    s=b''
    for i in range(0,len(string),2):
        s+=bytes([string[i]-string[i+1]])
    return s.decode('UTF-8')