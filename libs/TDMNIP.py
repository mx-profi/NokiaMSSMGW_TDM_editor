import libs.Connector
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as tkst
import threading
import queue,re,time

class TDMNIP(tk.Frame):
    def signalSend(self,cmd): print(cmd)
    def __init__(self,sessionValues,status=None):
        tk.Frame.__init__(self)
        self.values=sessionValues
        self.status=status
        self.outQueue = queue.Queue()
        self.term=libs.Connector.Connector(sessionValues[2], username=sessionValues[5], password=sessionValues[6])
        self.term.signalRead=lambda string:self.slotRead(string)
        self.signalSend=lambda cmd: self.term.slotSend(cmd)
        self.lastString=b''
        self.query=[]
        self.sendCmd=[]
        self.readResult=[]

        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        style=ttk.Style()
        style.configure('s1.Treeview',font=('monospace','12'))
        self.treeView=ttk.Treeview(self,style='s1.Treeview',columns=\
            ('apcm0','apcm1','apcm2','apcm3','pool0','pool1','pool1','pool3',''),displaycolumns=(0,1,2,3,4,5,6,7,8))
        self.treeView.grid(row=0,column=0,columnspan=10,sticky='NEWS')
        tk.Button(self,text='SDH_hierarchy',command=self.show_tdm_sdh_hierarchy).grid(row=1,column=1)
        tk.Button(self,text='show IPNIMP',command=self.show_ipnimp).grid(row=1,column=2)
        self.sendQueue=[]
        self.readQueue=[]
        self.readLoop(0,1)
    def show_tdm_sdh_hierarchy(self):
        print('self.show_tdm_sdh_hierarchy()=',self.query)
        if len(self.query)==2:
            s=self.query[1]
            self.query=[]
            for s in s.split(b'SDH hierarchy information')[1:]:
                i=s.split(b'\r\n')
                sets=int(i[2].split(b'-')[1]),int(i[10].split(b'-')[1])
                tdmnips=int(i[9].split(b':')[1]),int(i[17].split(b':')[1])
                first_et,last_et=int(i[20].split(b':')[1]),int(i[21].split(b':')[1])
                print(sets,tdmnips,first_et,last_et)
            #for s in s.split(b'SDH hierarchy information')[1:]:
            #    for i in s.split(b'\r\n'):
            #        if i.find(b'peer SET-')!=-1:
            return
        if self.query==[]:
            self.query=[b'show tdm sdh hierarchy\r']
            self.signalSend(self.query[0])
        self.show_tdm_sdh_hierarchy_timer=threading.Timer(0.5,self.show_tdm_sdh_hierarchy)
        self.show_tdm_sdh_hierarchy_timer.start()
    def show_ipnimp(self):
        if self.sendQueue==[]:
            self.readQueue=[]
            self.sendQueue.append(b'show tdm sdh hierarchy\r')
            self.sendQueue.append(b'show tdm sdh set-trace all\r')
        else:
            if len(self.readQueue)!=2:
                self.status.set('error: len(self.readQueue)!=len(self.sendQueue)')
                return
            print(self.readQueue)

    def destroy(self):
        print('MGW_CGR destroy()')
        self.readLoopTimer.cancel()
        self.term.signalRead=lambda s: None
        self.term.destroy()
        tk.Frame.destroy(self)
    def readLoop(self,timer=0,timeout=10,callback=None):
        if timer==0:
            timer=0.01
            self.lastString=b''
            self.signalSend(self.sendQueue.pop())
        while not self.outQueue.empty(): self.lastString+=self.outQueue.get()
        if self.lastString[-8:]==b'--More--':
            self.signalSend(b'100000 ')
        if self.lastString.find(b'COMMAND EXECUTED')!=-1 or timeout<0:
            self.readQueue.append(self.lastString.replace(b'--More--\r',b''))
            self.lastString=b''
            if len(self.sendQueue)==0:
                callback()
                return
            else: self.signalSend(self.sendQueue.pop())
        self.readLoopTimer=threading.Timer(timer,self.readLoop,args=(timer,timeout-timer,callback))
        self.readLoopTimer.start()
    def slotRead(self,string):
        self.outQueue.put(string)