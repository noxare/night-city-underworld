"""Real Lua capture -> real file IPC -> SQLite. Engine calls are mocked."""
import json
from pathlib import Path
import tempfile
import unittest
from lua_harness import LuaHarness
from underworld.mailbox import atomic_json
from underworld.nemesis_mailbox import NemesisMailbox
from underworld.nemesis_director import NemesisDirector


class LuaNemesisPipelineTest(unittest.TestCase):
    def test_original_hit_actor_survives_actual_lua_file_worker_roundtrip(self):
        try:
            lua = LuaHarness()
        except RuntimeError as error:
            self.skipTest(str(error))
        self.addCleanup(lua.close)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            box = NemesisMailbox(root, root / 'people.db', 'campaign', 'timeline', 'load-1')
            try:
                atomic_json(root / 'nemesis-context.json', {'schema_version': 1, 'slot': 'campaign',
                            'timeline': 'timeline', 'session_id': 'load-1'})
                module = Path(__file__).resolve().parents[1] / 'mods/night_city_underworld/encounters.lua'
                lua.run('ROOT=' + json.dumps(str(root) + '/') + '; MODULE=' + json.dumps(str(module)))
                lua.run('''
local realOpen,realRename,realRemove=io.open,os.rename,os.remove
io.open=function(path,mode)return realOpen(ROOT..path,mode)end
os.rename=function(a,b)return realRename(ROOT..a,ROOT..b)end
os.remove=function(path)return realRemove(ROOT..path)end
local player={IsPlayer=function()return true end}
local id={hash='actual-hit-actor'}
local actor={IsNPC=function()return true end,IsCrowd=function()return true end,
 IsDead=function()return false end,IsAttached=function()return true end,
 GetEntityID=function()return id end,GetRecordID=function()return 'crowd-record'end,
 GetTemplatePath=function()return 'person.ent'end,GetCurrentAppearanceName=function()return 'face-outfit'end,
 GetWorldPosition=function()return {x=4,y=2,z=0}end}
Game={GetPlayer=function()return player end,FindEntityByID=function()return actor end,
 GetDynamicEntitySystem=function()return {IsTagged=function()return false end}end,
 GetTargetingSystem=function()error('crosshair target must never replace hit actor')end}
CName={new=function(x)return x end}
ObserveAfter=function(_,_,callback)hitCallback=callback end
AttackData={IsAreaOfEffect=function()return false end}
DamageSystemHelper={GetHitShapeUserDataBase=function(x)return x end}
HitShapeUserDataBase={}
for _,name in ipairs({'Head','Torso','LeftArm','RightArm','LeftLeg','RightLeg'})do
 HitShapeUserDataBase['IsHitReactionZone'..name]=function(shape)return shape==name end
end
encounters=dofile(MODULE);encounters.initialize()
hitCallback(actor,{attackData={GetInstigator=function()return player end,GetAttackType=function()return 'bullet'end},
 hitRepresentationResult={hitShapes={'LeftLeg'}}})
assert(encounters.status().hits==1)
encounters.update(.1)
''')
                request = json.loads((root / 'nemesis-request.json').read_text())
                self.assertEqual(request['event']['entity_id'], 'actual-hit-actor')
                self.assertEqual(request['event']['zone'], 'left_leg')
                self.assertTrue(box.poll())
                result = json.loads((root / 'nemesis-response.json').read_text())['result']
                person = result['person_id']
                lua.run("encounters.update(.1); assert(#encounters.queue==0); assert(encounters.actors['actual-hit-actor'].person==" + json.dumps(person) + ")")
                # No native mutation APIs are supplied: default capture must not need any.
                self.assertEqual(box.store.get(person)['memories'][0]['kind'], 'V_injured_me')
                lua.run("Game.FindEntityByID=function()return nil end; encounters.update(.1); encounters.update(.1)")
                self.assertTrue(box.poll())
                state = box.store.get(person)
                self.assertEqual(state['mode'], 'simulated')
                self.assertEqual(state['position'], {'x': 4, 'y': 2, 'z': 0})
                self.assertEqual(state['appearance']['appearance'], 'face-outfit')
                self.assertEqual(len(state['memories']), 1)
                director = NemesisDirector(box.store, max_people=1)
                routes = {person: {'x': 100, 'y': 2, 'z': 0}}
                director.tick(10, routes)
                director.tick(20, routes)
                self.assertAlmostEqual(box.store.get(person)['position']['x'], 18)
                atomic_json(root / 'nemesis-request.json', {'schema_version': 1, 'slot': 'campaign',
                    'timeline': 'timeline', 'kind': 'treated', 'event': {'session_id': 'load-1',
                    'person_id': person, 'event_id': 'treatment-1', 'zone': 'left_leg', 'amount': 1}})
                self.assertTrue(box.poll())
                director.tick(30, routes)
                recovered = box.store.get(person)
                self.assertAlmostEqual(recovered['position']['x'], 53)
                self.assertEqual(recovered['memories'], state['memories'])
                self.assertEqual(recovered['appearance'], state['appearance'])
            finally:
                box.close()
