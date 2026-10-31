"""Produce the envelope accepted by Targa Scanner; secret comes only from GitHub Secrets."""
import base64,json,os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
secret=os.environ.get('REMOTE_CONFIG_SIGNING_KEY','').strip()
if not secret:raise SystemExit('Missing GitHub secret REMOTE_CONFIG_SIGNING_KEY. Complete setup first.')
try:key=Ed25519PrivateKey.from_private_bytes(base64.b64decode(secret,validate=True))
except Exception:raise SystemExit('Invalid signing key. Expected base64 Ed25519 private key (32 bytes).') from None
payload=Path('config.json').read_bytes();config=json.loads(payload)
if config.get('schema_version')!=1 or not isinstance(config.get('config_revision'),int):raise SystemExit('Invalid config version/revision.')
security=config.get('security',{})
if security.get('require_signed_config') is not True or security.get('reject_downgrade') is not True or security.get('signature_algorithm')!='Ed25519' or security.get('signature_key_id')!='primary-v1':raise SystemExit('Invalid security settings.')
public=base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode()
old_public=Path('public-key.txt')
if old_public.exists() and old_public.read_text().strip()!=public:raise SystemExit('Signing key changed: requires a new app build. Existing feed preserved.')
existing=Path('config-signed.json')
if existing.exists():
    old=json.loads(existing.read_text());old_payload=base64.b64decode(old['payload'],validate=True)
    key.public_key().verify(base64.b64decode(old['signature'],validate=True),old_payload)
    old_revision=json.loads(old_payload)['config_revision']
    if config['config_revision']<old_revision or (payload!=old_payload and config['config_revision']==old_revision):raise SystemExit('Increment config_revision before changing the config.')
signature=key.sign(payload);key.public_key().verify(signature,payload)
envelope={'key_id':'primary-v1','payload':base64.b64encode(payload).decode(),'signature':base64.b64encode(signature).decode()}
Path('config-signed.json').write_text(json.dumps(envelope,indent=2)+'\n')
old_public.write_text(public+'\n')
print('Configuration signature verified. Revision:',config['config_revision'])
