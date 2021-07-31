import threading,subprocess
import queue
import time


class Connector:
    def signalRead(self,string):pass
    def __init__(self,ip,protocol='ssh',username=None,password=None,**kw):
        self.protocol,self.username,self.password,self.ip=protocol,username,password,ip
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()
        self.writeLoopSpeed=0.01#seconds = 1msec
        self.restartSession()
        time.sleep(0.5)
        self.idleTimer=threading.Timer(300,lambda: self.slotSend(b' '))
        self.idleTimer.start()
    def destroy(self,event=None):
        self.queueLoop_timer.cancel()
        self.idleTimer.cancel()
        self.alive=False
        self.p.terminate()
    def readFromProccessOut(self):
        while self.alive:
            data = self.p.stdout.raw.read(1024)#.decode()
            if data==b'':self.alive=0
            self.outQueue.put(data)
    def readFromProccessErr(self):
        while self.alive:
            data = self.p.stderr.raw.read(1024)#.decode()
            if data==b'':self.alive=0
            #if self.p.poll()==0:self.alive=0
            self.errQueue.put(data)

    def queueLoop(self,s=b''):
        if not self.errQueue.empty():
            self.readFromQueue(self.errQueue.get())
        if not self.outQueue.empty():
            self.readFromQueue(self.outQueue.get())
            self.writeLoopSpeed=0.0001
        elif self.writeLoopSpeed<1:
            self.writeLoopSpeed+=0.001
        if self.p.poll()==0:self.alive=False
        if self.alive:
            self.queueLoop_timer=threading.Timer(self.writeLoopSpeed,self.queueLoop)
            self.queueLoop_timer.start()
    def readFromQueue(self,string):
        self.signalRead(string)
    def restartSession(self):
        try:self.destroy()
        except:pass
        self.outQueue.empty()
        self.errQueue.empty()
        if self.protocol=='ssh' and self.username!=None and self.password!=None:
            self.p=subprocess.Popen(["plink",'-ssh','-l',self.username,'-pw',self.password,self.ip],\
                                 stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        elif self.protocol=='telnet':
            self.p=subprocess.Popen(["plink",'-telnet',self.ip],\
                                 stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        else: pass
        if self.p.poll()!=0:
            self.alive = True
            threading.Thread(target=self.readFromProccessOut,daemon=True).start()
            threading.Thread(target=self.readFromProccessErr,daemon=True).start()
        #self.status.set('Connected')
        if self.alive:
            self.queueLoop_timer=threading.Timer(0.1,self.queueLoop)
            self.queueLoop_timer.start()
    def slotSend(self,byteString):
        if self.alive==False:self.restartSession()
        if self.alive==True:
            #print('send--->',byteString)
            self.p.stdin.write(byteString)
            self.p.stdin.flush()
            self.idleTimer.cancel()
            self.idleTimer=threading.Timer(300,lambda: self.slotSend(b' '))
            self.idleTimer.start()


if __name__ == '__main__':
    import tkinter as tk
    root=tk.Tk()
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)
    tty=tk.Text(root,font='Terminal 8',width=100)
    tty.grid(row=0,column=0,sticky='NEWS')
    root.event_add('<<1>>','<1>','<Motion>','<ButtonRelease-1>')
    def test(e):
        root.focus_set()
        return 'break'
    tty.bind('<<1>>',test)
    ssh=Connector('192.168.0.103',username='q',password='q1')
    ssh.signalRead=lambda s: [tty.insert('insert',s),tty.see('end')]
    root.bind('<Key>',lambda e: ssh.slotSend(e.char.encode()))
    threading.Timer(1,ssh.slotSend,args=(b'ls\rps -ef\r',)).start()

    root.mainloop()
    ssh.signalRead=lambda s: None
    ssh.destroy()
