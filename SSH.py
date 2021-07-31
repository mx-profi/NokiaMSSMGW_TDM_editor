import paramiko
import threading
import queue
import time
import telnetlib

class SSH:
    def __init__(self, hostname, username, password, port=22, ne_name=None):
        self.hostname,self.username,self.password,self.port=hostname,username,password,port
        threading.Thread(target=self.init,daemon=True).start()
        self.ne_name=ne_name
        self.Alive=False
        self.exceptError=''
        self.cmd=queue.Queue()
        self.result=queue.Queue()
    def init(self):
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=self.hostname,username=self.username,password=self.password,port=self.port)
            self.Alive=True
        except Exception as e:
            self.exceptError=e
        while self.Alive:
            if self.cmd.qsize()==0:
                time.sleep(0.2)
                continue
            while not self.result.empty():self.result.get()
            if self.username=='root':stdin, stdout, stderr = ssh.exec_command('fsclish -c "%s"'%self.cmd.get(),bufsize=65536*256)
            else: stdin, stdout, stderr = ssh.exec_command(self.cmd.get(),bufsize=65536*256)
            #time.sleep(0.5)
            s=stdout.read().decode()+stderr.read().decode()
            self.result.put(s)
        ssh.close()
    def send(self,cmd):
        if not self.Alive:
            raise RuntimeError("SSH not Alive")
            return ''
        t=time.time()
        f=open('./logs/%s_%s.txt'%(self.ne_name,time.strftime('%Y%m')),'a')
        self.cmd.put(cmd)
        print(cmd,file=f)
        while self.result.qsize()==0:
            if time.time()-t>20:
                while not self.cmd.empty():self.cmd.get()
                while not self.result.empty():self.result.get()
                raise TimeoutError("SSH timeout")
                return
            time.sleep(0.2)
        s=self.result.get()
        print(s,file=f)
        f.close()
        return s#self.result.get()
    def destroy(self):
        print('SSH->destroy()')
        self.Alive=False

class TELNET:
    def __init__(self, hostname, username, password, port=22, ne_name=None):
        self.hostname,self.username,self.password,self.port=hostname,username,password,port
        threading.Thread(target=self.init,daemon=True).start()
        self.ne_name=ne_name
        self.Alive=False
        self.exceptError=''
        self.cmd=queue.Queue()
        self.result=queue.Queue()
    def init(self):
        try:
            self.telnet=telnetlib.Telnet(self.hostname)
            self.telnet.read_until(b'< \x08',10)
            self.telnet.write(self.username.encode()+b'\r')
            self.telnet.read_until(b'< \x08',10)
            self.telnet.write(self.password.encode()+b'\r')
            self.telnet.read_until(b'< \x08',10)
            self.Alive=True
        except Exception as e:
            self.exceptError=e
            self.Alive=False
        self.run()
    def run(self):
        while self.Alive:
            if self.cmd.qsize()==0:
                time.sleep(0.2)
                continue
            try:self.telnet.write(self.cmd.get().encode()+b'\r')
            except:
                threading.Thread(target=self.init,daemon=True).start()
                time.sleep(4)
                self.telnet.write(self.cmd.get().encode()+b'\r')
            s=self.telnet.read_until(b'< \x08',40)
            self.result.put(s)
        self.telnet.close()
    def send(self,cmd):
        f=open('./logs/%s_%s.txt'%(self.ne_name,time.strftime('%Y%m')),'a')
        print(cmd,file=f)
        self.cmd.put(cmd)
        while self.result.qsize()==0: time.sleep(0.2)
        s=self.result.get().decode('utf-8')
        print(s,file=f)
        f.close()
        return s
    def destroy(self):
        print('TELNET->destroy()')
        self.Alive=False


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

def get_tsl_string(pcm,tsl_list):
    c=[tsl_list[0]]
    for i in range(1,len(tsl_list)-1):
        if tsl_list[i]-tsl_list[i-1]==1 and tsl_list[i+1]-tsl_list[i]==1:continue
        c.append(tsl_list[i])
    c.append(tsl_list[-1])
    s=[]
    if len(c)%2==1:
        if c.count(2)==0:s.append('%s-%s'%(pcm,c.pop(0)))
        else: s.append('%s-%s'%(pcm,c.pop(-1)))
    for i in range(0,len(c),2):
        s.append('%s-%s&&-%s'%(pcm,c[i],c[i+1]))
    return '&'.join(s)
def get_mgw_tsl_string(tsl_list):
    c=[tsl_list[0]]
    for i in range(1,len(tsl_list)-1):
        if tsl_list[i]-tsl_list[i-1]==1 and tsl_list[i+1]-tsl_list[i]==1:continue
        c.append(tsl_list[i])
    c.append(tsl_list[-1])
    s=[]
    if len(c)%2==1:
        if c.count(2)==0:s.append('%s'%(c.pop(0)))
        else: s.append('%s'%(c.pop(-1)))
    for i in range(0,len(c),2):
        s.append('%s-%s'%(c[i],c[i+1]))
    return ','.join(s)
