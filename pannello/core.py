"""Fixed-scope configuration editor. No credentials or private signing keys on disk."""
import base64,copy,json,uuid,urllib.request,urllib.error
REPO='forti21/targa-scanner-config'
BASE='https://api.github.com/repos/'+REPO+'/contents/'
FLAGS={
 'app_control.enabled':'App attiva',
 'app_control.searches_enabled':'Ricerche abilitate',
 'app_control.maintenance_mode':'Manutenzione',
 'app_control.emergency_stop':'Stop generale',
 'search.new_searches_enabled':'Nuove ricerche abilitate',
 'version_control.force_update':'Aggiornamento obbligatorio',
 'notices.startup_banner.enabled':'Mostra messaggio',
 'notices.blocking_notice.enabled':'Avviso bloccante',
}
FEATURES={'rca':'Assicurazione','revision':'Revisione','vehicle_data':'Dati veicolo','vin':'Telaio VIN','emission_class':'Classe ambientale','new_driver_eligibility':'Neopatentati','theft_check':'Furto','car':'Auto','motorcycle':'Moto','moped':'Ciclomotori','license_plate_trial':'Targhe prova'}
COUNTRIES={'IT':'Italia','GB':'Regno Unito','RO':'Romania','NL':'Paesi Bassi','PL':'Polonia','BG':'Bulgaria','CZ':'Repubblica Ceca','DK':'Danimarca','PT':'Portogallo','UA':'Ucraina','MD':'Moldavia','SE':'Svezia','LV':'Lettonia','LT':'Lituania','SK':'Slovacchia','RS':'Serbia'}
TEXTS={'app_control.maintenance_message':'Messaggio manutenzione / stop','notices.startup_banner.title':'Titolo messaggio','notices.startup_banner.message':'Testo messaggio','notices.blocking_notice.message':'Testo avviso bloccante','version_control.minimum_version':'Versione minima','version_control.minimum_build':'Build minima','version_control.update_message':'Messaggio aggiornamento','access_control.block_message':'Messaggio installazione bloccata','search.cooldown_seconds':'Attesa fra ricerche Italia (secondi)'}
def get(data,path,default=None):
    for part in path.split('.'):
        if not isinstance(data,dict) or part not in data:return default
        data=data[part]
    return data
def put(data,path,value):
    parts=path.split('.');node=data
    for part in parts[:-1]:node=node.setdefault(part,{})
    node[parts[-1]]=value
def validate(data):
    if type(data.get('schema_version')) is not int or data['schema_version']!=1:raise ValueError('Schema non supportato.')
    if type(data.get('config_revision')) is not int or data['config_revision']<0:raise ValueError('Revisione non valida.')
    expected={'require_signed_config':True,'reject_downgrade':True,'signature_algorithm':'Ed25519','signature_key_id':'primary-v1'}
    if any(get(data,'security.'+k)!=v for k,v in expected.items()):raise ValueError('Le impostazioni della firma non sono quelle previste.')
    for path in list(FLAGS)+['features.'+k for k in FEATURES]+['countries.'+k for k in COUNTRIES]:
        value=get(data,path)
        if value is not None and type(value) is not bool:raise ValueError('Valore non valido: '+path)
def build(original,values,blocked):
    validate(original);result=copy.deepcopy(original);changes=[]
    labels={**FLAGS,**{'features.'+k:v for k,v in FEATURES.items()},**{'countries.'+k:v for k,v in COUNTRIES.items()},**TEXTS}
    for path,value in values.items():
        if path not in labels:raise ValueError('Comando non supportato: '+path)
        if path in FLAGS or path.startswith(('features.','countries.')):
            if type(value) is not bool:raise ValueError('Interruttore non valido.')
        elif path in ['version_control.minimum_build','search.cooldown_seconds']:
            try:value=int(value)
            except (ValueError,TypeError):raise ValueError(labels[path]+': inserisci un numero intero.') from None
            maximum=300 if path.startswith('search.') else 2147483647
            if not 0<=value<=maximum:raise ValueError(labels[path]+': valore fuori intervallo.')
        else:
            value=str(value).strip()
            if len(value)>2000:raise ValueError(labels[path]+': testo troppo lungo.')
            if path=='version_control.minimum_version':
                parts=value.split('.')
                if not 1<=len(parts)<=4 or any(not p.isascii() or not p.isdigit() or int(p)>2147483647 for p in parts):raise ValueError('Versione minima non valida. Esempio: 3.92')
        old=get(original,path)
        # Absent flags have an effective default; do not create changes on a plain reload/save.
        default=False if path in FLAGS and path not in ['app_control.enabled','app_control.searches_enabled','search.new_searches_enabled'] else True
        if old==value or (old is None and type(value) is bool and value==default):continue
        put(result,path,value)
        rendered=lambda v: 'Sì' if v is True else 'No' if v is False else str(v if v is not None else '(predefinito)')
        changes.append(labels[path]+': '+rendered(old)+' → '+rendered(value))
    tokens=[]
    for line in blocked.splitlines():
        line=line.strip()
        if not line:continue
        try:token=str(uuid.UUID(line)).upper()
        except ValueError:raise ValueError('Codice installazione non valido: usa il codice copiato dall’app.') from None
        if token not in tokens:tokens.append(token)
    if len(tokens)>500:raise ValueError('Troppi codici installazione.')
    old=get(original,'access_control.blocked_installation_tokens',[])
    if tokens!=old:
        put(result,'access_control.blocked_installation_tokens',tokens)
        changes.append('Installazioni bloccate: '+str(len(old))+' → '+str(len(tokens)))
        changes.extend('Blocca installazione: '+token for token in tokens if token not in old)
        changes.extend('Sblocca installazione: '+token for token in old if token not in tokens)
    if not changes:return result,changes
    result['config_revision']=original['config_revision']+1
    validate(result)
    return result,changes
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None
class GitHub:
    def __init__(self,token=''):self.token=token.strip();self.opener=urllib.request.build_opener(NoRedirect())
    def request(self,path,body=None):
        if path not in ['config.json?ref=main','config-signed.json?ref=main','config.json']:raise ValueError('Percorso non ammesso.')
        headers={'Accept':'application/vnd.github+json','User-Agent':'TargaScanner-Admin','X-GitHub-Api-Version':'2022-11-28','Cache-Control':'no-cache'}
        if self.token:headers['Authorization']='Bearer '+self.token
        if body is not None:headers['Content-Type']='application/json'
        request=urllib.request.Request(BASE+path,headers=headers,data=json.dumps(body).encode() if body is not None else None,method='PUT' if body is not None else 'GET')
        try:
            with self.opener.open(request,timeout=15) as response:return json.load(response)
        except urllib.error.HTTPError as e:
            messages={401:'Token GitHub non valido.',403:'Accesso negato: controlla scadenza e permesso Contents del token.',404:'File non trovato o repository non accessibile.',409:'Il file è cambiato. Rileggilo e riapplica le modifiche.',422:'GitHub ha rifiutato la modifica. Rileggi il file prima di riprovare.'}
            raise RuntimeError(messages.get(e.code,'GitHub ha risposto HTTP '+str(e.code))) from None
        except (urllib.error.URLError,TimeoutError,OSError):raise RuntimeError('Connessione GitHub non disponibile. Nessuna conferma di pubblicazione: rileggi lo stato prima di riprovare.') from None
    def load(self):
        data=self.request('config.json?ref=main')
        config=json.loads(base64.b64decode(data['content']))
        validate(config);return config,data['sha']
    def publish(self,config,sha):
        if not self.token:raise ValueError('Inserisci il token GitHub per pubblicare.')
        current,current_sha=self.load()
        if sha!=current_sha:raise RuntimeError('Configurazione modificata da un altro accesso. Rileggi e ripeti le modifiche.')
        if config['config_revision']!=current['config_revision']+1:raise ValueError('Revisione non coerente: rileggi la configurazione.')
        validate(config)
        raw=(json.dumps(config,indent=2,ensure_ascii=False)+'\n').encode()
        result=self.request('config.json',{'message':'Update app controls, revision '+str(config['config_revision']),'branch':'main','sha':sha,'content':base64.b64encode(raw).decode()})
        return result['content']['sha'],raw
    def signed_matches(self,raw):
        data=self.request('config-signed.json?ref=main')
        envelope=json.loads(base64.b64decode(data['content']))
        return base64.b64decode(envelope['payload'])==raw
