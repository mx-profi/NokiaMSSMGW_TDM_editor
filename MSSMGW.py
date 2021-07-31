import tkinter as tk
import tkinter.ttk as ttk
import re,time,sys
from SSH import *
from tkinter.messagebox import askyesnocancel

class MSSMGW(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        self.rowconfigure(5,weight=10)
        self.rowconfigure(6,weight=3)
        #self.rowconfigure(15,weight=1)
        self.columnconfigure(5,weight=10)
        self.columnconfigure(20,weight=7)
        style=ttk.Style()
        style.configure('Treeview',font=('Terminal',14))
        self.tvmss=ttk.Treeview(self,style='Treeview')
        self.tvmgw=ttk.Treeview(self,style='Treeview')
        self.tvScrollmss=tk.Scrollbar(self,orient=tk.VERTICAL,command=self.tvmss.yview)
        self.tvScrollmgw=tk.Scrollbar(self,orient=tk.VERTICAL,command=self.tvmgw.yview)
        self.tvmss.grid(row=5,column=5,columnspan=9,sticky='NEWS')
        self.tvmgw.grid(row=5,column=16,columnspan=9,sticky='NEWS')
        self.tvScrollmss.grid(row=5,column=15,sticky='NS')
        self.tvScrollmgw.grid(row=5,column=26,sticky='NS')
        self.tvmss['yscrollcommand']=self.tvScrollmss.set
        self.tvmgw['yscrollcommand']=self.tvScrollmgw.set
        self.logmss=tk.Text(self,height=5,width=10)
        self.logmgw=tk.Text(self,height=5,width=10)
        self.logmss.grid(row=6,column=5,columnspan=11,sticky='NEWS')
        self.logmgw.grid(row=6,column=16,columnspan=11,sticky='NEWS')
        self.event_add('<<Return+1>>','<Double-1>','<Return>')
        self.status=self.nametowidget('.!status')
        self.pcm2cgr,self.pcm2Ater,self.et_state={},{},{}
        self.state0mss()
        self.state0mgw()
    def write_to_terminal(self,terminal,string):
        terminal.insert(tk.END,string)
        terminal.see(tk.END)
    def mss_unbind(self):
        self.tvmss.unbind('<<Return+1>>')
        self.tvmss.unbind('<3>')
    def mgw_unbind(self):
        self.tvmgw.unbind('<<Return+1>>')
        self.tvmgw.unbind('<3>')
    def state0mss(self):
        try: self.nemss.destroy()
        except:pass
        self.mss_unbind()
        self.tvmss.delete(*self.tvmss.get_children())
        self.tvmss.heading('#0',text='MSS')
        self.sessions=eval(open('sessions.txt').read())
        for mss in self.sessions['MSSs']: self.tvmss.insert('','end',id=mss,text=mss,tags=('mss'))
        self.tvmss.bind('<<Return+1>>',lambda e: threading.Thread(target=self.state1mss,daemon=1).start())
    def state1mss(self):
        self.mss_unbind()
        hostname,protocol,type,username,password=self.sessions['MSSs'][self.tvmss.selection()[0]]
        username,password=decipher(username),decipher(password)
        self.mss_name=self.tvmss.item(self.tvmss.selection()[0],option='text')
        self.status.set('Trying to connect to %s, ip=%s'%(self.mss_name,hostname))
        self.tvmss.heading('#0',text=self.mss_name)
        self.tvmss.delete(*self.tvmss.get_children())
        try:self.nemss.destroy()
        except:pass
        def submenu(event=None):
            for child in self.tvmss.winfo_children():child.destroy()
            menu=tk.Menu(self.tvmss,tearoff=0)
            menu.add_command(label='Show mss list',command=lambda: self.state0mss())
            tag=self.tvmss.item(self.tvmss.selection()[0],option='tags')[0]
            if tag=='dpc':
                menu.add_command(label='load circuits',command=lambda:\
                    [threading.Thread(target=self.state1mss_load_circuits,\
                                      args=(self.tvmss.selection()[0],),daemon=1).start()])
            if tag=='pcm' or tag=='cgr':
                menu.add_command(label='add pcm-tsl',command=lambda:\
                    threading.Thread(target=add_circuits,\
                                     args=(self.tvmss.item(self.tvmss.selection()[0],option='values')),\
                                     daemon=1).start())
                menu.add_command(label='add PCMs to CGRs in MSS and MGW',command=lambda: threading.Thread(target=self.add_pcms_to_cgr,daemon=1).start())
                menu.add_command(label='ZCEL:CGR=',command=lambda: threading.Thread(target=zcel_cgr,args=(self.tvmss.selection()),daemon=1).start())
            if tag=='pcm':
                menu.add_command(label='delete pcm-tsl',command=lambda:\
                    threading.Thread(target=delete_circuits,args=(self.tvmss.selection()),daemon=1).start())
                menu_state=tk.Menu(self.tvmss,tearoff=0)
                menu.add_cascade(label='change state',menu=menu_state)
                menu_state.add_command(label='WO',command=lambda: threading.Thread(target=change_circuits_state,args=(self.tvmss.selection(),'WO'),daemon=1).start())
                menu_state.add_command(label='SE',command=lambda: threading.Thread(target=change_circuits_state,args=(self.tvmss.selection(),'SE'),daemon=1).start())
                menu_state.add_command(label='NU',command=lambda: threading.Thread(target=change_circuits_state,args=(self.tvmss.selection(),'NU'),daemon=1).start())
                menu_state.add_command(label='BA',command=lambda: threading.Thread(target=change_circuits_state,args=(self.tvmss.selection(),'BA'),daemon=1).start())
                menu_state.add_command(label='BL',command=lambda: threading.Thread(target=change_circuits_state,args=(self.tvmss.selection(),'BL'),daemon=1).start())
                menu.add_command(label='Cont check',command=lambda: threading.Thread(target=continuity_check,args=(self.tvmss.selection()),daemon=1).start())
                menu.add_command(label='find in MGW',command=lambda: threading.Thread(target=self.find_pcm_mss2mgw(),daemon=1).start())
                #[menu_state.add_command(label=x,command=lambda: change_circuits_state(self.tvmss.selection(),x)) for x in ('WO','BA','BL','SE','NU')]
            menu.post(event.x_root,event.y_root)
        self.tvmss.bind('<3>',submenu)
        self.nemss=TELNET(hostname,username,password,ne_name=self.mss_name)
        t1=time.time()
        while time.time()-t1<15 and self.nemss.exceptError=='' and self.nemss.Alive==False: time.sleep(1)
        if self.nemss.Alive==False:
            self.status.set("No connection to %s %s"%(hostname,self.nemss.exceptError))
            return
        self.status.set("ok")
        s=self.nemss.send('ZNET;')
        #self.write_to_terminal(self.logmss,s)
        s=s.split('\nSIGNALLING ')[1]
        for s in s.split('\nNETWORK: ')[1:]:
            net=s[:3]
            for rsh,rsd,rs_name,rs_state,rh,rd,r_state in re.findall('\s+  (\w{4})/(\d{5})       (\w+) +(\S{2})      (\w{4})/(\d{5})       ([\w-]{5}).*',s):
                #self.DPC['%s %s'%(net,rsh)]=(net,rsh,rsd,rs_name,rs_state,rh,rd,r_state)
                tmp='%-3s %-4s %-5s %-12s %-2s %-4s %-5s %5s'
                self.tvmss.insert('','end',iid='%s %s'%(net,rsh),text=tmp%(net,rsh,rsd,rs_name,rs_state,rh,rd,r_state),values=(net,rsh,rsd,rs_name,rs_state,rh,rd,r_state),tags=('dpc',))
        def continuity_check(*items):
            self.status.set('Continuity check started!')
            results=[]
            for item in items:
                if self.tvmss.item(item,option='tags')[0]!='pcm':continue
                'cgr,ncgr,ccspcm,TSL_STATE[vmgw_pcm],vmgw,TSL_strings[vmgw_pcm]'
                values=self.tvmss.item(item,option='values')
                cgr,ncgr,ccspcm,pcm_state,vmgw,pcmtsl=values
                pcm=pcmtsl.split('-')[0]
                s=self.nemss.send('ZCEL:CGR=%s,CONN=ID,FORM=EXT,;'%cgr)
                for s in re.findall('\s+ {0,4}%s-(\d+) +([\w-]+)  (IDLE).*'%pcm,s):
                    self.write_to_terminal(self.logmss,s)
                    self.write_to_terminal(self.logmss,'\n')
                    tsl,tsl_state,busy=s
                    print(s)
                    if tsl_state!='WO-EX' and tsl_state!='SE-US' and tsl_state!='BA-US' and tsl_state!='BL-US':
                        continue
                    if tsl_state=='WO-EX':
                        cgr_direction=self.tvmss.item(self.tvmss.parent(item),option='values')[2]
                        blocked_state={'BI':'SE','OUT':'BA','IN':'BL'}
                        s=self.nemss.send('ZCEC:MGW=%s,TERMID=%s-%s:%s;'%(vmgw,pcm,tsl,blocked_state[cgr_direction]))
                        self.write_to_terminal(self.logmss,s)
                        s=self.nemss.send('ZCEX:CCR:MGW=%s,TERMID=%s-%s:;'%(vmgw,pcm,tsl,))
                        self.write_to_terminal(self.logmss,s)
                        s=re.findall('%s-%s +%s +%s +([\w ]+)'%(pcm,tsl,cgr,ncgr),s)[0]
                        results.append('%s - %s\n'%(self.tvmss.item(item,option='text'),s))
                        self.write_to_terminal(self.logmss,s)
                        s=self.nemss.send('ZCEC:MGW=%s,TERMID=%s-%s:WO;'%(vmgw,pcm,tsl))
                        self.write_to_terminal(self.logmss,s)
                        break
                    if tsl_state=='SE-US' or tsl_state=='BA-US' or tsl_state=='BL-US':
                        s=self.nemss.send('ZCEX:CCR:MGW=%s,TERMID=%s-%s:;'%(vmgw,pcm,tsl,))
                        self.write_to_terminal(self.logmss,s)
                        s=re.findall('%s-%s +%s +%s +([\w ]+)'%(pcm,tsl,cgr,ncgr),s)[0]
                        results.append('%s - %s\n'%(self.tvmss.item(item,option='text'),s))
                        self.write_to_terminal(self.logmss,s)
                        break
            self.write_to_terminal(self.logmss,'\n\n\n')
            for result in results:
                self.write_to_terminal(self.logmss,result)
            self.status.set('Continuity check complete!')
        def change_circuits_state(items,new_state):
            print(items,new_state)
            s=[]
            for item in items:
                values=self.tvmss.item(item,option='values')
                cgr,ncgr,ccspcm,pcm_state,vmgw,pcm_tsl=values
                s.append('ZCEC:MGW=%s,TERMID=%s:%s:; ?'%(vmgw,pcm_tsl,new_state))
            ask=askyesnocancel('Change crct state?','\n'.join(s))
            if ask==True:
                for item in items:
                    values=self.tvmss.item(item,option='values')
                    cgr,ncgr,ccspcm,pcm_state,vmgw,pcm_tsl=values
                    text=self.tvmss.item(item,option='text')
                    self.tvmss.item(item,text='*'+text)
                    self.status.set('ZCEC:MGW=%s,TERMID=%s:%s:;'%(vmgw,pcm_tsl,new_state))
                    s=self.nemss.send('ZCEC:MGW=%s,TERMID=%s:%s:;'%(vmgw,pcm_tsl,new_state))
                    self.write_to_terminal(self.logmss,s)
                    #print('ZCEC:MGW=%s,TERMID=%s:%s:;'%(vmgw,pcm_tsl,new_state))
                self.status.append('ok')
                self.state1mss_load_circuits(self.tvmss.selection()[0])
                self.tvmss.selection_set(*items)
                return
        def delete_circuits(*items):
            s=[]
            current_item=self.tvmss.prev(items[0])
            for iid in items:
                values=self.tvmss.item(iid,option='values')
                cgr,ncgr,ccspcm,pcm_state,vmgw,pcm_tsl=values
                s.append('Delete pcm=%s ccspcm=%s from cgr=%s ?'%(pcm_tsl,ccspcm,cgr))
            ask=askyesnocancel('Deleting circuits','\n'.join(s))
            if ask==True:
                for iid in items:
                    values=self.tvmss.item(iid,option='values')
                    text=self.tvmss.item(iid,option='text')
                    cgr,ncgr,ccspcm,pcm_state,vmgw,pcm_tsl=values
                    self.tvmss.item(iid,text='*'+text)
                    self.status.set('Deleting termid=%s ccspcm=%s'%(pcm_tsl,ccspcm))
                    self.write_to_terminal(self.logmss,'ZRCR:CGR=%s:TERMID=%s;'%(cgr,pcm_tsl))
                    s=self.nemss.send('ZRCR:CGR=%s:TERMID=%s;'%(cgr,pcm_tsl))
                    self.write_to_terminal(self.logmss,s)
                self.state1mss_load_circuits(current_item)
                self.tvmss.see(current_item)
                return
            if ask==False:
                for iid in items:
                    values=self.tvmss.item(iid,option='values')
                    cgr,ncgr,ccspcm,pcm_state,vmgw,pcm_tsl=values
                    ask=askyesnocancel('Deleting circuits','Delete CGR=%s TERMID=%s CCSPCM=%s ?'%(cgr,pcm_tsl,ccspcm))
                    if ask==True:
                        print('ZRCR:CGR=%s:TERMID=%s;'%(cgr,pcm_tsl))
                        s=self.nemss.send('ZRCR:CGR=%s:TERMID=%s;'%(cgr,pcm_tsl))
                        self.write_to_terminal(self.logmss,s)
                        self.state1mss_load_circuits(self.tvmss.prev(iid))
                        continue
                    if ask==False:
                        print('No')
                        continue
                    return
        def add_circuits(*values):
            cgr=values[0]
            root=tk.Toplevel(self.winfo_toplevel())
            t="<PCMs> <CCSPCMs> <TSL>\n.......\nExample:\n245  13  1-31\n245-247  13-15  1-31\n245  13  1-15,17-31\n"
            tk.Label(root,text=t).grid(row=0,column=0)
            text_input=tk.Text(root,height=6,width=50)
            text_input.grid(row=0,column=1,rowspan=8)
            text_input.bind('<KeyRelease>',lambda e: func_generate())
            text=tk.Text(root,height=15)
            text.grid(row=8,column=0,columnspan=2)
            text2=tk.Text(root,height=6)
            text2.grid(row=9,column=0,columnspan=2)
            def func_generate():
                s=text_input.get('1.0',tk.END)
                s='\n'+s
                PCMs=re.findall('\s+([\d,-]+).*',s)
                CCSPCMs=re.findall('\s+[\d,-]+ +([\d,-]+).*',s)
                TSLs=re.findall('\s+[\d,-]+ +[\d,-]+ +([\d,-]+).*',s)
                if len(PCMs)==len(CCSPCMs)==len(TSLs):pass
                else:
                    text.delete('1.0',tk.END)
                    return
                text.delete('1.0',tk.END)
                for i in range(0,len(PCMs)):
                    pcm,ccspcm,tsl=PCMs[i],CCSPCMs[i],TSLs[i]
                    PCM=pcm.split(',')
                    CCSPCM=ccspcm.split(',')
                    tsl=tsl.replace('-','&&-').replace(',','&-')
                    for k in range(len(PCM)):
                        if str(PCM[k]).count('-')==0:continue
                        ss=PCM[k].split('-')
                        if len(ss)<2 or len(ss)>2:continue
                        PCM.pop(k)
                        a,b=int(ss[0]),int(ss[1])
                        for x in range(b-a,-1,-1):
                            PCM.insert(k,a+x)
                    for k in range(len(CCSPCM)):
                        ss=str(CCSPCM[k]).split('-')
                        if len(ss)<2 or len(ss)>2:continue
                        CCSPCM.pop(k)
                        a,b=int(ss[0]),int(ss[1])
                        for x in range(b-a,-1,-1):
                            CCSPCM.insert(k,a+x)
                    if len(CCSPCM)!=len(PCM):
                        text.delete('1.0',tk.END)
                        return
                    for k in range(len(CCSPCM)):
                        text.insert(tk.INSERT,'ZRCA:CGR=%s:TERMID=%s-%s:CCSPCM=%s::;\n'%(cgr,PCM[k],tsl,CCSPCM[k]))
            def func_create():
                cmds=re.findall('(ZRCA.*)\s+',text.get('1.0',tk.END))
                self.status.set('Executing commands in %s'%self.mss_name)
                current_item=self.tvmss.selection()[0]
                for cmd in cmds:
                    text2.insert(tk.INSERT,cmd)
                    text2.see(tk.INSERT)
                    self.status.set('sending %s'%(cmd))
                    s=self.nemss.send(cmd)
                    self.write_to_terminal(self.logmss,s)
                    text2.insert(tk.INSERT,s)
                    text2.see(tk.INSERT)
                    text2.update()
                text2.insert(tk.INSERT,'--Done--')
                text2.see(tk.INSERT)
                self.status.append('ok')
                self.state1mss_load_circuits(current_item)
            #cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
            #cancel.grid(row=10,column=1)
            generate=tk.Button(root,text='Generate commands',command=lambda: func_generate())
            generate.grid(row=10,column=0)
            create=tk.Button(root,text='Create in MSS',command=lambda: func_create())
            create.grid(row=11,column=0)
            root.wait_window()
            #print('ZRCA:CGR=%s:TERMID=%s:CCSPCM=%s::;'%(cgr,'444-1&&-31',5))
        def zcel_cgr(*items):
            for iid in items:
                tag=self.tvmss.item(iid,option='tags')[0]
                if tag!='pcm' and tag!='cgr':continue
                cgr=self.tvmss.item(iid,option='values')[0]
                s=self.nemss.send('ZCEL:CGR=%s;'%cgr)
                self.write_to_terminal(self.logmss,s)
        def dbl_click_on_dpc():
            item=self.tvmss.selection()[0]
            if self.tvmss.item(item,option='tags')[0]!='dpc':return
            self.state1mss_load_circuits(self.tvmss.selection()[0])
        self.tvmss.bind('<<Return+1>>',lambda e: threading.Thread(target=dbl_click_on_dpc,daemon=1).start())
    def state0mgw(self):
        try:self.nemgw.destroy()
        except:pass
        self.mgw_unbind()
        self.tvmgw.delete(*self.tvmgw.get_children())
        self.tvmgw.heading('#0',text='MGW')
        self.sessions=eval(open('sessions.txt').read())
        for mgw in self.sessions['MGWs']: self.tvmgw.insert('','end',id=mgw,text=mgw,tags=('mgw'))
        self.tvmgw.bind('<<Return+1>>',lambda e: threading.Thread(target=self.state1mgw,daemon=1).start())
    def state1mgw(self):
        self.mgw_unbind()
        hostname,protocol,type,username,password=self.sessions['MGWs'][self.tvmgw.selection()[0]]
        username,password=decipher(username),decipher(password)
        self.mgw_name=self.tvmgw.item(self.tvmgw.selection()[0],option='text')
        self.status.set('Trying to connect to %s, ip=%s'%(self.mgw_name,hostname))
        self.tvmgw.heading('#0',text=self.mgw_name)
        self.tvmgw.delete(*self.tvmgw.get_children())
        try:self.nemgw.destroy()
        except:pass
        def submenu(event=None):
            for child in self.tvmgw.winfo_children():child.destroy()
            menu=tk.Menu(self.tvmgw,tearoff=0)
            menu.add_command(label='collaps all',command=lambda: [self.tvmgw.item(iid,open=False) for iid in self.tvmgw.get_children()])
            menu.add_command(label='back to mgw list',command=lambda: self.state0mgw())
            tag=self.tvmgw.item(self.tvmgw.selection()[0],option='tags')[0]
            if tag=='pcm' or tag=='cgr':
                menu.add_command(label='update PCMs in this CGR',command=lambda: threading.Thread(target=load_circuits,args=(self.tvmgw.selection()),daemon=1).start())
                menu.add_command(label='add PCMs to this CGR',command=lambda: threading.Thread(target=add_PCMs,args=(self.tvmgw.item(self.tvmgw.selection()[0],option='values')[0],),daemon=1).start())
                menu.add_command(label='add PCMs to MSS and MGW',command=lambda: threading.Thread(target=self.add_pcms_to_cgr,daemon=1).start())
            if tag=='pcm':
                menu_state=tk.Menu(self.tvmgw,tearoff=0)
                menu.add_cascade(label='set state',menu=menu_state)
                menu_state.add_command(label='unlocked',command=lambda: threading.Thread(target=set_crct_state,args=(self.tvmgw.selection(),'unlocked')).start())
                menu_state.add_command(label='locked',command=lambda: threading.Thread(target=set_crct_state,args=(self.tvmgw.selection(),'locked')).start())
                menu.add_command(label='delete PCMs',command=lambda: threading.Thread(target=delete_PCMs,args=(self.tvmgw.selection()),daemon=1).start())
                menu.add_command(label='go to PCMs->ATERs',command=lambda: threading.Thread(target=find_MGW_Aters,daemon=1).start())
                menu.add_command(label='find PCMs in MSS',command=lambda: threading.Thread(target=self.find_pcm_mgw2mss,daemon=1).start())
            if tag=='ater' or tag=='Aters':
                menu.add_command(label='add ATERs',command=lambda: threading.Thread(target=add_aters,daemon=1).start())
                menu.add_command(label='delete Aters',command=lambda: threading.Thread(target=delete_aters,args=(self.tvmgw.selection()),daemon=1).start())
                menu_set_pool=tk.Menu(self.tvmgw,tearoff=0)
                menu.add_cascade(label='set pool',menu=menu_set_pool)
                menu_set_pool.add_command(label='28',command=lambda: threading.Thread(target=set_ater_pool,args=(28,),daemon=1).start())
                menu_set_pool.add_command(label='37',command=lambda: threading.Thread(target=set_ater_pool,args=(37,),daemon=1).start())
                menu.add_command(label='add APCMs to CGR in MSS and MGW',command=lambda: threading.Thread(target=add_aters_to_cgr,daemon=1).start())
                menu.add_command(label='show ET state',command=lambda: threading.Thread(target=load_ater_state,daemon=1).start())
                menu.add_command(label='go to ATERs->PCMs',command=lambda: threading.Thread(target=find_MGW_PCMs,daemon=1).start())
                menu.add_command(label='update all ATERs',command=lambda: threading.Thread(target=update_all_aters,daemon=1).start())
            menu.post(event.x_root,event.y_root)
        self.tvmgw.bind('<3>',submenu)
        self.nemgw=SSH(hostname,username,password,ne_name=self.mgw_name)
        t1=time.time()
        while time.time()-t1<15 and self.nemgw.exceptError=='' and self.nemgw.Alive==False: time.sleep(1)
        if self.nemgw.Alive==False:
            self.status.set("No connection to %s %s"%(hostname,self.nemgw.exceptError))
            return
        self.status.set('ok')
        def set_ater_pool(pool):
            root=tk.Toplevel(self.winfo_toplevel())
            text=tk.Text(root,height=20)
            text.grid(row=0,column=0,columnspan=2)
            text2=tk.Text(root,height=10)
            text2.grid(row=1,column=0,columnspan=2)
            for iid in self.tvmgw.selection():
                tag=self.tvmgw.item(iid,option='tags')[0]
                if tag!='ater':continue
                values=self.tvmgw.item(iid,option='values')
                et=values[0]
                i=1
                for apcm in values[1:5]:
                    if apcm!='-':
                        text.insert(tk.INSERT,'set tdm ater cpool et-index %s tcpcm-index %s cpool-value %s\n'%(et,i,pool))
                    i+=1
            def func_create():
                cmds=re.findall('(set tdm ater cpool et-index.*)\s+',text.get('1.0',tk.END))
                self.status.set('Executing commands in %s'%self.mgw_name)
                current_item=self.tvmgw.selection()
                for cmd in cmds:
                    text2.insert(tk.INSERT,cmd+'\n')
                    text2.see(tk.INSERT)
                    self.status.set('sending %s'%(cmd))
                    s=self.nemgw.send(cmd)
                    self.write_to_terminal(self.logmgw,s)
                    text2.insert(tk.INSERT,s)
                    text2.update()
                self.status.append('ok')
                load_aters()
                self.tvmgw.selection_set(current_item)
                self.tvmgw.item('Aters',open=True)
            cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
            cancel.grid(row=10,column=0)
            create=tk.Button(root,text='Send commands',command=lambda: func_create())
            create.grid(row=10,column=1)
            root.wait_window()
        def add_aters_to_cgr():
            root=tk.Toplevel(self.winfo_toplevel())
            t1=ttk.Treeview(root,show='tree',height=10)
            t1.column('#0',width=600)
            t1.grid(row=1,column=0)
            t2=ttk.Treeview(root,show='tree',height=10)
            t2.column('#0',width=350)
            t2.grid(row=1,column=1)
            t3=tk.Text(root,height=8)
            t3.grid(row=2,column=0)
            t4=tk.Text(root,height=8)
            t4.grid(row=2,column=1)
            text1=tk.Text(root,height=5)
            text1.grid(row=3,column=0)
            text2=tk.Text(root,height=5)
            text2.grid(row=3,column=1)
            ccspcms=[]
            for iid in self.tvmss.get_children():
                tag=self.tvmss.item(iid,option='tags')[0]
                if tag!='dpc':continue
                if self.tvmss.get_children(iid)==():continue
                text=self.tvmss.item(iid,option='text')
                values=self.tvmss.item(iid,option='values')
                t1.insert('','end',iid=iid,text=text,values=values,tags=('dpc',),open=True)
                for id in self.tvmss.get_children(iid):
                    tag=self.tvmss.item(id,option='tags')[0]
                    if tag!='cgr':continue
                    text=self.tvmss.item(id,option='text')
                    values=self.tvmss.item(id,option='values')
                    t1.insert(iid,'end',iid=id,text=text,values=values,tags=('cgr',))
                    for id1 in self.tvmss.get_children(id):
                        tag=self.tvmss.item(id1,option='tags')[0]
                        if tag!='pcm':continue
                        text=self.tvmss.item(id1,option='text')
                        values=self.tvmss.item(id1,option='values')
                        'cgr,ncgr,ccspcm,TSL_STATE[vmgw_pcm],vmgw,TSL_strings[vmgw_pcm])'
                        t1.insert(id,'end',iid=id1,text=text,values=values,tags=('pcm',))
                        ccspcms.append(int(values[2]))
            free_ccspcms=[i for i in range(0,500)]
            for x in ccspcms: free_ccspcms.remove(x)
            print(ccspcms)
            try:
                t1.selection_set(self.tvmss.selection())
                t1.see(self.tvmss.selection())
            except:pass
            for iid in self.tvmgw.get_children():
                tag=self.tvmgw.item(iid,option='tags')[0]
                if tag!='cgr':continue
                text=self.tvmgw.item(iid,option='text')
                values=self.tvmgw.item(iid,option='values')
                t2.insert('','end',iid=iid,text=text,values=values,tags=('cgr',))
            def generate1():
                if t1.selection()==():return
                ncgr=t1.item(t1.selection()[0],option='values')[1]
                #cgr,ncgr,cgr_direction,cgr_tree,nbcrct,cgr_state,vmgw
                t3.delete('1.0','end')
                i=0
                for iid in self.tvmgw.selection():
                    tag=self.tvmgw.item(iid,option='tags')[0]
                    if tag!='ater':continue
                    values=self.tvmgw.item(iid,option='values')
                    apcms=values[1:5]
                    tc4=values[6]
                    for apcm in apcms[:3]:
                        t3.insert(tk.INSERT,'ZRCA:NCGR=%s:TERMID=%s-1&&-31:CCSPCM=%s:::;\n'%(ncgr,apcm,free_ccspcms[i]))
                        i+=1
                    t3.insert(tk.INSERT,'ZRCA:NCGR=%s:TERMID=%s-1&&-%s:CCSPCM=%s:::;\n\n'%(ncgr,apcms[3],27-(31-int(tc4))*4,free_ccspcms[i]))
                    i+=1
            def generate2():
                if t2.selection()==():return
                ncgr=t2.item(t2.selection()[0],option='values')[1]
                t4.delete('1.0','end')
                for iid in self.tvmgw.selection():
                    tag=self.tvmgw.item(iid,option='tags')[0]
                    if tag!='ater':continue
                    values=self.tvmgw.item(iid,option='values')
                    apcms=values[1:5]
                    tc4=values[6]
                    for apcm in apcms[:3]:
                        t4.insert(tk.INSERT,'add tdm crct ncgr %s crct-pcm %s crct-tsl 1-31\n'%(ncgr,apcm))
                    t4.insert(tk.INSERT,'add tdm crct ncgr %s crct-pcm %s crct-tsl 1-%s\n\n'%(ncgr,apcms[3],27-(31-int(tc4))*4))
            def func_create1():
                cmds=re.findall('(ZRCA:NCGR=.*)\s+',t3.get('1.0',tk.END))
                self.status.set('Executing commands in %s'%self.mss_name)
                for cmd in cmds:
                    text1.insert(tk.INSERT,cmd+'\n')
                    text1.see(tk.INSERT)
                    self.status.set('sending %s'%(cmd))
                    s=self.nemss.send(cmd)
                    self.write_to_terminal(self.logmss,s)
                    text1.insert(tk.INSERT,s)
                    text1.update()
                text1.insert(tk.INSERT,'\n---Done---')
                text1.see(tk.INSERT)
                self.status.append('ok')
            def func_create2():
                cmds=re.findall('(add tdm crct ncgr.*)\s+',t4.get('1.0',tk.END))
                self.status.set('Executing commands in %s'%self.mgw_name)
                for cmd in cmds:
                    text2.insert(tk.INSERT,cmd+'\n')
                    text2.see(tk.INSERT)
                    self.status.set('sending %s'%(cmd))
                    s=self.nemgw.send(cmd)
                    self.write_to_terminal(self.logmgw,s)
                    text2.insert(tk.INSERT,s)
                    text2.update()
                text2.insert(tk.INSERT,'\n---Done---')
                text2.see(tk.INSERT)
                load_circuits(t2.selection()[0])
                self.tvmgw.item(t2.selection()[0],open=True)
                update_all_aters()
                root.lift()
                self.status.append('ok')
            t1.bind('<ButtonRelease-1>',lambda e: generate1())
            t2.bind('<ButtonRelease-1>',lambda e: generate2())
            create=tk.Button(root,text='Add to MSS',command=lambda: func_create1())
            create.grid(row=5,column=0)
            create=tk.Button(root,text='Add to MGW',command=lambda: func_create2())
            create.grid(row=5,column=1)
            cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
            cancel.grid(row=6,column=0)
            root.wait_window()
        def update_all_aters():
            selection=self.tvmgw.selection()
            load_aters()
            for iid in selection:
                self.tvmgw.selection_set(iid)
                self.tvmgw.see(iid)
        def find_MGW_PCMs():
            iids=self.tvmgw.selection()
            self.tvmgw.selection_set()
            self.status.set('ok')
            for iid in iids:
                tag=self.tvmgw.item(iid,option='tag')[0]
                if tag!='ater':continue
                values=self.tvmgw.item(iid,option='values')
                apcms=values[1:5]
                for apcm in apcms:
                    try:cgrs=self.pcm2cgr[int(apcm)]
                    except:
                        self.status.set('NOT ALL ATER-APCM found!!!')
                        continue
                    for cgr in cgrs:
                        self.tvmgw.selection_add('%s-%s'%(cgr,apcm))
                        self.tvmgw.see('%s-%s'%(cgr,apcm))
        def find_MGW_Aters():
            iids=self.tvmgw.selection()
            self.tvmgw.selection_set()
            self.status.set('ok')
            for iid in iids:
                if self.tvmgw.item(iid,option='tags')[0]!='pcm':continue
                values=self.tvmgw.item(iid,option='values')
                'cgr,ncgr,pcm,admin,oper,usage,tsl'
                et=self.pcm2Ater[int(values[2])]
                self.tvmgw.selection_add('ater-%s'%et)
                self.tvmgw.see('ater-%s'%et)
        def load_ater_state():
            update_et_state()
            for iid in self.tvmgw.get_children('Aters'):
                values=self.tvmgw.item(iid,option='values')
                admin,oper,usage=self.et_state[int(values[0])]
                self.tvmgw.item(iid,text=values[5]+' %s%s%s'%(admin[0],oper[0],usage[0]))
        def delete_aters(*items):
            prev_item=self.tvmgw.prev(items[0])
            s=[]
            for iid in items:
                if self.tvmgw.item(iid,option='tags')[0]!='ater':continue
                values=self.tvmgw.item(iid,option='values')
                et=values[0]
                s.append('Delete Ater for ET=%s ?'%et)
            ask=askyesnocancel('Deleting Aters','\n'.join(s))
            if ask==True:
                for iid in items:
                    if self.tvmgw.item(iid,option='tags')[0]!='ater':continue
                    values=self.tvmgw.item(iid,option='values')
                    et=values[0]
                    self.status.set('Delete Ater for ET=%s ?'%et)
                    print('Delete Ater for ET=%s ?'%et)
                    self.tvmgw.item(iid,text=self.tvmgw.item(iid,option='text')+'*')
                    for i in range(4,0,-1):
                        if values[i]!='-':
                            self.status.set('delete tdm ater et-index %s tcpcm-index %s'%(et,i))
                            s=self.nemgw.send('delete tdm ater et-index %s tcpcm-index %s'%(et,i))
                            self.write_to_terminal(self.logmgw,s)
                    self.status.set('set tdm ater nbr et-index %s thru-conn-num 0'%et)
                    s=self.nemgw.send('set tdm ater nbr et-index %s thru-conn-num 0'%et)
                    self.write_to_terminal(self.logmgw,s)
                    self.status.set('ok')
                load_aters()
                self.tvmgw.selection_set(prev_item)
                self.tvmgw.item('Aters',open=True)
                return
        def add_aters():
            root=tk.Toplevel(self.winfo_toplevel())
            t="<ET>\n.......\n\n\nExample:\n24,246-248\n"
            tk.Label(root,text=t).grid(row=0,column=0)
            text_input=tk.Text(root,height=6,width=50)
            text_input.grid(row=0,column=1,rowspan=6)
            text_input.bind('<KeyRelease>',lambda e: func_generate())
            cpool,nbr=tk.StringVar(),tk.StringVar()
            cpool.set(28)
            nbr.set(0)
            tk.Label(root,text='cpool=').grid(row=6,column=0)
            tk.OptionMenu(root,cpool,20,23,28,37,command=lambda e: func_generate()).grid(row=6,column=1,sticky='e')
            tk.Label(root,text='thru-conn-num=').grid(row=7,column=0)
            tk.OptionMenu(root,nbr,0,1,2,4,8,16,command=lambda e: func_generate()).grid(row=7,column=1,sticky='e')
            text=tk.Text(root,height=15)
            text.grid(row=8,column=0,columnspan=2)
            text2=tk.Text(root,height=6)
            text2.grid(row=9,column=0,columnspan=2)
            def func_generate():
                s=text_input.get('1.0',tk.END)
                s='\n'+s
                PCMs=re.findall('\s+([\d,-]+).*',s)
                #TSLs=re.findall('\s+[\d,-]+ +([\d,-]+).*',s)
                text.delete('1.0',tk.END)
                #if len(PCMs)!=len(TSLs):return
                for i in range(0,len(PCMs)):
                    pcm=PCMs[i]
                    PCM=pcm.split(',')
                    #tsl=tsl.replace('-','&&-').replace(',','&-')
                    for k in range(len(PCM)):
                        if str(PCM[k]).count('-')==0:continue
                        ss=PCM[k].split('-')
                        if len(ss)<2 or len(ss)>2:continue
                        PCM.pop(k)
                        try:a,b=int(ss[0]),int(ss[1])
                        except:continue
                        for x in range(b-a,-1,-1):
                            PCM.insert(k,a+x)
                    for k in range(len(PCM)):
                        text.insert(tk.INSERT,'set tdm ater nbr et-index %s thru-conn-num %s\n'%(PCM[k],nbr.get()))
                        text.insert(tk.INSERT,'add tdm ater et-index %s tcpcm-index 1 cpool-value %s\n'%(PCM[k],cpool.get()))
                        text.insert(tk.INSERT,'add tdm ater et-index %s tcpcm-index 2 cpool-value %s\n'%(PCM[k],cpool.get()))
                        text.insert(tk.INSERT,'add tdm ater et-index %s tcpcm-index 3 cpool-value %s\n'%(PCM[k],cpool.get()))
                        text.insert(tk.INSERT,'add tdm ater et-index %s tcpcm-index 4 cpool-value %s\n'%(PCM[k],cpool.get()))
            def func_create():
                cmds=re.findall('(add tdm ater et-index.*)\s+',text.get('1.0',tk.END))
                self.status.set('Executing commands in %s'%self.mgw_name)
                current_item=self.tvmgw.selection()
                for cmd in cmds:
                    text2.insert(tk.INSERT,cmd+'\n')
                    text2.see(tk.INSERT)
                    self.status.set('sending %s'%(cmd))
                    s=self.nemgw.send(cmd)
                    self.write_to_terminal(self.logmgw,s)
                    text2.insert(tk.INSERT,s)
                    text2.update()
                    text2.see(tk.INSERT)
                text2.insert(tk.INSERT,'--Done--')
                text2.update()
                text2.see(tk.END)
                self.status.append('ok')
                load_aters()
                self.tvmgw.selection_set(current_item)
                self.tvmgw.item('Aters',open=True)
            #cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
            #cancel.grid(row=10,column=1)
            generate=tk.Button(root,text='Generate commands',command=lambda: func_generate())
            generate.grid(row=10,column=0)
            create=tk.Button(root,text='Create in MGW',command=lambda: func_create())
            create.grid(row=11,column=0)
            root.wait_window()
        def set_crct_state(items,new_state):
            cgrs={}
            for item in items:
                if self.tvmgw.item(item,option='tag')[0]!='pcm':continue
                cgr,ncgr,pcm,admin,oper,usage,tsl=self.tvmgw.item(item,option='values')
                cgrs[cgr]=1
                self.tvmgw.item(item,text=self.tvmgw.item(item,option='text')+'*')
                s=self.nemgw.send('set tdm crct-state admin-state %s crct-pcm %s crct-tsl %s'%(new_state,pcm,tsl))
                self.write_to_terminal(self.logmgw,s)
            load_circuits(list(cgrs.keys()))
            self.tvmgw.selection_set(items)
        def delete_PCMs(*items):
            s=[]
            current_cgr=self.tvmgw.item(items[0],option='values')[0]
            for iid in items:
                if self.tvmgw.item(iid,option='tags')[0]!='pcm':continue
                values=self.tvmgw.item(iid,option='values')
                cgr,ncgr,pcm,admin,oper,usage,tsl=values
                s.append('Delete pcm=%s tsl=%s from cgr=%s ?'%(pcm,tsl,cgr))
            ask=askyesnocancel('Deleting circuits','\n'.join(s))
            if ask==True:
                for iid in items:
                    if self.tvmgw.item(iid,option='tags')[0]!='pcm':continue
                    values=self.tvmgw.item(iid,option='values')
                    cgr,ncgr,pcm,admin,oper,usage,tsl=values
                    self.status.set('Deleting pcm=%s crct=%s'%(pcm,tsl))
                    print('delete tdm crct cgr %s crct-pcm %s crct-tsl %s'%(cgr,pcm,tsl))
                    self.tvmgw.item(iid,text=self.tvmgw.item(iid,option='text')+'*')
                    s=self.nemgw.send('delete tdm crct cgr %s crct-pcm %s crct-tsl %s'%(cgr,pcm,tsl))
                    self.write_to_terminal(self.logmgw,s)
                load_circuits(current_cgr)
                return
        def add_PCMs(cgr):
            print(cgr)
            root=tk.Toplevel(self.winfo_toplevel())
            t="<PCMs> <TSL>\n.......\nExample:\n245  1-31\n245-247  1-31\n245  1-15,17-31\n"
            tk.Label(root,text=t).grid(row=0,column=0)
            text_input=tk.Text(root,height=6,width=50)
            text_input.grid(row=0,column=1,rowspan=8)
            text_input.bind('<KeyRelease>',lambda e: func_generate())
            text=tk.Text(root,height=15)
            text.grid(row=8,column=0,columnspan=2)
            text2=tk.Text(root,height=6)
            text2.grid(row=9,column=0,columnspan=2)
            def func_generate():
                s=text_input.get('1.0',tk.END)
                s='\n'+s
                PCMs=re.findall('\s+([\d,-]+).*',s)
                TSLs=re.findall('\s+[\d,-]+ +([\d,-]+).*',s)
                text.delete('1.0',tk.END)
                if len(PCMs)!=len(TSLs):return
                for i in range(0,len(PCMs)):
                    pcm,tsl=PCMs[i],TSLs[i]
                    PCM=pcm.split(',')
                    #tsl=tsl.replace('-','&&-').replace(',','&-')
                    for k in range(len(PCM)):
                        if str(PCM[k]).count('-')==0:continue
                        ss=PCM[k].split('-')
                        if len(ss)<2 or len(ss)>2:continue
                        PCM.pop(k)
                        a,b=int(ss[0]),int(ss[1])
                        for x in range(b-a,-1,-1):
                            PCM.insert(k,a+x)
                    for k in range(len(PCM)):
                        text.insert(tk.INSERT,'add tdm crct cgr %s crct-pcm %s crct-tsl %s\n'%(cgr,PCM[k],tsl))
            def func_create():
                cmds=re.findall('(add tdm crct cgr.*)\s+',text.get('1.0',tk.END))
                self.status.set('Executing commands in %s'%self.mgw_name)
                current_item=self.tvmgw.selection()[0]
                for cmd in cmds:
                    text2.insert(tk.INSERT,cmd)
                    text2.see(tk.INSERT)
                    self.status.set('sending %s'%(cmd))
                    s=self.nemgw.send(cmd)
                    self.write_to_terminal(self.logmgw,s)
                    text2.insert(tk.INSERT,s)
                    text2.update()
                self.status.append('ok')
                load_circuits(current_item)
                root.lift()
            #cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
            #cancel.grid(row=10,column=1)
            generate=tk.Button(root,text='Generate commands',command=lambda: func_generate())
            generate.grid(row=10,column=0)
            create=tk.Button(root,text='Create in MGW',command=lambda: func_create())
            create.grid(row=11,column=0)
            root.wait_window()
        def load_circuits(*items):
            cgr='2-2037'
            if items!=():
                cgrs={}
                for item in items:
                    cgrs[self.tvmgw.item(item,option='values')[0]]=1
                cgr=','.join(list(cgrs.keys()))
                for i in cgrs:
                    for s in self.tvmgw.get_children(i):
                        cgr,pcm=s.split('-')
                        cgr,pcm=int(cgr),int(pcm)
                        cgr_list=self.pcm2cgr[pcm]
                        while cgr_list.count(cgr)>0:cgr_list.remove(cgr)
            else:self.pcm2cgr={}#[pcm]=[cgr1,cgr2,...]
            self.status.set("Query 'show tdm circuitgroup crct cgr cgr-num %s'"%cgr)
            s=self.nemgw.send('show tdm circuitgroup crct cgr cgr-num %s'%cgr)
            self.winfo_toplevel().state('iconic')
            for s in s.split('\nNCGR:')[1:]:
                ncgr,cgr=re.findall('^(\w+) +CGR:(\d+)',s)[0]
                cgr=int(cgr)
                position='end'
                if self.tvmgw.exists(cgr):
                    position=self.tvmgw.index(cgr)
                    self.tvmgw.delete(cgr)
                lines=re.findall('\s+(\d+)-(\d+) +(\d+) +(\w+) +(\w+) +(\w+)',s)
                count=len(lines)
                if position=='end':self.tvmgw.insert('',position,iid=cgr,text='%-5s %-12s %-4s'%(cgr,ncgr,count),values=(cgr,ncgr,count),tags=('cgr',))
                else: self.tvmgw.insert('',position,iid=cgr,text='%-5s %-12s %-4s'%(cgr,ncgr,count),values=(cgr,ncgr,count),tags=('cgr',),open=True)
                TSLs={}#TSLs[pcm]=[1,2,3,...,31]
                PCM_STATE={}#PCM_STATE[pcm]=('unlocked','enabled','busy')
                for pcm,tsl,ord,admin,oper,usage in lines:
                    pcm,tsl=int(pcm),int(tsl)
                    try:TSLs[pcm].append(tsl)
                    except:TSLs[pcm]=[tsl]
                    try:
                        PCM_STATE[pcm]
                        if usage=='busy':PCM_STATE[pcm]=(admin,oper,'busy')
                    except: PCM_STATE[pcm]=(admin,oper,usage)

                for pcm in TSLs:TSLs[pcm].sort()
                for pcm in PCM_STATE:
                    admin,oper,usage=PCM_STATE[pcm]
                    tsl=get_mgw_tsl_string(TSLs[pcm])
                    text='%-5s %-8s %-8s %-8s %s'%(pcm,admin,oper,usage,tsl)
                    self.tvmgw.insert(cgr,'end',iid='%s-%s'%(cgr,pcm),text=text,values=(cgr,ncgr,pcm,admin,oper,usage,tsl),tags=('pcm',))
                    try:
                        if self.pcm2cgr[pcm].count(cgr)==0: self.pcm2cgr[pcm].append(cgr)
                    except:self.pcm2cgr[pcm]=[cgr]
            self.winfo_toplevel().state('normal')
            try: self.tvmgw.selection_set(items)
            except:pass
            if items==():
                self.status.set('Query: show tdm ater')
                load_aters()
            self.status.set('ok')
        def load_aters():
            self.Aters={}
            self.pcm2Ater={}
            s=self.nemgw.send('show tdm ater')
            selection=self.tvmgw.selection()
            try: self.tvmgw.delete('Aters')
            except:pass
            self.tvmgw.insert('',0,iid='Aters',text='Aters',tags=('Aters',))
            for apcm,et,tc,tc2,speed,cpool in re.findall('\s+(\d+) +(\d+) +(\d+)-(\d+) +(\d+) +(\d+).*',s):
                apcm,et,tc,tc2,speed,cpool=int(apcm),int(et),int(tc),int(tc2),int(speed),int(cpool)
                try:
                    self.Aters[et].append((apcm,tc,tc2,speed,cpool))
                    self.pcm2Ater[apcm]=et
                except:
                    self.Aters[et]=[(apcm,tc,tc2,speed,cpool)]
                    self.pcm2Ater[apcm]=et
            aters=list(self.Aters.keys())
            aters.sort()
            self.mgw_pcm2cgr={}
            for cgr in self.tvmgw.get_children():
                if self.tvmgw.item(cgr,option='tags')[0]!='cgr':continue
                for cgr_pcm in self.tvmgw.get_children(cgr):
                    if self.tvmgw.item(cgr_pcm,option='tags')[0]!='pcm':continue
                    values=self.tvmgw.item(cgr_pcm,option='values')
                    cgr,pcm=int(values[0]),int(values[2])
                    try:self.mgw_pcm2cgr[pcm].append(cgr)
                    except:self.mgw_pcm2cgr[pcm]=[cgr,]
            for et in aters:
                apcm,tc,tc2,speed,cpool=[['-','-','-','-'] for i in range(0,5)]
                for i in range(0,4):
                    try:apcm[i],tc[i],tc2[i],speed[i],cpool[i]=self.Aters[et][i]
                    except:pass
                x=['*','*','*','*']
                for i in range(0,4):
                    try:
                        if self.mgw_pcm2cgr.get(int(apcm[i]))==None:x[i]='-'
                    except: x[i]='-'
                try: tc24=31-int(tc2[3])
                except: tc24='-'
                text='%-4s %s%s%s%s%s%s%s%s%s %s %s %s %s'%(et,apcm[0],x[0],apcm[1],x[1],apcm[2],x[2],apcm[3],x[3],cpool[0],cpool[1],cpool[2],cpool[3],tc24)
                self.tvmgw.insert('Aters','end',iid='ater-%s'%et,text=text,values=(et,apcm[0],apcm[1],apcm[2],apcm[3],text,tc2[3]),tags=('ater',))
        def update_et_state():
            self.status.set('executing: show tdm pdh et-state')
            s=self.nemgw.send('show tdm pdh et-state')
            for et,admin,oper,usage in re.findall('\s+(\d+) +(\w+) +(\w+) +(\w+).*',s):
                self.et_state[int(et)]=[admin,oper,usage]
            self.status.set('ok')
        threading.Thread(target=load_circuits,daemon=1).start()
    def add_pcms_to_cgr(self):
        root=tk.Toplevel(self.winfo_toplevel())
        t1=ttk.Treeview(root,show='tree',height=10)
        t1.column('#0',width=600)
        t1.grid(row=0,column=0,rowspan=2,sticky='NEWS')
        tk.Label(root,text='<PCMs> <CCSPCMs> <TSL>\n.............').grid(row=0,column=1,columnspan=2)
        t2=tk.Text(root,height=8)
        t2.grid(row=1,column=1,sticky='NEWS')
        t3=tk.Text(root,height=8)
        t3.grid(row=2,column=0)
        t4=tk.Text(root,height=8)
        t4.grid(row=2,column=1)
        text1=tk.Text(root,height=5)
        text1.grid(row=3,column=0)
        text2=tk.Text(root,height=5)
        text2.grid(row=3,column=1)
        ccspcms=[]
        for iid in self.tvmss.get_children():
            tag=self.tvmss.item(iid,option='tags')[0]
            if tag!='dpc':continue
            if self.tvmss.get_children(iid)==():continue
            text=self.tvmss.item(iid,option='text')
            values=self.tvmss.item(iid,option='values')
            t1.insert('','end',iid=iid,text=text,values=values,tags=('dpc',),open=True)
            for id in self.tvmss.get_children(iid):
                tag=self.tvmss.item(id,option='tags')[0]
                if tag!='cgr':continue
                text=self.tvmss.item(id,option='text')
                values=self.tvmss.item(id,option='values')
                t1.insert(iid,'end',iid=id,text=text,values=values,tags=('cgr',))
                for id1 in self.tvmss.get_children(id):
                    tag=self.tvmss.item(id1,option='tags')[0]
                    if tag!='pcm':continue
                    text=self.tvmss.item(id1,option='text')
                    values=self.tvmss.item(id1,option='values')
                    'cgr,ncgr,ccspcm,TSL_STATE[vmgw_pcm],vmgw,TSL_strings[vmgw_pcm])'
                    t1.insert(id,'end',iid=id1,text=text,values=values,tags=('pcm',))
                    ccspcms.append(int(values[2]))
        free_ccspcms=[i for i in range(0,500)]
        for x in ccspcms: free_ccspcms.remove(x)
        print(ccspcms)
        try:
            t1.selection_set(self.tvmss.selection())
            t1.see(self.tvmss.selection())
        except:pass
        def generate1():
            if t1.selection()==():return
            ncgr=t1.item(t1.selection()[0],option='values')[1]
            #cgr,ncgr,cgr_direction,cgr_tree,nbcrct,cgr_state,vmgw
            s=t2.get('1.0',tk.END)
            s='\n'+s
            PCMs=re.findall('\s+([\d,-]+).*',s)
            CCSPCMs=re.findall('\s+[\d,-]+ +([\d,-]+).*',s)
            TSLs=re.findall('\s+[\d,-]+ +[\d,-]+ +([\d,-]+).*',s)
            if len(PCMs)==len(CCSPCMs)==len(TSLs):pass
            else:
                t3.delete('1.0',tk.END)
                return
            t3.delete('1.0',tk.END)
            for i in range(0,len(PCMs)):
                pcm,ccspcm,tsl=PCMs[i],CCSPCMs[i],TSLs[i]
                PCM=pcm.split(',')
                CCSPCM=ccspcm.split(',')
                tsl=tsl.replace('-','&&-').replace(',','&-')
                for k in range(len(PCM)):
                    if str(PCM[k]).count('-')==0:continue
                    ss=PCM[k].split('-')
                    if len(ss)<2 or len(ss)>2:continue
                    PCM.pop(k)
                    a,b=int(ss[0]),int(ss[1])
                    for x in range(b-a,-1,-1):
                        PCM.insert(k,a+x)
                for k in range(len(CCSPCM)):
                    ss=str(CCSPCM[k]).split('-')
                    if len(ss)<2 or len(ss)>2:continue
                    CCSPCM.pop(k)
                    a,b=int(ss[0]),int(ss[1])
                    for x in range(b-a,-1,-1):
                        CCSPCM.insert(k,a+x)
                if len(CCSPCM)!=len(PCM):
                    t3.delete('1.0',tk.END)
                    return
                for k in range(len(CCSPCM)):
                    t3.insert(tk.INSERT,'ZRCA:NCGR=%s:TERMID=%s-%s:CCSPCM=%s::;\n'%(ncgr,PCM[k],tsl,CCSPCM[k]))
        def generate2():
            ncgr=self.tvmgw.item(self.tvmgw.selection()[0],option='values')[1]
            s=t2.get('1.0',tk.END)
            s='\n'+s
            PCMs=re.findall('\s+([\d,-]+).*',s)
            CCSPCMs=re.findall('\s+[\d,-]+ +([\d,-]+).*',s)
            TSLs=re.findall('\s+[\d,-]+ +[\d,-]+ +([\d,-]+).*',s)
            t4.delete('1.0','end')
            if len(PCMs)==len(CCSPCMs)==len(TSLs):pass
            else:
                t3.delete('1.0',tk.END)
                return
            for i in range(0,len(PCMs)):
                pcm,tsl=PCMs[i],TSLs[i]
                PCM=pcm.split(',')
                #tsl=tsl.replace('-','&&-').replace(',','&-')
                for k in range(len(PCM)):
                    if str(PCM[k]).count('-')==0:continue
                    ss=PCM[k].split('-')
                    if len(ss)<2 or len(ss)>2:continue
                    PCM.pop(k)
                    a,b=int(ss[0]),int(ss[1])
                    for x in range(b-a,-1,-1):
                        PCM.insert(k,a+x)
                for k in range(len(PCM)):
                    t4.insert(tk.INSERT,'add tdm crct ncgr %s crct-pcm %s crct-tsl %s\n'%(ncgr,PCM[k],tsl))
        def func_create1():
            cmds=re.findall('(ZRCA:NCGR=.*)\s+',t3.get('1.0',tk.END))
            self.status.set('Executing commands in %s'%self.mss_name)
            for cmd in cmds:
                text1.insert(tk.INSERT,cmd+'\n')
                text1.see(tk.INSERT)
                self.status.set('sending %s'%(cmd))
                s=self.nemss.send(cmd)
                self.write_to_terminal(self.logmss,s)
                text1.insert(tk.INSERT,s)
                text1.update()
            text1.insert(tk.INSERT,'\n---Done---')
            text1.see(tk.INSERT)
            self.status.append('ok')
        def func_create2():
            cmds=re.findall('(add tdm crct ncgr.*)\s+',t4.get('1.0',tk.END))
            self.status.set('Executing commands in %s'%self.mgw_name)
            for cmd in cmds:
                text2.insert(tk.INSERT,cmd+'\n')
                text2.see(tk.INSERT)
                self.status.set('sending %s'%(cmd))
                s=self.nemgw.send(cmd)
                self.write_to_terminal(self.logmgw,s)
                text2.insert(tk.INSERT,s)
                text2.update()
            text2.insert(tk.INSERT,'\n---Done---')
            text2.see(tk.INSERT)
            self.status.append('ok')
        t1.bind('<ButtonRelease-1>',lambda e: generate1())
        t2.bind('<KeyRelease>',lambda e: generate2())
        create=tk.Button(root,text='Add to MSS',command=lambda: func_create1())
        create.grid(row=5,column=0)
        create=tk.Button(root,text='Add to MGW',command=lambda: func_create2())
        create.grid(row=5,column=1)
        root.wait_window()
    def state1mss_load_circuits(self,item):
        current_item=item
        while self.tvmss.item(item,option='tags')[0]!='dpc':
            item=self.tvmss.parent(item)
        values=self.tvmss.item(item,option='values')
        net,rsh,rsd,rs_name,rs_state,rh,rd,r_state=values
        TSL={}
        #TSLCGR={}
        #CCSPCM={}
        CCSPCM1={}
        TSL_STATE={}
        CGR={}#CGR[pcm]=[cgr,ncgr,vmgw]
        NCGR={}#NCGR[cgr]=ncgr
        self.tvmss.delete(*self.tvmss.get_children(item))
        s=self.nemss.send('ZRCI:SEA=6:NET=%s,SPC=%s;'%(net,rsh))
        #self.write_to_terminal(self.logmss,s)
        for cgr,ncgr,cgr_type,cgr_direction,cgr_tree,nbcrct,cgr_state in re.findall('\s(\d{1,4}) +(\w+) +(\w+) +(\w+) +([\w-]+) +(\d+) +([\w-]+).+',s):
            s=self.nemss.send('ZRCI:SEA=3:CGR=%s:PRINT=5;'%(cgr))
            #self.write_to_terminal(self.logmss,s)
            for s in s.split('\nCGR      : ')[1:]:
                header,circuits=s.split('\nCIRCUIT(S)')
                cgr,ncgr,vmgw=re.findall('^(\d+).+: (\w+) +[\s\S]+MGW      : (\w+)',header)[0]
                opc='-'
                if header.find('OPC(H/D) :')!=-1: opc=re.findall('\sOPC.{5} : ([\w/-]+).*',header)[0]
                #print('cgr=%s opc=%s'%(cgr,opc))
                self.tvmss.insert('%s %s'%(net,rsh),'end',iid='cgr=%s'%cgr,text='%-4s %-12s %-3s %-4s %-6s %-5s %-12s %-9s'%(cgr,ncgr,cgr_direction,cgr_tree,nbcrct,cgr_state,vmgw,opc),values=(cgr,ncgr,cgr_direction,nbcrct,vmgw,opc),tags=('cgr',))
                for pcm,tsl,tsl_state,ccspcm in re.findall('\s(\d+)-(\d+) +\w+ +\w+ +[\d-]+ +([\w-]+)+ +(\d+)',circuits):
                    pcm,tsl,ccspcm=int(pcm),int(tsl),int(ccspcm)
                    CGR['%s,%s'%(vmgw,pcm)]=(cgr,ncgr,vmgw)
                    #CGR[pcm]=[cgr,ncgr,vmgw]
                    NCGR[cgr]=ncgr
                    CCSPCM1['%3s,%s,%s,%s'%(ccspcm,cgr,ncgr,vmgw)]='%s,%s,%s'%(cgr,vmgw,pcm)
                    #CCSPCM[ccspcm]='%s,%s'%(vmgw,pcm)
                    TSL_STATE['%s,%s,%s'%(cgr,vmgw,pcm)]=tsl_state
                    try:TSL['%s,%s,%s'%(cgr,vmgw,pcm)].append(tsl)
                    except:TSL['%s,%s,%s'%(cgr,vmgw,pcm)]=[tsl]
        self.tvmss.insert('%s %s'%(net,rsh),0,iid='header dpc %s %s'%(net,rsh),text='%-4s %-12s %-3s %-4s %-6s %-5s %-12s %-9s'%('cgr','ncgr','dir','tree','nbcrct','state','vmgw','opc'),tags=('header',))
        self.tvmss.insert('%s %s'%(net,rsh),'end',iid='all %s %s'%(net,rsh),text='All in one:',tags=('All',))
        PCM=list(TSL)
        PCM.sort()
        ccspcms1=list(CCSPCM1)
        ccspcms1.sort()
        TSL_strings={}
        for cgr_vmgw_pcm in TSL:
            cgr,vmgw,pcm=cgr_vmgw_pcm.split(',')
            TSL[cgr_vmgw_pcm].sort()
            TSL_strings[cgr_vmgw_pcm]=get_tsl_string(pcm,TSL[cgr_vmgw_pcm])
        for ccspcm_cgr in ccspcms1:
            ccspcm,cgr,ncgr,vmgw=ccspcm_cgr.split(',')
            ccspcm=int(ccspcm)
            cgr_vmgw_pcm=CCSPCM1[ccspcm_cgr]
            tsls=[x for x in range(1,32)]
            [tsls.remove(i) for i in TSL[cgr_vmgw_pcm]]
            #cgr1,ncgr,vmgw=CGR[vmgw_pcm]
            #print('allpcm %s %s %s %s %s'%(cgr,cgr1,ccspcm,ncgr,vmgw))
            self.tvmss.insert('all %s %s'%(net,rsh),'end',iid='allpcm %s %s'%(cgr,ccspcm),text='%-4s %-12s %-6s %-5s %-12s %-12s'%(cgr,ncgr,ccspcm,TSL_STATE[cgr_vmgw_pcm],vmgw,TSL_strings[cgr_vmgw_pcm]),tags=('pcm',),values=(cgr,ncgr,ccspcm,TSL_STATE[cgr_vmgw_pcm],vmgw,TSL_strings[cgr_vmgw_pcm]))
            self.tvmss.insert('cgr=%s'%cgr,'end',iid='pcm %s %s'%(cgr,ccspcm),text='%-4s %-12s %-6s %-5s %-12s %-12s'%(cgr,ncgr,ccspcm,TSL_STATE[cgr_vmgw_pcm],vmgw,TSL_strings[cgr_vmgw_pcm]),tags=('pcm',),values=(cgr,ncgr,ccspcm,TSL_STATE[cgr_vmgw_pcm],vmgw,TSL_strings[cgr_vmgw_pcm]))
        for cgr in NCGR:
            cgr_count=len(self.tvmss.get_children('cgr=%s'%cgr))
            self.tvmss.insert('cgr=%s'%cgr,0,iid='header cgr %s'%cgr,text='%-4s %-12s %-6s %-5s %-12s %-12s count=%-5s'%('cgr','ncgr','ccspcm','state','vmgw','pcm-tsl',cgr_count),tags=('header',))
        all_count=len(self.tvmss.get_children('all %s %s'%(net,rsh)))
        self.tvmss.insert('all %s %s'%(net,rsh),0,iid='all header %s %s'%(net,rsh),text='%-4s %-12s %-6s %-5s %-12s %-12s count=%-5s'%('cgr','ncgr','ccspcm','state','vmgw','pcm-tsl',all_count),tags=('header',))
        self.status.append('-ok')
        if self.tvmss.exists(current_item):
            tag=self.tvmss.item(current_item,option='tags')[0]
            if tag=='pcm':
                try:
                    self.tvmss.see(current_item)
                    #self.tvmss.selection_set(current_item)
                except:pass
    def find_pcm_mss2mgw(self):
        self.status.set('finding PCMs in MGW')
        vmgw2mgwip={}#vmgw->ip
        s=self.nemss.send('ZJGI:;')
        self.write_to_terminal(self.logmss,s)
        for s in re.findall('\s+\d+ +(\w+) .*REGISTERED.*\s+\d+ +([\d.]+)',s): vmgw2mgwip[s[0]]=s[1]
        try: s=self.nemgw.send('show vmgw mgw mod 2')
        except Exception as e:
            self.write_to_terminal(self.logmss,e)
            self.status.set(e)
            return
        self.write_to_terminal(self.logmgw,s)
        pcm2iid={}
        for iid in self.tvmgw.get_children():
            if self.tvmgw.item(iid,option='tags')[0]!='cgr':continue
            for id in self.tvmgw.get_children(iid):
                if self.tvmgw.item(id,option='tags')[0]!='pcm':continue
                values=self.tvmgw.item(id,option='values')
                'cgr,ncgr,pcm,admin,oper,usage,tsl'
                pcm=int(values[2])
                pcm2iid[pcm]=id
        self.tvmgw.selection_set()
        for iid in self.tvmss.selection():
            if self.tvmss.item(iid,option='tag')[0]!='pcm':continue
            values=self.tvmss.item(iid,option='values')
            'cgr,ncgr,ccspcm,TSL_STATE,vmgw,TSL_strings'
            vmgw,pcm=values[4],int(values[5].split('-')[0])
            #print('ip2mgwcgr',vmgw,vmgw2mgwip[vmgw],ip2mgwcgr[vmgw2mgwip[vmgw]])
            if s.find(vmgw2mgwip[vmgw])==-1:
                self.write_to_terminal(self.logmss,'\n\n\nWARNING: No such VMGW=%s in MGW=%s\n'%(vmgw,self.mgw_name))
                continue
            try:
                self.tvmgw.selection_add(pcm2iid[pcm])
                self.tvmgw.see(pcm2iid[pcm])
            except: self.write_to_terminal(self.logmss,'\n\n\nWARNING: No such PCM=%s in MGW=%s\n'%(pcm,self.mgw_name))
        self.status.set('ok')
    def find_pcm_mgw2mss(self):
        self.status.set('finding PCMs in MSS')
        cgr2ip={}
        s=self.nemgw.send('show vmgw mgw mod 2')
        self.write_to_terminal(self.logmgw,s)
        for s in s.split('VIRTUAL MGW DATA:')[1:]:
            for s in re.findall('\s+own primary IP address           : ([\d.]+).*\s+own secondary IP address         : ([\d.]+)[\s\S]+circuit group                    : ([\w ,\s]+)\sCONTROLLER DATA :',s):
                print(s)
                for cgr in s[2].split(','):
                    cgr.replace('\n','')
                    cgr=int(cgr)
                    cgr2ip[cgr]=[s[0],s[1]]
        ip2vmgw={}
        s=self.nemss.send('ZJGI;')
        self.write_to_terminal(self.logmss,s)
        for s in re.findall('\s+\d+ +(\w+) .*REGISTERED.*\s+\d+ +([\d.]+)',s): ip2vmgw[s[1]]=s[0]
        self.tvmss.selection_set()
        loaded_dpc=[]
        for iid in self.tvmss.get_children():
            if len(self.tvmss.get_children(iid))!=0:
                loaded_dpc.append(iid)
        for iid in self.tvmgw.selection():
            if self.tvmgw.item(iid,option='tag')[0]!='pcm':continue
            values=self.tvmgw.item(iid,option='values')
            'cgr,ncgr,pcm,admin,oper,usage,tsl'
            cgr,pcm,tsl=values[0],values[2],values[6].split('-')[0].split(',')[0]
            IPs=cgr2ip[int(cgr)]
            try: vmgw=ip2vmgw[IPs[0]]
            except:
                try: vmgw=ip2vmgw[IPs[1]]
                except: continue
            print(cgr,pcm,tsl,IPs,vmgw)
            s=self.nemss.send('ZRCI:SEA=14:MGW=%s,TERMID=%s-%s;'%(vmgw,pcm,tsl))
            self.write_to_terminal(self.logmss,s)
            cgr,net,spc,ccspcm,vmgw=re.findall('\s+CGR   : (\w+) [\s\S]+ NET  : (\w+).{14}(\w+)/\d+ +CCSPCM : (\d+)[\s\S]+\nMGW   : (\w+)',s)[0]
            if loaded_dpc.count('%s %s'%(net,spc))==0:
                self.state1mss_load_circuits('%s %s'%(net,spc))
                loaded_dpc.append('%s %s'%(net,spc))
            self.tvmss.selection_add('pcm %s %s'%(int(cgr),int(ccspcm)))
            self.tvmss.see('pcm %s %s'%(int(cgr),int(ccspcm)))
        self.status.set('ok')
    def destroy(self):
        self.event_delete('<<Return+1>>')
        try:self.nemss.destroy()
        except:pass
        try: self.nemgw.destroy()
        except:pass
        tk.Frame.destroy(self)

