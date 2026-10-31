import copy,queue,threading,time,tkinter as tk,webbrowser
from tkinter import ttk,messagebox
from core import GitHub,FLAGS,FEATURES,COUNTRIES,TEXTS,get,build

class Panel:
    def __init__(self,root):
        self.root=root;self.original=None;self.sha=None;self.values={};self.queue=queue.Queue();self.busy=False;self.pending_raw=None
        root.title('Targa Scanner · Amministrazione');root.geometry('960x780');root.minsize(780,650)
        outer=ttk.Frame(root,padding=16);outer.pack(fill='both',expand=True)
        ttk.Label(outer,text='Targa Scanner',font=('Segoe UI',20,'bold')).pack(anchor='w')
        ttk.Label(outer,text='Controllo remoto · le modifiche arrivano all’app entro il prossimo controllo, minimo 30 minuti.').pack(anchor='w',pady=(0,12))
        connection=ttk.Frame(outer);connection.pack(fill='x')
        ttk.Label(connection,text='Token GitHub:').pack(side='left')
        self.token=tk.StringVar();ttk.Entry(connection,textvariable=self.token,show='•',width=45).pack(side='left',padx=8)
        ttk.Button(connection,text='Come collegarmi',command=self.help).pack(side='left')
        self.status=tk.StringVar(value='Premi Rileggi da GitHub. Il token serve soltanto per pubblicare e non viene salvato.')
        ttk.Label(outer,textvariable=self.status,wraplength=900).pack(anchor='w',pady=10)
        self.tabs=ttk.Notebook(outer);self.tabs.pack(fill='both',expand=True)
        general=self.tab('App e messaggi');features=self.tab('Controlli Italia');countries=self.tab('Paesi');access=self.tab('Installazioni bloccate')
        for i,(path,label) in enumerate(FLAGS.items()):self.checkbox(general,path,label,i//2,i%2)
        for i,(path,label) in enumerate(TEXTS.items()):
            row=5+i;ttk.Label(general,text=label).grid(row=row,column=0,sticky='w',pady=5)
            var=tk.StringVar();self.values[path]=var;ttk.Entry(general,textvariable=var,width=62).grid(row=row,column=1,sticky='ew',pady=5)
        for i,(key,label) in enumerate(FEATURES.items()):self.checkbox(features,'features.'+key,label,i//2,i%2)
        ttk.Label(features,text='Questi interruttori riguardano le verifiche italiane.\nLe altre opzioni preparatorie del JSON non sono modificabili da questo pannello.').grid(row=8,column=0,columnspan=2,sticky='w',pady=20)
        for i,(key,label) in enumerate(COUNTRIES.items()):self.checkbox(countries,'countries.'+key,label,i//2,i%2)
        ttk.Label(access,text='Un codice per riga, copiato da Impostazioni → Informazioni nell’app.\nIl file è pubblico: inserisci solo i codici, mai nomi o altre informazioni personali.').pack(anchor='w',pady=8)
        self.blocked=tk.Text(access,width=85,height=15,wrap='none');self.blocked.pack(fill='both',expand=True)
        buttons=ttk.Frame(outer);buttons.pack(fill='x',pady=(12,0))
        self.load_button=ttk.Button(buttons,text='Rileggi da GitHub',command=self.reload);self.load_button.pack(side='left')
        self.save_button=ttk.Button(buttons,text='Rivedi modifiche e pubblica',command=self.review,state='disabled');self.save_button.pack(side='right')
        ttk.Button(buttons,text='Stato firma su GitHub',command=lambda:webbrowser.open('https://github.com/forti21/targa-scanner-config/actions')).pack(side='right',padx=8)
        root.after(100,self.drain)
    def tab(self,title):
        holder=ttk.Frame(self.tabs);self.tabs.add(holder,text=title)
        canvas=tk.Canvas(holder,highlightthickness=0);bar=ttk.Scrollbar(holder,orient='vertical',command=canvas.yview)
        canvas.configure(yscrollcommand=bar.set);bar.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
        frame=ttk.Frame(canvas,padding=12);item=canvas.create_window((0,0),window=frame,anchor='nw')
        frame.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda e:canvas.itemconfigure(item,width=e.width));return frame
    def checkbox(self,parent,path,label,row,column):
        var=tk.BooleanVar();self.values[path]=var
        ttk.Checkbutton(parent,text=label,variable=var).grid(row=row,column=column,sticky='w',padx=(0,30),pady=7)
    def help(self):
        messagebox.showinfo('Collegamento GitHub','Crea un Fine-grained personal access token su GitHub.\n\nRepository: soltanto forti21/targa-scanner-config\nPermesso: Contents → Read and write\nScegli una scadenza e incollalo nel campo Token.\n\nNon servono permessi amministratore o accesso ai Secrets. Il token resta solo in memoria finché il programma è aperto. Non usare la chiave privata di firma.\n\nPuoi leggere la configurazione anche senza token.')
    def run(self,work,done):
        if self.busy:return
        self.busy=True;self.load_button.configure(state='disabled');self.save_button.configure(state='disabled')
        def task():
            try:self.queue.put((done,work(),None))
            except Exception as e:self.queue.put((done,None,str(e)))
        threading.Thread(target=task,daemon=True).start()
    def drain(self):
        try:
            while True:
                done,value,error=self.queue.get_nowait();self.busy=False;self.load_button.configure(state='normal')
                self.save_button.configure(state='normal' if self.original else 'disabled')
                if error:self.status.set(error);messagebox.showerror('Operazione non completata',error)
                else:done(value)
        except queue.Empty:pass
        self.root.after(100,self.drain)
    def read_form(self):return build(self.original,{k:v.get() for k,v in self.values.items()},self.blocked.get('1.0','end'))
    def reload(self):
        if self.original:
            try:dirty=bool(self.read_form()[1])
            except ValueError:dirty=True
            if dirty and not messagebox.askyesno('Rileggi configurazione','Scartare le modifiche non pubblicate e rileggere da GitHub?'):return
        self.pending_raw=None
        self.status.set('Lettura della configurazione corrente…');client=GitHub(self.token.get())
        self.run(client.load,self.loaded)
    def loaded(self,result):
        self.original,self.sha=result
        for path,var in self.values.items():
            default=True if path.startswith(('features.','countries.')) or path in ['app_control.enabled','app_control.searches_enabled','search.new_searches_enabled'] else False
            value=get(self.original,path,default if isinstance(var,tk.BooleanVar) else '')
            var.set(value)
        self.blocked.delete('1.0','end');self.blocked.insert('1.0','\n'.join(get(self.original,'access_control.blocked_installation_tokens',[])))
        self.status.set('Configurazione letta · revisione '+str(self.original['config_revision']));self.save_button.configure(state='normal')
    def review(self):
        if not self.original:return
        try:config,changes=self.read_form()
        except ValueError as e:messagebox.showerror('Controlla i campi',str(e));return
        if not changes:messagebox.showinfo('Nessuna modifica','La configurazione non è stata modificata.');return
        if not self.token.get().strip():messagebox.showerror('Token necessario','Inserisci il token GitHub. La chiave privata di firma non serve.');return
        dialog=tk.Toplevel(self.root);dialog.title('Controlla prima di pubblicare');dialog.geometry('760x520');dialog.transient(self.root);dialog.grab_set()
        ttk.Label(dialog,text='Nuova revisione: '+str(config['config_revision']),font=('Segoe UI',13,'bold')).pack(anchor='w',padx=16,pady=12)
        box=tk.Text(dialog,wrap='word',height=18);box.pack(fill='both',expand=True,padx=16);box.insert('1.0','\n\n'.join(changes));box.configure(state='disabled')
        ttk.Label(dialog,text='Pubblicherai queste modifiche per gli utenti dell’app.\nLa firma automatica deve riuscire prima che diventino disponibili.').pack(anchor='w',padx=16,pady=12)
        def publish():
            dialog.destroy();self.status.set('Salvataggio su GitHub…');client=GitHub(self.token.get());sha=self.sha
            def saved(result):
                new_sha,raw=result;self.original=copy.deepcopy(config);self.sha=new_sha
                self.pending_raw=raw
                self.status.set('JSON salvato · attendo la pubblicazione firmata…');self.poll(client,raw,time.monotonic()+180)
            self.run(lambda:client.publish(config,sha),saved)
        ttk.Button(dialog,text='Conferma: salva e pubblica',command=publish).pack(side='right',padx=16,pady=12)
        ttk.Button(dialog,text='Torna a modificare',command=dialog.destroy).pack(side='right',pady=12)
    def poll(self,client,raw,deadline):
        if self.pending_raw!=raw:return
        if self.busy:self.root.after(3000,lambda:self.poll(client,raw,deadline));return
        def done(matches):
            if self.pending_raw!=raw:return
            if matches:self.status.set('File firmato pubblicato. Le app lo riceveranno al prossimo controllo.');return
            if time.monotonic()>deadline:
                self.status.set('JSON salvato; firma non confermata. Apri Stato firma su GitHub per controllare il workflow.');return
            self.root.after(5000,lambda:self.poll(client,raw,deadline))
        self.run(lambda:client.signed_matches(raw),done)

if __name__=='__main__':
    root=tk.Tk();Panel(root);root.mainloop()
