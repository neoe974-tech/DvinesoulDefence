"""DVINESOUL DEFENCE - integrated defensive workbench.
Network features are for systems/domains you own or are explicitly authorized to test.
"""
from __future__ import annotations
import json, os, platform, queue, secrets, socket, string, threading, math, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = 'DVINESOUL DEFENCE'
BG='#080d0b'; PANEL='#101a15'; GREEN='#39ff88'; MUTED='#8ba99a'; WHITE='#e7f5ed'
COMMON_PORTS={21:'FTP',22:'SSH',23:'Telnet',25:'SMTP',53:'DNS',80:'HTTP',110:'POP3',143:'IMAP',443:'HTTPS',445:'SMB',3306:'MySQL',3389:'RDP',5432:'PostgreSQL',8080:'HTTP-alt',8443:'HTTPS-alt'}
DEFAULT_PATHS=['admin','login','robots.txt','sitemap.xml','api','backup','uploads','assets','docs','health']
DEFAULT_SUBS=['www','mail','dev','test','api','staging','portal','vpn','ftp','blog','shop','admin']

def valid_url(value):
    u=urlparse(value.strip())
    if u.scheme not in ('http','https') or not u.hostname: raise ValueError('Enter a complete http:// or https:// URL.')
    return value.strip().rstrip('/')+'/'

def load_words(path, defaults):
    if not path: return defaults
    f=Path(path)
    if not f.is_file(): raise ValueError(f'Wordlist not found: {path}')
    words=[x.strip() for x in f.read_text(encoding='utf-8',errors='ignore').splitlines() if x.strip() and not x.lstrip().startswith('#')]
    if not words: raise ValueError('Wordlist is empty.')
    if len(words)>10000: raise ValueError('Wordlist is too large for the GUI (maximum 10,000 entries).')
    return words

def tcp_check(host, port, timeout=.5):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host,port))==0

def http_status(url, timeout=4):
    req=Request(url,headers={'User-Agent':'DvinesoulDefence/0.2 (authorized security audit)'},method='GET')
    try:
        with urlopen(req,timeout=timeout) as r: return r.status
    except HTTPError as e: return e.code

def strength(password):
    if not password: return 0, 'No password entered.'
    classes=sum((any(c.islower() for c in password),any(c.isupper() for c in password),any(c.isdigit() for c in password),any(not c.isalnum() for c in password)))
    score=min(100, len(password)*4 + max(0,classes-1)*8 + (12 if len(set(password))>len(password)*.7 else 0))
    note=('Very short; use a long unique passphrase.' if len(password)<8 else 'Prefer 14+ characters and uniqueness.' if len(password)<14 else 'Good length; uniqueness and breach exposure still matter.')
    return score,note

def make_password(length=20):
    if not 12<=length<=128: raise ValueError('Password length must be between 12 and 128.')
    groups=[string.ascii_lowercase,string.ascii_uppercase,string.digits,'!@#$%^&*()-_=+[]{}?']
    chars=[secrets.choice(g) for g in groups]; pool=''.join(groups)
    chars += [secrets.choice(pool) for _ in range(length-len(chars))]; secrets.SystemRandom().shuffle(chars)
    return ''.join(chars)

class DefenceApp:
 def __init__(self,root):
    self.root=root; root.title(APP_NAME+' | Cybersecurity Workbench'); root.geometry('1180x820'); root.minsize(900,650); root.configure(bg=BG)
    self.events=queue.Queue(); self.findings=[]; self.auth_vars={}; self.jobs=0; self.sniff_stop=threading.Event(); self.sniff_thread=None; self.sniff_packets=0
    self._style(); self._layout(); self.log('Ready. Use only against assets you own or have explicit permission to assess.'); self.log(f'{platform.platform()} | Python {platform.python_version()}'); root.after(100,self._drain)
 def _style(self):
    s=ttk.Style(); s.theme_use('clam'); s.configure('TNotebook',background=BG,borderwidth=0); s.configure('TNotebook.Tab',background=PANEL,foreground=MUTED,padding=(12,8),font=('TkFixedFont',9,'bold')); s.map('TNotebook.Tab',background=[('selected','#193126')],foreground=[('selected',GREEN)]); s.configure('Treeview',background=PANEL,fieldbackground=PANEL,foreground=WHITE,rowheight=24); s.configure('Treeview.Heading',background='#193126',foreground=GREEN)
 def _layout(self):
    h=tk.Frame(self.root,bg=BG,padx=18,pady=10); h.pack(fill='x'); tk.Label(h,text='▲ DVINESOUL DEFENCE ▲',bg=BG,fg=GREEN,font=('TkFixedFont',22,'bold')).pack(anchor='w'); tk.Label(h,text='UNIFIED CYBERSECURITY WORKBENCH / DEFENSIVE OPERATIONS',bg=BG,fg=MUTED,font=('TkFixedFont',9)).pack(anchor='w'); self.status=tk.StringVar(value='● READY'); tk.Label(h,textvariable=self.status,bg=BG,fg=GREEN,font=('TkFixedFont',10,'bold')).pack(anchor='e')
    self.nb=ttk.Notebook(self.root); self.nb.pack(fill='both',expand=True,padx=12,pady=4)
    self.tabs={}
    for key,title in [('overview','OVERVIEW'),('surface','THREAT SURFACE'),('ports','PORT SCANNER'),('dirs','DIRECTORY DISCOVERY'),('subs','SUBDOMAIN ENUM'),('sniff','PACKET SNIFFER'),('audit','SYSTEM AUDIT'),('password','PASSWORD SUITE'),('keysec','KEYLOGGER LAB')]:
     f=tk.Frame(self.nb,bg=BG); self.tabs[key]=f; self.nb.add(f,text=title)
    self._overview(); self._ports(); self._dirs(); self._subs(); self._surface(); self._sniff(); self._audit(); self._password(); self._keysec()
    foot=tk.Frame(self.root,bg=BG,padx=12,pady=6); foot.pack(fill='x'); tk.Label(foot,text='LIVE EVENT CONSOLE',bg=BG,fg=GREEN,font=('TkFixedFont',9,'bold')).pack(anchor='w'); self.console=tk.Text(foot,height=6,bg='#050806',fg=GREEN,insertbackground=GREEN,relief='flat',font=('TkFixedFont',9),wrap='word'); self.console.pack(fill='x'); self.console.configure(state='disabled'); row=tk.Frame(foot,bg=BG); row.pack(fill='x',pady=4); self.button(row,'CLEAR LOG',self.clear_log).pack(side='left'); self.button(row,'EXPORT JSON REPORT',self.export).pack(side='right')
 def label(self,parent,text): tk.Label(parent,text=text,bg=BG,fg=WHITE,font=('TkFixedFont',10)).pack(anchor='w',padx=16,pady=(12,3))
 def entry(self,parent,default='',width=48):
    v=tk.StringVar(value=default); e=tk.Entry(parent,textvariable=v,bg=PANEL,fg=WHITE,insertbackground=WHITE,width=width,relief='flat'); e.pack(anchor='w',padx=16,pady=3); return v
 def button(self,parent,text,cmd): return tk.Button(parent,text=text,command=cmd,bg=PANEL,fg=GREEN,activebackground='#214332',activeforeground=WHITE,relief='flat',padx=12,pady=7,font=('TkFixedFont',9,'bold'),cursor='hand2')
 def auth(self,parent):
    if not self.auth_vars[parent].get(): messagebox.showwarning('Authorization required','Confirm you own this target or have explicit permission to test it.'); return False
    return True
 def auth_box(self,parent):
    var=tk.BooleanVar(value=False); self.auth_vars[parent]=var; tk.Checkbutton(parent,text='I confirm this target is mine or explicitly authorized for testing.',variable=var,bg=BG,fg=WHITE,selectcolor=PANEL,activebackground=BG,activeforeground=GREEN).pack(anchor='w',padx=16,pady=7)
 def _overview(self):
    f=self.tabs['overview']; tk.Label(f,text='OPERATIONS OVERVIEW',bg=BG,fg=GREEN,font=('TkFixedFont',15,'bold')).pack(anchor='w',padx=18,pady=18); tk.Label(f,text='Integrated tools with real results, explicit scope confirmation, and exportable evidence.',bg=BG,fg=WHITE).pack(anchor='w',padx=18); 
    for title,desc in [('Threat surface','Authorized TCP service inventory plus optional web path checks.'),('Discovery','Directory checks and DNS subdomain resolution using provided or built-in wordlists.'),('Packet capture','Optional Scapy-based passive capture; requires suitable permissions and interface support.'),('Local audit','Machine facts and selected defensive configuration observations.'),('Password suite','Local heuristic assessment and cryptographically secure password generation.')]:
     box=tk.Frame(f,bg=PANEL,padx=12,pady=10,highlightbackground='#254735',highlightthickness=1); box.pack(fill='x',padx=18,pady=5); tk.Label(box,text=title.upper(),bg=PANEL,fg=GREEN,font=('TkFixedFont',10,'bold')).pack(anchor='w'); tk.Label(box,text=desc,bg=PANEL,fg=WHITE).pack(anchor='w',pady=(4,0))
 def _ports(self):
    f=self.tabs['ports']; self.label(f,'Target hostname or IP'); self.porthost=self.entry(f,'127.0.0.1'); self.label(f,'Port range (maximum 1024 ports)'); self.portrange=self.entry(f,'1-128'); self.auth_box(f); self.button(f,'START PORT SCAN',self.start_ports).pack(anchor='w',padx=16,pady=8); self.porttree=ttk.Treeview(f,columns=('port','state','service'),show='headings');
    for c,t,w in [('port','PORT',100),('state','STATE',130),('service','SERVICE LABEL',220)]: self.porttree.heading(c,text=t); self.porttree.column(c,width=w)
    self.porttree.pack(fill='both',expand=True,padx=16,pady=8)
 def _dirs(self):
    f=self.tabs['dirs']; self.label(f,'Base URL (HTTP or HTTPS)'); self.dirurl=self.entry(f,'http://127.0.0.1'); self.label(f,'Optional wordlist file (blank uses built-in safe starter list)'); row=tk.Frame(f,bg=BG); row.pack(anchor='w'); self.dirword=tk.StringVar(); tk.Entry(row,textvariable=self.dirword,bg=PANEL,fg=WHITE,width=55).pack(side='left',padx=16); self.button(row,'BROWSE',lambda:self.pick(self.dirword)).pack(side='left'); self.auth_box(f); self.button(f,'RUN DIRECTORY DISCOVERY',self.start_dirs).pack(anchor='w',padx=16,pady=8); self.dirout=tk.Text(f,bg=PANEL,fg=WHITE,height=14); self.dirout.pack(fill='both',expand=True,padx=16,pady=8)
 def _subs(self):
    f=self.tabs['subs']; self.label(f,'Domain name (without scheme)'); self.subdomain=self.entry(f,'example.com'); self.label(f,'Optional subdomain wordlist (blank uses built-in starter list)'); row=tk.Frame(f,bg=BG); row.pack(anchor='w'); self.subword=tk.StringVar(); tk.Entry(row,textvariable=self.subword,bg=PANEL,fg=WHITE,width=55).pack(side='left',padx=16); self.button(row,'BROWSE',lambda:self.pick(self.subword)).pack(side='left'); self.auth_box(f); self.button(f,'ENUMERATE SUBDOMAINS',self.start_subs).pack(anchor='w',padx=16,pady=8); self.subout=tk.Text(f,bg=PANEL,fg=WHITE,height=14); self.subout.pack(fill='both',expand=True,padx=16,pady=8)
 def _surface(self):
    f=self.tabs['surface']; self.label(f,'Authorized host or domain'); self.surfhost=self.entry(f,'127.0.0.1'); self.label(f,'Optional web base URL (blank skips HTTP path checks)'); self.surfurl=self.entry(f,''); self.label(f,'Optional directory wordlist'); row=tk.Frame(f,bg=BG); row.pack(anchor='w'); self.surfword=tk.StringVar(); tk.Entry(row,textvariable=self.surfword,bg=PANEL,fg=WHITE,width=55).pack(side='left',padx=16); self.button(row,'BROWSE',lambda:self.pick(self.surfword)).pack(side='left'); self.auth_box(f); self.button(f,'RUN THREAT SURFACE INVENTORY',self.start_surface).pack(anchor='w',padx=16,pady=8); self.surfout=tk.Text(f,bg=PANEL,fg=WHITE,height=12); self.surfout.pack(fill='both',expand=True,padx=16,pady=8)
 def _sniff(self):
    f=self.tabs['sniff']; tk.Label(f,text='PASSIVE PACKET CAPTURE',bg=BG,fg=GREEN,font=('TkFixedFont',14,'bold')).pack(anchor='w',padx=16,pady=14); tk.Label(f,text='Captures packet metadata only. Requires Scapy and capture permissions. Select a real interface such as eth0 or wlan0; capture only on networks you are authorized to monitor.',bg=BG,fg=WHITE,wraplength=900,justify='left').pack(anchor='w',padx=16)
    row0=tk.Frame(f,bg=BG); row0.pack(anchor='w',padx=16,pady=(10,2)); tk.Label(row0,text='Interface:',bg=BG,fg=MUTED).pack(side='left',padx=(0,8)); self.sniffiface=tk.StringVar(value='')
    self.sniffcombo=ttk.Combobox(row0,textvariable=self.sniffiface,width=28,state='normal'); self.sniffcombo.pack(side='left',padx=(0,8)); self.button(row0,'REFRESH INTERFACES',self.refresh_sniff_interfaces).pack(side='left')
    row=tk.Frame(f,bg=BG); row.pack(anchor='w',padx=16,pady=8); self.button(row,'START CAPTURE',self.start_sniff).pack(side='left',padx=(0,8)); self.button(row,'STOP CAPTURE',self.stop_sniff).pack(side='left',padx=(0,8)); self.button(row,'CLEAR PACKETS',lambda:self.sniffout.delete('1.0','end')).pack(side='left')
    self.sniffstate=tk.StringVar(value='Capture idle. Refresh interfaces, select one, then start.'); tk.Label(f,textvariable=self.sniffstate,bg=BG,fg=GREEN,wraplength=900,justify='left').pack(anchor='w',padx=16,pady=4)
    self.sniffout=tk.Text(f,bg=PANEL,fg=WHITE); self.sniffout.pack(fill='both',expand=True,padx=16,pady=8); self.refresh_sniff_interfaces()
 def refresh_sniff_interfaces(self):
    try:
     from scapy.all import get_if_list
     names=get_if_list()
     self.sniffcombo['values']=names
     if names and self.sniffiface.get() not in names: self.sniffiface.set(names[0])
     self.sniffstate.set(f'{len(names)} interface(s) detected. If capture fails, check Scapy and packet-capture permissions.')
     self.log('Packet interfaces: '+(', '.join(names) if names else 'none detected'))
    except Exception as e:
     hint = ' On Windows, install Npcap from https://npcap.com/ and restart the app.' if platform.system() == 'Windows' else ' On Kali/Debian, install Scapy with: sudo apt install python3-scapy.'
     self.sniffstate.set(f'Could not list interfaces: {type(e).__name__}: {e}.{hint}')
     self.log(f'Interface discovery failed: {type(e).__name__}: {e}.{hint}')
 def _audit(self):
    f=self.tabs['audit']; tk.Label(f,text='LOCAL SYSTEM AUDIT',bg=BG,fg=GREEN,font=('TkFixedFont',14,'bold')).pack(anchor='w',padx=16,pady=14); tk.Label(f,text='Informational inventory; does not claim to be a complete vulnerability scanner.',bg=BG,fg=MUTED).pack(anchor='w',padx=16); self.button(f,'RUN LOCAL AUDIT',self.run_audit).pack(anchor='w',padx=16,pady=8); self.auditout=tk.Text(f,bg=PANEL,fg=WHITE); self.auditout.pack(fill='both',expand=True,padx=16,pady=8)
 def _password(self):
    f=self.tabs['password']; tk.Label(f,text='PASSWORD SUITE',bg=BG,fg=GREEN,font=('TkFixedFont',14,'bold')).pack(anchor='w',padx=16,pady=14); tk.Label(f,text='Assessment is local and heuristic. Avoid entering a password you currently use.',bg=BG,fg=MUTED).pack(anchor='w',padx=16); self.label(f,'Test password'); self.passvar=self.entry(f,''); row=tk.Frame(f,bg=BG); row.pack(anchor='w',padx=16,pady=8); self.button(row,'ASSESS LOCALLY',self.check_password).pack(side='left',padx=(0,8)); self.button(row,'GENERATE 20-CHAR PASSWORD',self.gen_password).pack(side='left'); self.passout=tk.StringVar(value='No assessment performed.'); tk.Label(f,textvariable=self.passout,bg=BG,fg=GREEN,wraplength=850,justify='left').pack(anchor='w',padx=16,pady=12); self.generated=tk.StringVar(value=''); tk.Entry(f,textvariable=self.generated,bg=PANEL,fg=WHITE,width=70).pack(anchor='w',padx=16,pady=4)
 def _keysec(self):
    f=self.tabs['keysec']
    tk.Label(f,text='VISIBLE KEYLOGGER LAB / KEYBOARD EVENT TEST',bg=BG,fg=GREEN,font=('TkFixedFont',14,'bold')).pack(anchor='w',padx=16,pady=14)
    tk.Label(f,text='Controlled test only: events are observed only when the dedicated test field below has focus and the test is active. It records key names, not typed text, passwords, clipboard data, or input from other applications. Nothing is transmitted or saved to disk.',bg=BG,fg=WHITE,wraplength=900,justify='left').pack(anchor='w',padx=16)
    self.keylab_active=False
    self.keylab_count=0
    row=tk.Frame(f,bg=BG); row.pack(anchor='w',padx=16,pady=10)
    self.button(row,'START VISIBLE TEST',self.start_keylab).pack(side='left',padx=(0,8))
    self.button(row,'STOP TEST',self.stop_keylab).pack(side='left',padx=(0,8))
    self.button(row,'CLEAR EVENTS',self.clear_keylab).pack(side='left')
    self.keylab_state=tk.StringVar(value='STOPPED — press Start, then focus the test field.')
    tk.Label(f,textvariable=self.keylab_state,bg=BG,fg=GREEN,wraplength=900,justify='left').pack(anchor='w',padx=16,pady=4)
    tk.Label(f,text='TEST FIELD — do not type passwords or private information',bg=BG,fg=MUTED).pack(anchor='w',padx=16,pady=(10,3))
    self.keylab_entry=tk.Entry(f,bg=PANEL,fg=WHITE,insertbackground=WHITE,width=72,relief='flat')
    self.keylab_entry.pack(anchor='w',padx=16,pady=4)
    self.keylab_entry.bind('<KeyPress>',self.record_keylab_event)
    self.keylab_out=tk.Text(f,bg=PANEL,fg=WHITE,height=14,state='disabled')
    self.keylab_out.pack(fill='both',expand=True,padx=16,pady=8)
 def start_keylab(self):
    self.keylab_active=True
    self.keylab_state.set('ACTIVE — app-local visible test. Click the dedicated field and type harmless test keys.')
    self.keylab_entry.focus_set()
    self.log('Visible keyboard test started; key names only, dedicated field only.')
 def stop_keylab(self):
    self.keylab_active=False
    self.keylab_state.set('STOPPED — no keyboard events are being recorded.')
    self.log('Visible keyboard test stopped.')
 def record_keylab_event(self,event):
    if not self.keylab_active: return
    self.keylab_count+=1
    modifiers=[]
    if event.state & 0x0001: modifiers.append('Shift')
    if event.state & 0x0004: modifiers.append('Ctrl')
    if event.state & 0x0008: modifiers.append('Alt')
    key=' + '.join(modifiers+[event.keysym])
    line=f'{self.keylab_count:04d}  {datetime.now().strftime("%H:%M:%S")}  {key}'
    self.keylab_out.configure(state='normal')
    self.keylab_out.insert('end',line+'\\n')
    self.keylab_out.see('end')
    self.keylab_out.configure(state='disabled')
 def clear_keylab(self):
    self.keylab_count=0
    self.keylab_out.configure(state='normal')
    self.keylab_out.delete('1.0','end')
    self.keylab_out.configure(state='disabled')
    self.log('Visible keyboard test event list cleared.')
 def pick(self,var):
    name=filedialog.askopenfilename(title='Select wordlist');
    if name: var.set(name)
 def log(self,msg): self.events.put(('log',f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"))
 def append(self,widget,msg): self.events.put(('text',(widget,msg)))
 def worker(self,fn):
    self.jobs+=1; self.status.set('● WORKING'); threading.Thread(target=self._worker,args=(fn,),daemon=True).start()
 def _worker(self,fn):
    try: fn()
    except Exception as e: self.log(f'ERROR: {type(e).__name__}: {e}')
    finally: self.events.put(('jobdone',None))
 def _drain(self):
    try:
     while True:
      k,p=self.events.get_nowait()
      if k=='log': self.console.configure(state='normal'); self.console.insert('end',p+'\n'); self.console.see('end'); self.console.configure(state='disabled')
      elif k=='text':
       w,msg=p; w.insert('end',msg+'\n'); w.see('end')
      elif k=='port': self.porttree.insert('','end',values=p)
      elif k=='jobdone': self.jobs=max(0,self.jobs-1); self.status.set('● WORKING' if self.jobs else '● READY')
      elif k=='sniffstate': self.sniffstate.set(p)
    except queue.Empty: pass
    self.root.after(100,self._drain)
 def start_ports(self):
    if not self.auth(self.tabs['ports']): return
    host=self.porthost.get().strip()
    try:
     a,b=map(int,self.portrange.get().split('-',1));
     if not host or not 1<=a<=b<=65535 or b-a+1>1024: raise ValueError
     ip=socket.gethostbyname(host)
    except Exception as e: messagebox.showerror('Invalid target/range',f'Check host and range (1-1024 ports).\n{e}'); return
    for i in self.porttree.get_children(): self.porttree.delete(i)
    self.log(f'TCP scan started: {host} ({ip}), ports {a}-{b}.')
    def task():
     opened=[]
     with ThreadPoolExecutor(max_workers=48) as pool:
      fs={pool.submit(tcp_check,ip,p,.45):p for p in range(a,b+1)}
      for fu in as_completed(fs):
       port=fs[fu]
       try: ok=fu.result()
       except OSError as e: self.log(f'Port {port}: {e}'); continue
       if ok: opened.append(port); self.events.put(('port',(port,'OPEN',COMMON_PORTS.get(port,'Unknown')))); self.log(f'Open TCP port {port} ({COMMON_PORTS.get(port,"Unknown")})')
     self.findings.append({'type':'tcp_port_inventory','target':host,'resolved_ip':ip,'range':[a,b],'open_ports':sorted(opened),'timestamp':datetime.now(timezone.utc).isoformat(),'interpretation':'Connectivity only; not proof of vulnerability.'}); self.log(f'Scan finished: {len(opened)} open ports.')
    self.worker(task)
 def start_dirs(self):
    if not self.auth(self.tabs['dirs']): return
    try: base=valid_url(self.dirurl.get()); words=load_words(self.dirword.get().strip(),DEFAULT_PATHS)
    except Exception as e: messagebox.showerror('Invalid input',str(e)); return
    self.dirout.delete('1.0','end'); self.log(f'Directory discovery started for {base} ({len(words)} paths).')
    def task():
     hits=[]
     for word in words:
      url=urljoin(base,word.lstrip('/'))
      try: code=http_status(url)
      except Exception as e: self.log(f'{url}: request failed ({e})'); continue
      if code in (200,204,301,302,307,308,401,403): hits.append({'url':url,'status':code}); self.append(self.dirout,f'{code}  {url}'); self.log(f'HTTP {code} {url}')
     self.findings.append({'type':'web_path_discovery','base_url':base,'results':hits,'tested':len(words),'timestamp':datetime.now(timezone.utc).isoformat()}); self.log(f'Directory discovery complete: {len(hits)} matching responses from {len(words)} paths.')
    self.worker(task)
 def start_subs(self):
    if not self.auth(self.tabs['subs']): return
    domain=self.subdomain.get().strip().lower().rstrip('.')
    if not domain or '/' in domain or ' ' in domain: messagebox.showerror('Invalid domain','Enter a domain name only.'); return
    try: words=load_words(self.subword.get().strip(),DEFAULT_SUBS)
    except Exception as e: messagebox.showerror('Wordlist error',str(e)); return
    self.subout.delete('1.0','end'); self.log(f'Subdomain enumeration started for {domain} ({len(words)} labels).')
    def task():
     found=[]
     def resolve(label):
      fqdn=f'{label}.{domain}'
      try: return fqdn, sorted({x[4][0] for x in socket.getaddrinfo(fqdn,None,type=socket.SOCK_STREAM)})
      except socket.gaierror: return fqdn,[]
     with ThreadPoolExecutor(max_workers=24) as pool:
      for fqdn,ips in pool.map(resolve,words):
       if ips: found.append({'domain':fqdn,'addresses':ips}); self.append(self.subout,f'{fqdn} -> {", ".join(ips)}'); self.log(f'Resolved {fqdn}: {", ".join(ips)}')
     self.findings.append({'type':'dns_subdomain_inventory','domain':domain,'results':found,'tested':len(words),'timestamp':datetime.now(timezone.utc).isoformat()}); self.log(f'Subdomain enumeration complete: {len(found)} resolved.')
    self.worker(task)
 def start_surface(self):
    if not self.auth(self.tabs['surface']): return
    host=self.surfhost.get().strip()
    try: ip=socket.gethostbyname(host); words=load_words(self.surfword.get().strip(),DEFAULT_PATHS); web=self.surfurl.get().strip(); web=valid_url(web) if web else ''
    except Exception as e: messagebox.showerror('Invalid input',str(e)); return
    self.surfout.delete('1.0','end'); self.log(f'Threat surface inventory started: {host} ({ip}).')
    def task():
     opened=[]
     for port,svc in COMMON_PORTS.items():
      try:
       if tcp_check(ip,port,.3): opened.append({'port':port,'service':svc}); self.append(self.surfout,f'OPEN {port}/tcp  {svc}'); self.log(f'Surface: open {port}/tcp ({svc})')
      except OSError as e: self.log(f'Port {port} error: {e}')
     paths=[]
     if web:
      for word in words:
       url=urljoin(web,word.lstrip('/'))
       try: code=http_status(url)
       except Exception as e: self.log(f'Web check failed {url}: {e}'); continue
       if code in (200,204,301,302,307,308,401,403): paths.append({'url':url,'status':code}); self.append(self.surfout,f'HTTP {code}  {url}')
     if not opened and not paths: self.append(self.surfout,'Completed: no matching open ports or web paths were identified by these checks.')
     self.findings.append({'type':'threat_surface_inventory','target':host,'resolved_ip':ip,'open_ports':opened,'web_paths':paths,'timestamp':datetime.now(timezone.utc).isoformat(),'note':'Inventory only; findings require contextual validation.'}); self.log(f'Threat surface inventory complete: {len(opened)} ports, {len(paths)} web paths.')
    self.worker(task)
 def start_sniff(self):
    if self.sniff_thread and self.sniff_thread.is_alive(): messagebox.showinfo('Capture active','Packet capture is already running.'); return
    try:
     from scapy.all import sniff, get_if_list
     interfaces=get_if_list()
    except Exception as e:
     hint = ('On Windows, install Npcap from https://npcap.com/ and run this app with suitable capture permissions.' if platform.system() == 'Windows' else 'On Kali/Debian, install it with: sudo apt install python3-scapy')
     messagebox.showerror('Packet capture unavailable',f'Could not initialize Scapy packet capture.\n{type(e).__name__}: {e}\n\n{hint}'); self.log(f'Scapy unavailable: {type(e).__name__}: {e}'); return
    iface=self.sniffiface.get().strip() or None
    if iface and iface not in interfaces:
     messagebox.showerror('Unknown interface',f'Interface {iface!r} was not found. Click REFRESH INTERFACES and choose one of: {", ".join(interfaces) or "(none detected)"}'); return
    if not messagebox.askyesno('Authorized capture','Confirm you are authorized to monitor this network interface. Packet metadata may contain sensitive information. Continue?'): return
    self.sniff_stop.clear(); self.sniff_packets=0; self.sniffout.delete('1.0','end'); self.sniffstate.set(f'Starting capture on {iface or "Scapy default interface"}…'); self.log(f'Packet capture requested on {iface or "default interface"}.')
    def task():
     try:
      from scapy.all import sniff
      from scapy.layers.inet import IP, TCP, UDP, ICMP
      self.log('Capture loop active. Waiting for packets…')
      # Short timed capture slices allow STOP to work even when no packets arrive.
      while not self.sniff_stop.is_set():
       packets=sniff(iface=iface,timeout=1,prn=None,store=True)
       for pkt in packets:
        if self.sniff_stop.is_set(): break
        try:
         if IP in pkt:
          ip=pkt[IP]; proto='TCP' if TCP in pkt else 'UDP' if UDP in pkt else 'ICMP' if ICMP in pkt else str(ip.proto)
          detail=f'{ip.src} -> {ip.dst} | {proto}'
          if TCP in pkt: detail+=f' {pkt[TCP].sport}->{pkt[TCP].dport}'
          elif UDP in pkt: detail+=f' {pkt[UDP].sport}->{pkt[UDP].dport}'
          self.sniff_packets+=1; self.append(self.sniffout,detail)
          if self.sniff_packets % 10 == 0: self.log(f'Captured {self.sniff_packets} IP packets.')
        except Exception as e: self.log(f'Packet parse error: {type(e).__name__}: {e}')
      self.log(f'Packet capture ended; displayed {self.sniff_packets} IP packets.')
      self.events.put(('sniffstate',f'Capture stopped. {self.sniff_packets} IP packets displayed.'))
     except Exception as e:
      msg=f'Capture failed: {type(e).__name__}: {e}'
      self.log(msg); self.events.put(('sniffstate',msg))
    self.sniff_thread=threading.Thread(target=task,daemon=True); self.sniff_thread.start()
 def stop_sniff(self):
    self.sniff_stop.set(); self.sniffstate.set('Stopping capture…'); self.log('Packet capture stop requested.')

 def run_audit(self):
    import shutil
    root_path = Path.home().anchor or str(Path.home())
    try:
     disk_free = shutil.disk_usage(root_path).free
    except OSError:
     disk_free = None
    facts={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'hostname':socket.gethostname(),'platform':platform.platform(),'system':platform.system(),'release':platform.release(),'architecture':platform.machine(),'python':platform.python_version(),'cpu_count':os.cpu_count(),'effective_user':os.environ.get('USERNAME') or os.environ.get('USER','unknown'),'disk_root_free_bytes':disk_free,'checks':{'python_tkinter':'available','scapy':self._has_module('scapy'),'requests':self._has_module('requests')}}
    self.auditout.delete('1.0','end'); self.auditout.insert('end',json.dumps(facts,indent=2)); self.findings.append({'type':'local_system_inventory',**facts}); self.log('Local system inventory collected (informational, not a vulnerability verdict).')
 def _has_module(self,name):
    import importlib.util; return importlib.util.find_spec(name) is not None
 def check_password(self):
    val=self.passvar.get()
    if not val: self.passout.set('Enter a test password. Do not reuse a real account password.'); return
    score,note=strength(val); self.passout.set(f'Heuristic score: {score}/100. {note} This is not a guarantee of resistance to guessing.'); self.log('Password assessed locally; secret was not logged or exported.'); self.passvar.set('')
 def gen_password(self):
    pw=make_password(20); self.generated.set(pw); self.log('Secure random password generated locally. Store it safely; it is not included in reports.')
 def export(self):
    path=filedialog.asksaveasfilename(title='Export findings',defaultextension='.json',filetypes=[('JSON report','*.json')],initialfile='dvinesoul_defence_report.json')
    if not path:return
    try: Path(path).write_text(json.dumps({'application':APP_NAME,'version':'0.2.0','exported_at':datetime.now(timezone.utc).isoformat(),'findings':self.findings},indent=2),encoding='utf-8'); self.log(f'Report exported: {path}'); messagebox.showinfo('Export complete','JSON report saved.')
    except OSError as e: messagebox.showerror('Export failed',str(e))
 def clear_log(self): self.console.configure(state='normal'); self.console.delete('1.0','end'); self.console.configure(state='disabled')

def main():
 root=tk.Tk(); DefenceApp(root); root.mainloop()
if __name__=='__main__': main()
