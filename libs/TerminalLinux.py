import libs.Connector
import tkinter as tk
import tkinter.scrolledtext as tkst
import threading

class TerminalLinux(tk.Frame):
    def __init__(self,sessionValues):
        tk.Frame.__init__(self)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.tty=tkst.ScrolledText(self,font='Terminal 10',wrap=tk.NONE,width=100)
        #self.tty=tk.Text(self,font='Terminal 10',width=100)
        self.tty.grid(row=0,column=0,sticky='NEWS')
        self.event_add('<<Mouse>>','<1>','<Motion>','<ButtonRelease-1>','<FocusIn>')
        def test(e):
            self.focus_set()
            return 'break'
        self.tty.bind('<<Mouse>>',test)
        self.term=libs.Connector.Connector(sessionValues[2], username=sessionValues[5], password=sessionValues[6])
        def write1(s):
            #self.tty.insert('insert',s)
            #self.tty.see('end')
            #return
            i=0
            while i<len(s):
                j=0
                if s[i]<32:
                    if s[i:i+1]==b'\x1b':
                        j+=1
                        if s[i+j:i+j+1]==b'[':
                            j+=1
                            while s[i+j]<65:
                                j+=1
                        elif s[i+j:i+j+1]==b']':
                            i=i+4
                        else:pass
                        s1=s[i:i+j+1]
                        oper=s1[-1:]
                        s1=s1[2:-1]
                        s1=b'0'+s1
                        if oper==b'm': pass
                        elif oper==b'D':
                            self.tty.mark_set(tk.INSERT,'insert - {} chars'.format(int(s1)))
                        elif oper==b'C':
                            self.tty.mark_set(tk.INSERT,'insert + {} chars'.format(int(s1)))
                        elif oper==b'A' or oper==b'E':
                            self.tty.mark_set(tk.INSERT,'insert - {} lines'.format(int(s1)))
                        elif oper==b'B' or oper==b'F':
                            self.tty.mark_set(tk.INSERT,'insert + {} lines'.format(int(s1)))
                        elif oper==b'J':
                            if int(s1)==0: self.tty.delete('insert','end')
                            elif int(s1)==2: self.tty.insert('insert',b'\n')
                            else:pass
                        elif oper==b'K':
                            if int(s1)==0: self.tty.delete('insert','insert lineend')
                            elif int(s1)==1: self.tty.delete('insert linestart','insert')
                            elif int(s1)==2: self.tty.delete('insert linestart','insert lineend')
                            else:pass
                        else:pass
                        i=i+j+1
                        continue
                    elif s[i:i+1]==b'\x08':
                        self.tty.delete('insert - 1 chars','insert')
                    elif s[i:i+1]==b'\n':
                        self.tty.insert('insert',s[i:i+1])
                    else:pass
                else: self.tty.insert('insert',s[i:i+1])
                i+=1
                self.tty.see('end')
        self.term.signalRead=write1
        def writeToTTY(string):
            #self.tty.insert('insert',string)
            #self.tty.see('end')
            if string==b'':return
            string=string.replace(b'\r',b'')
            self.lastString=string
            #string=b''.join([i[:-1] for i in string.split(b'\x08')[:-1]])+string.split(b'\x08')[-1]
            if string[0:2]==b'\x1b[':
                self.tty.tag_delete('mycursor')
                for s in string.split(b'\x1b[')[1:]:
                    print('s=',s)
                    count=0
                    for i in range(len(s)):
                        if s[i]<=57: count=count*10+(s[i]-48)
                        else: break
                    print('count=',count,s)
                    b=bytes((s[i],))
                    if b==b'J':
                        print('-->',b'J, count=',count)
                        self.tty.delete(tk.INSERT,'end'+'- 1 chars')
                    elif b==b'D':
                        print('-->',b'D, count=',count)
                        self.tty.mark_set(tk.INSERT,tk.INSERT+'- {} chars'.format(count))
                    elif b==b'C':
                        print('-->',b'C, count=',count)
                        self.tty.mark_set(tk.INSERT,tk.INSERT+'+ {} chars'.format(count))
                    elif b==b'P':
                        print('-->',b'P, count=',count)
                        self.tty.replace(tk.INSERT,tk.INSERT+'+ {} chars'.format(len(s[i+1:])),s[i+1:])
            else:
                self.tty.insert(tk.INSERT, string)
                if len(string)==1 and string!=b'\n':self.tty.delete(tk.INSERT)
            self.tty.see(tk.INSERT)
            self.tty.update()
            #self.tty.insert('insert',string)
            #self.tty.see('end')
        #self.term.signalRead=writeToTTY
        #self.term.signalRead=lambda s: [self.tty.insert('insert',s),self.tty.see('end')]
        def KeyPressed(event):
            for s in event.char:
                key=s.encode()
                if key[0]<32 and key[0]!=13 and key[0]!=8 and key[0]!=25:return
                if event.keysym=='BackSpace': key=b'\x7f'
                self.term.slotSend(key)
                return
            if event.keycode>=111 and event.keycode<=117:
                if event.keysym=='Up':key=b'\033[A'
                if event.keysym=='Down':key=b'\033[B'
                if event.keysym=='Right':key=b'\033[C'
                if event.keysym=='Left':key=b'\033[D'
                if event.keysym=='Prior':
                    self.tty.yview_scroll(-1,'pages')
                    return
                if event.keysym=='Next':
                    self.tty.yview_scroll(1,'pages')
                    return
                self.term.slotSend(key)
            return 'break'
        self.bind('<Key>',KeyPressed)#lambda e: self.term.slotSend(e.char.encode()))
        self.bind('<FocusIn>',lambda e: self.configure(bg='green'))
        self.bind('<FocusOut>',lambda e: print('focusOut'))
        print('terminalLinux: sessionValues=',sessionValues)
    def __del__(self):
        print('TerminalLinux.__del__()')
    def destroy(self):
        print('TerminalLinux destroy()')
        self.term.signalRead=lambda s: None
        self.term.destroy()
        tk.Frame.destroy(self)
