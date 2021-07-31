import tkinter as tk
import tkinter.ttk as ttk
import re
import time,sys
from SSH import *



class ETSTATE(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        self.rowconfigure(10,weight=1)
        self.columnconfigure(10,weight=1)
        self.tv=ttk.Treeview(self,columns=('Admin','Operation','Usage','Framing'),displaycolumns=(0,1,2,3))
        self.tvScroll=tk.Scrollbar(self,orient=tk.VERTICAL,command=self.tv.yview)
        self.tv.grid(row=5,column=5,columnspan=10,rowspan=10,sticky='NEWS')
        self.tvScroll.grid(row=5,column=15,rowspan=10,sticky='NSE')
        self.tv['yscrollcommand']=self.tvScroll.set
        self.tv.heading('#0',text='MGW')
        [self.tv.heading(i,text=text) for i,text in (('#1','Admin'),('#2','Operation'),('#3','Usage'),('#4','Framing'))]
        self.event_add('<<Return+1>>','<Double-1>','<Return>')
        self.status=self.nametowidget('.!status')
        self.state0()
    def all_unbind(self):
        self.tv.unbind('<<Return+1>>')
        self.tv.unbind('<3>')
    def state0(self, event=None):#show list of MGWs
        try:self.ne.destroy()
        except:pass
        self.all_unbind()
        self.tv.delete(*self.tv.get_children())
        self.tv.heading('#0',text='MGW')
        self.sessions=eval(open('sessions.txt').read())
        for mgw in self.sessions['MGWs']: self.tv.insert('','end',id=mgw,text=mgw,tags=('mgw'))
        self.tv.bind('<<Return+1>>',lambda e: threading.Thread(target=self.state1,daemon=1).start())
    def state1(self, event=None):
        self.all_unbind()
        self.tv.bind('<BackSpace>',self.state0)
        hostname,protocol,type,username,password=self.sessions['MGWs'][self.tv.selection()[0]]
        username,password=decipher(username),decipher(password)
        self.mgw_name=self.tv.item(self.tv.selection()[0],option='text')
        self.tv.delete(*self.tv.get_children())
        self.tv.heading('#0',text='ET')
        try: self.ne.destroy()
        except:pass
        self.ne=SSH(hostname,username,password,ne_name=self.mgw_name)
        t1=time.time()
        while time.time()-t1<60 and self.ne.exceptError=='' and self.ne.Alive==False: time.sleep(1)
        if self.ne.Alive==False:
            self.status.set("no connection to %s %s"%(hostname,self.ne.exceptError))
            return
        frameModes={}
        self.status.set('run command: show tdm pdh et-supervision')
        for et,framing in re.findall('\s+(\d+).{54,57} {5}(\w+).{50,54}',self.ne.send('show tdm pdh et-supervision')):
            frameModes[et]=framing
        self.all_et=[]
        self.status.set('run command: show tdm pdh et-state')
        s=self.ne.send('show tdm pdh et-state')
        self.status.set('ok')
        self.winfo_toplevel().state('iconic')
        for et,admState,operState,usage in re.findall('\s+(\d+).* (\S+).* (\S+).* (\S+)',s):
            self.all_et.append(et)
            try:self.tv.insert('','end',id=et,text=et,values=(admState,operState,usage,frameModes[et]),tags=('et'))
            except:pass
        self.winfo_toplevel().state('normal')
        def update_frame_mode(ETs):
            s=self.ne.send('show tdm pdh et-supervision et-index %s'%(','.join(ETs)))
            for et,framing in re.findall('\s+(\d+).{54,57} {5}(\w+).{50,54}',s):
                self.tv.set(et,column=3,value=framing)
        def change_frame_mode(ETs, new_frameMode):
            for et in ETs:
                self.status.set('set frame mode %s for et=%s'%(new_frameMode,et))
                self.ne.send('set tdm pdh et-supervision function-mode etsi alignment-mode %s et-index %s'%(new_frameMode,et))
                update_frame_mode((et,))
            self.status.set('ok')
        def update_et_state(ETs):
            self.status.set('updating ET state for ET=%s'%','.join(ETs))
            s=self.ne.send('show tdm pdh et-state et-index %s'%(','.join(ETs)))
            for et,admState,operState,usage in re.findall('\s+(\d+).* (\S+).* (\S+).* (\S+)',s):
                self.tv.set(et,column=0,value=admState)
                self.tv.set(et,column=1,value=operState)
                self.tv.set(et,column=2,value=usage)
            self.status.set('ok')
        def change_et_state(ETs, new_state):
            for et in ETs:
                self.status.set('set et state for et=%s'%et)
                self.ne.send('set tdm pdh et-state et-index %s admin-state %s'%(et,new_state))
                update_et_state((et,))
        def show_selected(ETs):
            self.tv.detach(*self.tv.get_children())
            for iid in ETs: self.tv.move(iid,'','end')
            self.tv.see(ETs[0])
        def submenu(event=None):
            for child in self.tv.winfo_children():child.destroy()
            menu=tk.Menu(self.tv,tearoff=0)
            menu.add_command(label='update state of selected ET',command=lambda :update_et_state(self.tv.selection()))
            menu.add_command(label='show only selected ET',command=lambda: show_selected(self.tv.selection()))
            menu.add_command(label='show all_ET',command=lambda: show_selected(self.all_et))
            menu_frameMode=tk.Menu(self.tv,tearoff=0)
            menu_frameMode.add_command(label='crc4',command=lambda : change_frame_mode(self.tv.selection(),'crc4'))
            menu_frameMode.add_command(label='dblf',command=lambda : change_frame_mode(self.tv.selection(),'dblf'))
            menu.add_cascade(label='set FrameMode',menu=menu_frameMode)
            menu_adminState=tk.Menu(self.tv,tearoff=0)
            menu_adminState.add_command(label='unlocked',command=lambda : change_et_state(self.tv.selection(),'unlocked'))
            menu_adminState.add_command(label='locked',command=lambda : change_et_state(self.tv.selection(),'locked'))
            menu.add_cascade(label='set ET state',menu=menu_adminState)
            menu.add_command(label='show MGW list',command=lambda :self.state0())
            menu.post(event.x_root,event.y_root)
        self.tv.bind('<3>',submenu)
        #self.tv.bind_all('<space>',lambda e: update_et_state(self.tv.selection()))
    def destroy(self):
        self.event_delete('<<Return+1>>')
        try:self.ne.destroy()
        except:pass
        tk.Frame.destroy(self)






