import tkinter as tk
import tkinter.ttk as ttk
from SSH import *
import time
from tkinter.messagebox import askyesno



class Signalling(tk.Frame):
    def __init__(self,master):
        tk.Frame.__init__(self,master)
        self.rowconfigure(10,weight=1)
        self.columnconfigure(10,weight=1)
        style=ttk.Style()
        style.configure('mgw_signalling.Treeview',font=('Terminal',13))
        self.tv=ttk.Treeview(self,style='mgw_signalling.Treeview')
        #self.tv=ttk.Treeview(self)
        self.tvYScroll=tk.Scrollbar(self,orient=tk.VERTICAL,command=self.tv.yview)
        self.tvXScroll=tk.Scrollbar(self,orient=tk.HORIZONTAL,command=self.tv.xview)
        self.tv.grid(row=5,column=5,columnspan=10,rowspan=10,sticky='NEWS')
        self.tvYScroll.grid(row=5,column=15,rowspan=10,sticky='NSE')
        self.tvXScroll.grid(row=15,column=5,columnspan=10,sticky='SWE')
        self.tv['yscrollcommand']=self.tvYScroll.set
        self.tv['xscrollcommand']=self.tvXScroll.set
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
    def state1(self):
        self.all_unbind()
        hostname,protocol,type,username,password=self.sessions['MGWs'][self.tv.selection()[0]]
        username,password=decipher(username),decipher(password)
        ne_name=self.tv.item(self.tv.selection()[0],option='text')
        self.status.set('Trying to connect to %s, ip=%s'%(ne_name,hostname))
        self.tv.heading('#0',text=ne_name)
        self.tv.delete(*self.tv.get_children())
        try: self.ne.destroy()
        except:pass
        def submenu(event):
            for child in self.tv.winfo_children():child.destroy()
            def create_by_tag():
                if self.tv.selection()==[]:return
                tag=self.tv.item(self.tv.selection()[0],option='tags')[0]
                func_by_tag={\
                    'DESTINATION-POINT-CODE':self.create_dpc,
                    'LINK':self.create_link,
                    'LINKSET':self.create_linkset,
                    'ROUTE':self.create_route
                }
                func_by_tag[tag](self.tv.selection()[0])
            menu=tk.Menu(self.tv,tearoff=0)
            menu.add_command(label='Update', command=lambda:\
                self.update_items_by_tag(self.tv.item(self.tv.selection()[0],\
                                                      option='tags')[0],selected_item=self.tv.selection()[0]))
            menu.add_command(label='Create',command=create_by_tag)
            menu.add_command(label='Delete',command=lambda: self.delete_item(self.tv.selection()[0]))
            menu.add_command(label='Show mgw list',command=lambda: self.state0())
            menu.post(event.x_root,event.y_root)
        self.tv.bind('<3>',submenu)
        self.ne=SSH(hostname,username,password,ne_name=ne_name)
        t1=time.time()
        while time.time()-t1<60 and self.ne.exceptError=='' and self.ne.Alive==False: time.sleep(1)
        if self.ne.Alive==False:
            self.status.set("no connect %s,%s %s"%(ne_name,hostname,self.ne.exceptError))
            return
        self.update_items_by_tag('DESTINATION-POINT-CODE',index=0)
        self.update_items_by_tag('LINK',index=1)
        self.update_items_by_tag('LINKSET',index=2)
        self.update_items_by_tag('ROUTE',index=3)
    def delete_item(self,iid):
        prev=self.tv.prev(iid)
        tag=self.tv.item(iid,option='tags')[0]
        text=self.tv.item(iid,option='text')
        values=self.tv.item(iid,option='values')
        values=values[int(len(values)/2):]
        if not askyesno('Delete %s?'%tag,text): return
        cmd={'DESTINATION-POINT-CODE':'delete signaling ss7 destination-point-code name {}',\
             'LINK':'delete signaling ss7 link id {}',\
             'LINKSET':'delete signaling ss7 linkset name {}',\
             'ROUTE':'delete signaling ss7 route name {}'}
        s=self.ne.send(cmd[tag].format(values[0]))
        print(s)
        self.update_items_by_tag(tag,selected_item=prev)
    def create_dpc(self,template_iid=None):
        if template_iid==None:return
        tag1=self.tv.item(template_iid,option='tags')[1]
        if tag1=='item':
            values=self.tv.item(template_iid,'values')
            k=values[:int(len(values)/2)]
            v=values[int(len(values)/2):]
            d=dict(zip(k,v))
        root=tk.Toplevel(self.winfo_toplevel())
        root.title('Create DESTINATION-POINT-CODE')
        '''add signaling ss7 destination-point-code associated-service-access-point-name SAPNA0 name xxx point-code 3333 service-access-point-name SAPNA0 type remote sls-number 0 special-ansi-sltm-mode enable'''
        tk.Label(root,text='destination-point-code-name').grid(row=0,column=0)
        tk.Label(root,text='service-access-point-name').grid(row=1,column=0)
        tk.Label(root,text='destination-point-code').grid(row=2,column=0)
        tk.Label(root,text='associated-service-access-point-name').grid(row=3,column=0)
        tk.Label(root,text='type').grid(row=4,column=0)
        tk.Label(root,text='sls-number').grid(row=5,column=0)
        tk.Label(root,text='special-ansi-sltm-mode').grid(row=6,column=0)
        dest_name,sap_name,dest_code,sls_number,dest_type,sltm,asap_name,status=[tk.StringVar() for i in range(8)]
        if tag1=='item':
            dest_name.set(d['destination-point-code-name'])
            sap_name.set(d['sap-name'])
            dest_code.set(d['destination-point-code'])
            sls_number.set(d['sls-number'])
            dest_type.set(d['destination-type'].lower())
            sltm.set(d['sltm-option'].lower())
            try:asap_name.set(d['Associated Service Access Point Name'])
            except:pass
            '''[x.set(y) for x,y in zip(\
                (dest_name,sap_name,dest_code,sls_number,dest_type,sltm,asap_name,status),\
                (d['destination-point-code-name'],d['sap-name'],d['destination-point-code'],\
                d['sls-number'],d['destination-type'].lower(),d['sltm-option'].lower(),d['Associated Service Access Point Name'],\
                 d['dpc-status']))]'''
        sap_names=[]
        for s in self.ne.send('show signaling service-access-point all').split('service-access-point-name               :   ')[1:]:
            sap_names.append(s.split(' ')[0])
        w1=tk.Entry(root,width=80,textvariable=dest_name)
        w1.grid(row=0,column=1)
        w1.focus_set()
        w1.select_range(0,80)
        tk.OptionMenu(root,sap_name,*sap_names).grid(row=1,column=1)
        tk.Entry(root,width=80,textvariable=dest_code).grid(row=2,column=1)
        tk.OptionMenu(root,asap_name,*sap_names).grid(row=3,column=1)
        tk.OptionMenu(root,dest_type,'adjacent','adjacent-bsc','remote').grid(row=4,column=1)
        tk.Entry(root,width=80,textvariable=sls_number).grid(row=5,column=1)
        tk.OptionMenu(root,sltm,'disable','enable').grid(row=6,column=1)
        text=tk.Text(root,width=80,height=4,wrap=tk.WORD)
        text.grid(row=7,column=0,columnspan=2)
        text2=tk.Text(root,width=80,height=8,wrap=tk.WORD)
        text2.grid(row=8,column=0,columnspan=2)
        def func_create():
            if dest_type.get()=='remote':
                s1='add signaling ss7 destination-point-code name {} point-code {} service-access-point-name {} type {} sls-number {} special-ansi-sltm-mode {}'.format(\
                dest_name.get(),dest_code.get(),sap_name.get(),dest_type.get(),sls_number.get(),sltm.get())
            else:s1='add signaling ss7 destination-point-code associated-service-access-point-name {} name {} point-code {} service-access-point-name {} type {} sls-number {} special-ansi-sltm-mode {}'.format(\
                asap_name.get(),dest_name.get(),dest_code.get(),sap_name.get(),dest_type.get(),sls_number.get(),sltm.get())
            create.configure(state=tk.DISABLED)
            text2.insert(tk.INSERT,s1)
            s=self.ne.send(s1)
            text2.insert(tk.INSERT,s)
            self.update_items_by_tag('DESTINATION-POINT-CODE',template_iid)
            create.configure(state=tk.NORMAL)
        def func_generate():
            if dest_type.get()=='remote':
                s1='add signaling ss7 destination-point-code name {} point-code {} service-access-point-name {} type {} sls-number {} special-ansi-sltm-mode {}'.format(\
                dest_name.get(),dest_code.get(),sap_name.get(),dest_type.get(),sls_number.get(),sltm.get())
            else:s1='add signaling ss7 destination-point-code associated-service-access-point-name {} name {} point-code {} service-access-point-name {} type {} sls-number {} special-ansi-sltm-mode {}'.format(\
                asap_name.get(),dest_name.get(),dest_code.get(),sap_name.get(),dest_type.get(),sls_number.get(),sltm.get())
            text.insert(tk.INSERT,s1)
        create=tk.Button(root,text='Create DPC in MGW',command=func_create)
        cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
        generate=tk.Button(root,text='only Generate command',command=func_generate)
        generate.grid(row=9,column=0)
        cancel.grid(row=9,column=1)
        create.grid(row=10,column=0)
        root.wait_window()
    def create_linkset(self,template_iid=None):
        root=tk.Toplevel(self.winfo_toplevel())
        root.title('Create LINKSET')
        tk.Label(root,text='linkset id').grid(row=0,column=0)
        tk.Label(root,text='linkset name').grid(row=1,column=0)
        tk.Label(root,text='link-id').grid(row=2,column=0)
        linkset_id,linkset_name,link_id=[tk.StringVar() for i in range(3)]
        w1=tk.Entry(root,width=80,textvariable=linkset_id)
        w1.grid(row=0,column=1)
        w1.focus_set()
        w1.select_range(0,80)
        tk.Entry(root,width=80,textvariable=linkset_name).grid(row=1,column=1)
        tk.Entry(root,width=80,textvariable=link_id).grid(row=2,column=1)
        text=tk.Text(root,width=80,height=4,wrap=tk.WORD)
        text.grid(row=3,column=0,columnspan=2)
        text2=tk.Text(root,width=80,height=8,wrap=tk.WORD)
        text2.grid(row=4,column=0,columnspan=2)
        def func_create():
            s1='add signaling ss7 linkset id {} name {} link-id {} '.format(\
                linkset_id.get(),linkset_name.get(),link_id.get())
            create.configure(state=tk.DISABLED)
            text2.insert(tk.INSERT,s1)
            s=self.ne.send(s1)
            text2.insert(tk.INSERT,s)
            self.update_items_by_tag('LINKSET',template_iid)
            create.configure(state=tk.NORMAL)
        def func_generate():
            s1='add signaling ss7 linkset id {} name {} link-id {} '.format(\
                linkset_id.get(),linkset_name.get(),link_id.get())
            text.insert(tk.INSERT,s1)
        create=tk.Button(root,text='Create Linkset in MGW',command=func_create)
        cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
        generate=tk.Button(root,text='only Generate command',command=func_generate)
        generate.grid(row=5,column=0)
        cancel.grid(row=5,column=1)
        create.grid(row=6,column=0)
        root.wait_window()
    def create_link(self,template_iid=None):
        if template_iid==None:return
        tag1=self.tv.item(template_iid,option='tags')[1]
        if tag1=='item':
            values=self.tv.item(template_iid,'values')
            k=values[:int(len(values)/2)]
            v=values[int(len(values)/2):]
            d=dict(zip(k,v))
        root=tk.Toplevel(self.winfo_toplevel())
        root.title('Create LINK')
        tk.Label(root,text='link-id').grid(row=0,column=0)
        tk.Label(root,text='self-point-code-name').grid(row=1,column=0)
        tk.Label(root,text='destination-point-code-name').grid(row=2,column=0)
        tk.Label(root,text='node').grid(row=3,column=0)
        tk.Label(root,text='slc').grid(row=4,column=0)
        tk.Label(root,text='Link Rate').grid(row=5,column=0)
        tk.Label(root,text='PCM Id').grid(row=6,column=0)
        tk.Label(root,text='TimeSlot').grid(row=7,column=0)
        tk.Label(root,text='Number of Timeslots').grid(row=8,column=0)
        tk.Label(root,text='link-bandwidth').grid(row=9,column=0)
        tk.Label(root,text='spmc-link').grid(row=10,column=0)
        tk.Label(root,text='Link Profile').grid(row=11,column=0)
        tk.Label(root,text='Timer Profile').grid(row=12,column=0)
        id,opcname,dpcname,node,slc,rate,pcm,tsl,nbrTsl,band,spmc,linkprofile,timerprofile=[tk.StringVar() for i in range(13)]
        if tag1=='item':
            [x.set(y) for x,y in zip(\
                (id,opcname,dpcname,node,slc,rate,pcm,tsl,nbrTsl,band,spmc,linkprofile,timerprofile),\
                (d['link-id'],d['self-point-code-name'],d['destination-point-code-name'],\
                d['node'],d['slc'],d['Link Rate'],d['PCM Id'],d['TimeSlot'],d['Number of Timeslots'],\
                d['link-bandwidth'].lower(),d['spmc-link'],d['Link Profile'],d['Timer Profile']))]
        dpc_names=[]
        for iid in self.tv.get_children('DESTINATION-POINT-CODE')[1:]:
            values=self.tv.item(iid,option='values')
            values=values[int(len(values)/2):]
            dpc_names.append(values[0])
        opc_names=[]
        s=self.ne.send('show signaling ss7 own-point-code all')
        for s1 in s.split('self-point-code-name                    : ')[1:]:
            opc_names.append(s1.split(' ')[0])
        w1=tk.Entry(root,width=80,textvariable=id)
        w1.grid(row=0,column=1)
        w1.focus_set()
        w1.select_range(0,80)
        tk.OptionMenu(root,opcname,*opc_names).grid(row=1,column=1)
        tk.OptionMenu(root,dpcname,*dpc_names).grid(row=2,column=1)
        tk.Entry(root,width=80,textvariable=node).grid(row=3,column=1)
        tk.Entry(root,width=80,textvariable=slc).grid(row=4,column=1)
        tk.Entry(root,width=80,textvariable=rate).grid(row=5,column=1)
        tk.Entry(root,width=80,textvariable=pcm).grid(row=6,column=1)
        tk.Entry(root,width=80,textvariable=tsl).grid(row=7,column=1)
        tk.Entry(root,width=80,textvariable=nbrTsl).grid(row=8,column=1)
        tk.OptionMenu(root,band,'narrowband','broadband','hsl','hsl_with_coo').grid(row=9,column=1)
        tk.OptionMenu(root,spmc,'yes','no').grid(row=10,column=1)
        tk.Entry(root,width=80,textvariable=linkprofile).grid(row=11,column=1)
        tk.Entry(root,width=80,textvariable=timerprofile).grid(row=12,column=1)
        text=tk.Text(root,width=80,height=4,wrap=tk.WORD)
        text.grid(row=13,column=0,columnspan=2)
        text2=tk.Text(root,width=80,height=8,wrap=tk.WORD)
        text2.grid(row=14,column=0,columnspan=2)
        def func_ok():
            s1='add signaling ss7 link id {} destination-point-code-name {} own-point-code-name {} bandwidth {} slc {}  link-rate {} mtp2-link-profile {} mtp2-timer-profile {} node-name {} number-of-time-slots {} pcm-id {} spmc-link {} time-slot {}\n'.format(\
                id.get(),dpcname.get(),opcname.get(),band.get(),slc.get(),rate.get(),linkprofile.get(),timerprofile.get(),\
                node.get(),nbrTsl.get(),pcm.get(),spmc.get(),tsl.get())
            create.configure(state=tk.DISABLED)
            text2.insert(tk.INSERT,s1)
            s=self.ne.send(s1)
            text2.insert(tk.INSERT,s)
            self.update_items_by_tag('LINK',template_iid)
            create.configure(state=tk.NORMAL)
        def func_generate():
            text.insert(tk.INSERT,'add signaling ss7 link id {} destination-point-code-name {} own-point-code-name {} bandwidth {} slc {}  link-rate {} mtp2-link-profile {} mtp2-timer-profile {} node-name {} number-of-time-slots {} pcm-id {} spmc-link {} time-slot {}\n'.format(\
                id.get(),dpcname.get(),opcname.get(),band.get(),slc.get(),rate.get(),linkprofile.get(),timerprofile.get(),\
                node.get(),nbrTsl.get(),pcm.get(),spmc.get(),tsl.get()))
        create=tk.Button(root,text='Create Link in MGW',command=func_ok)
        cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
        generate=tk.Button(root,text='only Generate command',command=func_generate)
        generate.grid(row=15,column=0)
        cancel.grid(row=15,column=1)
        create.grid(row=16,column=0)
        root.wait_window()
    def create_route(self,template_iid=None):
        if template_iid==None:return
        tag1=self.tv.item(template_iid,option='tags')[1]
        if tag1=='item':
            values=self.tv.item(template_iid,'values')
            k=values[:int(len(values)/2)]
            v=values[int(len(values)/2):]
            d=dict(zip(k,v))
        root=tk.Toplevel(self.winfo_toplevel())
        root.title('Create ROUTE')
        '''add signaling ss7 route destination-point-code-name xxx id 1 name nnn own-point-code-name xxx linkset-name  xxx priority 1'''
        tk.Label(root,text='route-id').grid(row=0,column=0)
        tk.Label(root,text='route-name').grid(row=1,column=0)
        tk.Label(root,text='destination-point-code-name').grid(row=2,column=0)
        tk.Label(root,text='own-point-code-name').grid(row=3,column=0)
        tk.Label(root,text='linkset-name').grid(row=4,column=0)
        tk.Label(root,text='priority').grid(row=5,column=0)
        dpc_names=[]
        for iid in self.tv.get_children('DESTINATION-POINT-CODE')[1:]:
            values=self.tv.item(iid,option='values')
            values=values[int(len(values)/2):]
            dpc_names.append(values[0])
        linkset_names=[]
        for iid in self.tv.get_children('LINKSET')[1:]:
            values=self.tv.item(iid,option='values')
            values=values[int(len(values)/2):]
            linkset_names.append(values[0])
        opc_names=[]
        s=self.ne.send('show signaling ss7 own-point-code all')
        for s1 in s.split('self-point-code-name                    : ')[1:]:
            opc_names.append(s1.split(' ')[0])
        route_name,route_id,sap_name,spc_name,spc,dpc_name,dpc,linkset_name,linkset_id,priority,route_status,linkset_status,route_management_status=[tk.StringVar() for i in range(13)]
        if tag1=='item':
            [x.set(y) for x,y in zip(\
                (route_name,route_id,sap_name,spc_name,spc,dpc_name,dpc,linkset_name,linkset_id,priority,route_status,linkset_status,route_management_status),\
                (d['route-name'],d['route-id'],d['sap-name'],d['self-point-code-name'],d['self-point-code'],\
                 d['destination-point-code-name'],d['destination-point-code'],d['linkset-name'],d['linkset-id'],\
                d['route-priority'],d['route-status'],d['linkset-status'],d['route-management-status']))]
        w1=tk.Entry(root,width=80,textvariable=route_id)
        w1.grid(row=0,column=1)
        w1.focus_set()
        w1.select_range(0,80)
        tk.Entry(root,width=80,textvariable=route_name).grid(row=1,column=1)
        tk.OptionMenu(root,dpc_name,*dpc_names).grid(row=2,column=1)
        tk.OptionMenu(root,spc_name,*opc_names).grid(row=3,column=1)
        tk.OptionMenu(root,linkset_name,*linkset_names).grid(row=4,column=1)
        tk.OptionMenu(root,priority,'0','1','2','3').grid(row=5,column=1)
        text=tk.Text(root,width=80,height=4,wrap=tk.WORD)
        text.grid(row=6,column=0,columnspan=2)
        text2=tk.Text(root,width=80,height=8,wrap=tk.WORD)
        text2.grid(row=7,column=0,columnspan=2)
        def func_ok():
            s1='add signaling ss7 route destination-point-code-name {} id {} name {} own-point-code-name {} linkset-name {} priority {}\n'.format(\
                dpc_name.get(),route_id.get(),route_name.get(),spc_name.get(),linkset_name.get(),priority.get())
            create.configure(state=tk.DISABLED)
            text2.insert(tk.INSERT,s1)
            s=self.ne.send(s1)
            text2.insert(tk.INSERT,s)
            self.update_items_by_tag('ROUTE')
            create.configure(state=tk.NORMAL)
        def func_generate():
            s1='add signaling ss7 route destination-point-code-name {} id {} name {} own-point-code-name {} linkset-name {} priority {}\n'.format(\
                dpc_name.get(),route_id.get(),route_name.get(),spc_name.get(),linkset_name.get(),priority.get())
            text.insert(tk.INSERT,s1)
        create=tk.Button(root,text='Create Route in MGW',command=func_ok)
        cancel=tk.Button(root,text='Cancel',command=lambda: root.destroy())
        generate=tk.Button(root,text='only Generate command',command=func_generate)
        generate.grid(row=8,column=0)
        cancel.grid(row=8,column=1)
        create.grid(row=9,column=0)
        root.wait_window()
    def update_items_by_tag(self,tag,selected_item=None, index=None):
        cmd={'DESTINATION-POINT-CODE':'show signaling ss7 destination-point-code all',
             'LINK':'show signaling ss7 link all',
             'LINKSET':'show signaling ss7 linkset all',
             'ROUTE':'show signaling ss7 route all'}
        self.status.set('Updating %s'%tag)
        if index==None: index=self.tv.index(tag)
        try: self.tv.delete(tag)
        except:pass
        self.tv.insert('',index,iid=tag,text=tag,tags=(tag,'tag'))
        s=self.ne.send(cmd[tag])
        for s1 in s.split(tag)[1:]:
            D={}
            for i in s1.split('\n')[1:]:
                if i.find(':')==-1:continue
                name,value=i.split(':')
                name,value=name.strip(),value.strip()
                D[name]=value
            tmp=' '.join(['%-12s']*len(D))
            self.tv.insert(tag,'end',id='%s=%s'%(tag,tuple(D.values())[0]),text=tmp%tuple(D.values()),values=tuple(D.keys())+tuple(D.values()),tags=(tag,'item'))
        iid=self.tv.get_children(tag)[0]
        values=self.tv.item(iid,option='values')
        keys=[]
        for i in values[:int(len(values)/2)]:
            if len(i)>12: keys.append(i[:4]+i[-5:])
            else: keys.append(i)
        tmp=' '.join(['%-12s']*len(keys))
        self.tv.insert(tag,0,id='header of %s'%tag,text=tmp%tuple(keys),tags=(tag,'header'))
        if selected_item!=None:
            self.tv.see(selected_item)
            self.tv.selection_set(selected_item)
        self.status.set('ok')
