import libs.Connector
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as tkst
import threading,time
import queue


class MGW_CGR(tk.Frame):
    def signalSend(self,cmd): print(cmd)
    def __init__(self,sessionValues,status=None):
        tk.Frame.__init__(self)
        self.values=sessionValues
        self.status=status
        self.outQueue = queue.Queue()

        self.f=open('test.txt','w')
        self.lastString,self.readMoreFlag=b'',True
        self.query=[]
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        #self.columnconfigure(10,weight=1)
        #self.columnconfigure(1,weight=1)


        style=ttk.Style()
        style.configure('s1.Treeview',font=('monospace','12'))
        self.treeView=ttk.Treeview(self,style='s1.Treeview',columns=\
            ('apcm0','apcm1','apcm2','apcm3','pool0','pool1','pool1','pool3',''),displaycolumns=(0,1,2,3,4,5,6,7,8))
        self.treeView.grid(row=0,column=0,columnspan=10,sticky='NEWS')
        self.treeView.heading('#0',text='et')
        self.treeView.heading('#1',text='apcm0')
        self.treeView.heading('#2',text='apcm1')
        self.treeView.heading('#3',text='apcm2')
        self.treeView.heading('#4',text='apcm3')
        self.treeView.heading('#5',text='p0')
        self.treeView.heading('#6',text='p1')
        self.treeView.heading('#7',text='p2')
        self.treeView.heading('#8',text='p3')
        self.treeView.column('#0',anchor='center',width=120,stretch=False)
        self.treeView.column('#1',anchor='center',width=60,stretch=False)
        self.treeView.column('#2',anchor='center',width=60,stretch=False)
        self.treeView.column('#3',anchor='center',width=60,stretch=False)
        self.treeView.column('#4',anchor='center',width=60,stretch=False)
        self.treeView.column('#5',anchor='center',width=30,stretch=False)
        self.treeView.column('#6',anchor='center',width=30,stretch=False)
        self.treeView.column('#7',anchor='center',width=30,stretch=False)
        self.treeView.column('#8',anchor='center',width=30,stretch=False)

        #self.listbox=ttk.Treeview(self,style='s1.Treeview',columns=('1','2','3'),displaycolumns=(0))
        #self.listbox.grid(row=0,column=10,columnspan=10,sticky='NEWS')

        self.button1=tk.Button(self,text='TCSMs',command=self.getAllTCSM)
        self.button1.grid(row=1,column=1)
        tk.Button(self,text='CGRbyTCSM',command=lambda: self.getCGRbyAPCM(self.treeView.selection())).grid(row=1,column=2)
        tk.Button(self,text='show',command=lambda: [self.treeView.detach(*self.treeView.selection()),\
                                                    [self.treeView.move(iid,'','end') for iid in self.iids]]).grid(row=1,column=3)

        #threading.Timer(0.1,self.readMore).start()
        self.treeView.tag_bind('ater','<space>',lambda e:self.getCGRbyAPCM(self.treeView.selection()))
        self.getAllTCSM_timer=threading.Timer(1,lambda :None)
        self.readMore_timer=threading.Timer(1,lambda :None)
        self.query_timer=threading.Timer(8,lambda: [self.button1['state']==tk.DISABLED and self.query.clear(),\
                                                self.button1.configure(state=tk.NORMAL)])
        self.loop_flag=True
        threading.Thread(target=self.loop,daemon=True).start()
    def loop(self):
        self.term=libs.Connector.Connector(sessionValues[2], username=sessionValues[5], password=sessionValues[6])
        self.term.signalRead=lambda string:self.slotRead(string)
        self.signalSend=lambda cmd: self.term.slotSend(cmd)
        query=None
        s=b''
        while self.loop_flag==True:
            if len(self.query)>0:
                query=self.query.pop(0)
                self.signalSend(query[0])
                s=b''
            while query!=None and self.loop_flag==True:
                while not self.outQueue.empty(): s+=self.outQueue.get()
                if s[-8:]==b'--More--':
                    s=s[:-8]
                    self.signalSend(b'10000 ')
                if s.find(b'COMMAND EXECUTED')!=-1:
                    threading.Thread(target=query[1],args=(query[0],s),daemon=True).start()
                    query=None
            time.sleep(0.1)
    def getAllTCSM(self,cmd=None,res=None):
        if cmd==None:
            self.query.append([b'show tdm ater\r',self.getAllTCSM])
            return
        else:
            print(res)
            return

        if len(self.query)==0:
            if self.status!=None: self.status.set('[%s] executing "show tdm ater"'%self.values[1])
            self.query=[b'show tdm ater\r']
            self.signalSend(self.query[0])
            threading.Thread(target=self.getAllTCSM,daemon=True).start()
            '''self.readMore_timer=threading.Timer(0.5,self.readMore,args=(0.01,))
            self.readMore_timer.start()
            self.query_timer.cancel()
            self.query_timer=threading.Timer(8,lambda: [self.button1['state']==tk.DISABLED and self.query.clear(),\
                                                self.button1.configure(state=tk.NORMAL)])
            self.query_timer.start()
            self.button1.configure(state=tk.DISABLED)'''
        elif len(self.query)==2 and self.query[0]==b'show tdm ater\r':
            self.query_timer.cancel()
            self.treeView.delete(*self.treeView.get_children())
            if self.query[0]==b'show tdm ater\r':
                s=self.query[1]
                self.query=[]
                s=s.decode().replace('\r\n\r','\r\n')
                ET={}
                APCM={}
                for i in s.split('\r\n'):
                    if i[26:28]=='16':
                        apcm=int(i[:5])
                        et=int(i[10:14].strip())
                        tcpcm=int((int(i[16:21].split('-')[0].strip())-1)/8)
                        pool=int(i[36:38])
                        ET[et]={}
                        APCM[apcm]=[et,tcpcm,pool]
                    else: pass
                for apcm in APCM:
                    et,tcpcm,pool=APCM[apcm]
                    ET[et][tcpcm]=[apcm,pool]
                sET=list(ET.keys())
                sET.sort()
                #self.winfo_toplevel().iconify()
                self.treeView.insert('','end',text='count=%s'%len(ET))
                for et in sET:
                    s=['-','-','-','-','-','-','-','-']
                    for tcpcm in ET[et]: s[tcpcm],s[tcpcm+4]=ET[et][tcpcm]
                    #self.treeView.insert('','end',iid=et,text=et,values=(s),tags=('ater'))
                    print(et,s)
                for line in open('Test1/a.txt'):
                    print(line)
                    self.treeView.insert('','end',text=line)
                #self.winfo_toplevel().deiconify()
            if self.status!=None: self.status.set('')
            self.button1.configure(state=tk.NORMAL)
            return
        self.getAllTCSM_timer=threading.Timer(0.5,self.getAllTCSM)
        self.getAllTCSM_timer.start()
    def getCGRbyAPCM(self,iids=()):
        iids=list(iids)
        for iid in iids:
            print(self.treeView.item(iid))
        '''if len(iids)>0:
            #iid=iids.pop(0)
            #print(self.treeView.item(iid))
            #print(iids)
            self.iids=self.treeView.get_children()
            self.treeView.detach(*self.treeView.get_children())
            print(self.treeView.get_children())
            for iid in iids: self.treeView.move(iid,'','end')
            #threading.Timer(0.1,self.getCGRbyAPCM,args=(iids,)).start()'''
    def destroy(self):
        print('MGW_CGR destroy()')
        self.loop_flag=False
        self.query_timer.cancel()
        self.getAllTCSM_timer.cancel()
        self.readMore_timer.cancel()
        self.readMoreFlag=False
        self.term.signalRead=lambda s: None
        self.term.destroy()
        tk.Frame.destroy(self)
    def readMore(self,timer=1):
        if self.lastString==b'' and timer<0.5: timer+=0.01
        while not self.outQueue.empty(): self.lastString+=self.outQueue.get()
        if self.lastString[-8:]==b'--More--':
            print(self.lastString)
            print('----More-----')
            self.lastString=self.lastString[:-8]
            self.signalSend(b'10000 ')
            timer=0.001
        if self.lastString.find(b'COMMAND EXECUTED')!=-1:
            self.query.append(self.lastString)
            self.lastString=b''
            return
        if self.readMoreFlag==True:
            self.readMore_timer=threading.Timer(timer,self.readMore,args=(timer,))
            self.readMore_timer.start()
    def slotRead(self,string):
        #print('slotRead->>',string)
        self.outQueue.put(string)
