"""Run locally once. Keep the generated key private; paste it only into GitHub Secrets."""
import base64,os,subprocess,sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption
path=Path.home()/'TargaScanner-private-signing-key.txt'
if path.exists():
    secret=path.read_text().strip()
    key=Ed25519PrivateKey.from_private_bytes(base64.b64decode(secret,validate=True))
else:
    key=Ed25519PrivateKey.generate()
    secret=base64.b64encode(key.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption())).decode()
    fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:f.write(secret+'\n')
print('Chiave privata conservata solo sul tuo PC:',path)
if sys.platform=='win32':
    subprocess.run(['powershell','-NoProfile','-Command','$input | Set-Clipboard'],input=secret,text=True,check=True)
    print('Chiave copiata negli appunti. Incollala SOLO nel secret GitHub REMOTE_CONFIG_SIGNING_KEY.')
else:
    print('Copia il contenuto del file nel secret GitHub REMOTE_CONFIG_SIGNING_KEY.')
print('Chiave PUBBLICA:',base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode())
