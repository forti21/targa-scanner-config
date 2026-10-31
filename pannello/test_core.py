import copy,json,unittest,base64,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import build,GitHub,get

class Tests(unittest.TestCase):
    def setUp(self):self.config=json.loads((Path(__file__).resolve().parents[1]/'config.json').read_text())
    def test_no_change(self):
        result,changes=build(self.config,{},'');self.assertEqual(result,self.config);self.assertFalse(changes)
        result,changes=build(self.config,{'countries.SK':True},'');self.assertEqual(result,self.config);self.assertFalse(changes)
    def test_preserve_unknown_and_revision(self):
        self.config['future_section']={'keep':[1,2,3]};original=copy.deepcopy(self.config)
        result,changes=build(self.config,{'features.rca':False,'app_control.maintenance_mode':True},'')
        self.assertEqual(self.config,original);self.assertEqual(result['future_section'],original['future_section'])
        self.assertEqual(result['config_revision'],original['config_revision']+1);self.assertEqual(len(changes),2)
    def test_validation(self):
        for values,blocked in [({'search.cooldown_seconds':'-1'},''),({'search.cooldown_seconds':'301'},''),({'version_control.minimum_version':'a.b'},''),({'security.require_signed_config':False},''),({},'Enrico'),({'features.rca':'false'},'')]:
            with self.assertRaises(ValueError):build(self.config,values,blocked)
    def test_installation_changes_reviewed(self):
        token='ABCDEF12-1234-1234-1234-ABCDEF123456'
        result,changes=build(self.config,{},token.lower()+'\n'+token)
        self.assertEqual(get(result,'access_control.blocked_installation_tokens'),[token])
        self.assertTrue(any(token in line for line in changes))
    def test_conflict_does_not_write(self):
        class Fake(GitHub):
            def __init__(self,data):super().__init__('test-token');self.data=data;self.written=False
            def load(self):return self.data,'new-sha'
            def request(self,*args,**kwargs):self.written=True;raise AssertionError('Should not write')
        client=Fake(self.config);new=copy.deepcopy(self.config);new['config_revision']+=1
        with self.assertRaises(RuntimeError):client.publish(new,'old-sha')
        self.assertFalse(client.written)
    def test_publish_uses_expected_sha_and_exact_bytes(self):
        class Fake(GitHub):
            def load(inner):return self.config,'old-sha'
            def request(inner,path,body=None):
                self.assertEqual(path,'config.json');self.assertEqual(body['sha'],'old-sha');self.assertEqual(body['branch'],'main')
                inner.payload=base64.b64decode(body['content']);return {'content':{'sha':'saved'}}
        client=Fake('test-token');new,_=build(self.config,{'features.rca':False},'')
        sha,raw=client.publish(new,'old-sha');self.assertEqual(sha,'saved');self.assertEqual(raw,client.payload);self.assertEqual(json.loads(raw),new)
    def test_no_token_no_write(self):
        with self.assertRaises(ValueError):GitHub().publish(self.config,'sha')

if __name__=='__main__':unittest.main()
