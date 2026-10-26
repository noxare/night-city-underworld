import json
from pathlib import Path
import unittest
import tempfile
from lua_harness import LuaHarness


class NativeInjuryTest(unittest.TestCase):
    def test_owned_clone_status_application_removal_and_timed_cleanup(self):
        try: h=LuaHarness()
        except RuntimeError as e:self.skipTest(str(e))
        self.addCleanup(h.close)
        p=Path(__file__).resolve().parents[1]/'mods/night_city_underworld/injury_test.lua'
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        trace=Path(directory.name)/'injury.jsonl'
        h.run('TRACE='+json.dumps(str(trace)))
        h.run('MODULE='+json.dumps(str(p)))
        h.run('''
local chosen,deleted,applied,removed,created=nil,0,0,0,0
local effects={}
local lastMovement=nil
local commandActive=false
AIbehaviorUniqueActiveCommandList={IsActionCommandById=function()return commandActive end}
local sent=0;local pos={x=0,y=0,z=0}
local controller={SendCommand=function(_,cmd)assert(cmd.ignoreNavigation==false);sent=sent+1;lastMovement=cmd.movementType end,CancelCommand=function()end}
local policyMovement=nil
local weights={}
local actor={GetMovePolicesComponent=function()return {ChangeMovementType=function(_,kind)policyMovement=kind end}end,IsAttached=function()return true end,GetAIControllerComponent=function()return controller end,GetWorldPosition=function()return pos end}
local player={GetWorldPosition=function()return {x=0,y=0,z=0}end,GetWorldForward=function()return {x=1,y=0}end,GetWorldOrientation=function()return {}end}
local target={IsNPC=function()return true end,IsCrowd=function()return true end,GetRecordID=function()return 'crowd-record'end}
local s={IsReady=function()return true end,IsPopulated=function()return false end,
CreateEntity=function(_,spec)assert(not spec.persistState and not spec.persistSpawn);created=created+1;return 'owned'end,
IsTagged=function(_,id) return id=='owned'end,GetEntity=function()return actor end,DeleteTagged=function()deleted=deleted+1 end}
Game={GetDynamicEntitySystem=function()return s end,GetPlayer=function()return player end,
GetTargetingSystem=function()return {GetLookAtObject=function()return target end}end,
GetStatusEffectSystem=function()return {HasStatusEffect=function(_,id,effect)return effects[effect]==true end,RemoveStatusEffect=function(_,id,effect)assert(id=='owned');effects[effect]=false;removed=removed+1 end}end}
CName={new=function(x)return x end};TweakDBID=CName
WorldPosition={new=function()return {SetVector4=function()end}end};AIPositionSpec={new=function()return {SetWorldPosition=function()end}end};AIMoveToCommand={new=function()return {}end};moveMovementType={Walk=1,Run=2}
Vector4={new=function()return {}end};DynamicEntitySpec={new=function()return {}end}
TweakDB={GetRecord=function()return {}end}
StatusEffectHelper={ApplyStatusEffect=function(a,effect)assert(a==actor);effects[effect]=true;applied=applied+1 end}
AnimationControllerComponent={SetAnimWrapperWeightOnOwnerAndItems=function(a,name,weight)assert(a==actor);weights[name]=weight end}
registerForEvent=nil;print=function()end
ImGui={Separator=function()end,Text=function()end,Button=function(x)return x==chosen end}
local t=dofile(MODULE);t.tracePath=TRACE
local function click(x)chosen=x;t.draw(true);chosen=nil end
click('Eigenen Test-NPC erzeugen');assert(created==1)
t.update(2);assert(sent==1);pos.x=2;t.update(.1);assert(t.distance==2)
click('Test-NPC gehen lassen (6 m)');assert(sent==2)
click('Eigenen Test-NPC erzeugen');assert(created==1)
click('Flucht vom Spieler testen');assert(lastMovement==moveMovementType.Run and policyMovement==moveMovementType.Run)
click('Linkes Bein: nativen Effekt anwenden');assert(applied==1 and lastMovement==moveMovementType.Run)
click('Flucht vom Spieler testen');assert(lastMovement==moveMovementType.Run and applied==1)
assert(t.legEffects.Left and t.intent=='flee')
assert(weights.woundedLocomotion_l_leg==1 and weights.woundedLocomotion_r_leg==0)
-- AI command activation can replace the initial graph state. Rebind once.
weights.woundedLocomotion_l_leg=0
commandActive=true;t.update(1)
assert(weights.woundedLocomotion_l_leg==1 and t.wrapperBoundToCommand)
weights.woundedLocomotion_l_leg=.25;t.update(1)
assert(weights.woundedLocomotion_l_leg==.25) -- no per-frame forcing
click('Rechtes Bein: nativen Effekt anwenden')
assert(weights.woundedLocomotion_l_leg==0 and weights.woundedLocomotion_r_leg==1)
assert(not effects['BaseStatusEffect.CrippledLegLeft'] and effects['BaseStatusEffect.CrippledLegRight'])
assert(not t.legEffects.Left and t.legEffects.Right)
click('Beineffekte entfernen');assert(removed==3 and lastMovement==moveMovementType.Run)
assert(not t.legEffects.Left and not t.legEffects.Right)
assert(weights.woundedLocomotion_l_leg==0 and weights.woundedLocomotion_r_leg==0)
pos.x=2;t.update(4)
assert(t.motionState:find('Keine Bewegung'))
assert(t.commandState=='aktiv')
-- Losing the spawned actor releases this adapter immediately, without retry spam.
s.GetEntity=function()return nil end
t.update(.5);assert(deleted==1 and t.id==nil)
''')
        rows=[json.loads(line) for line in trace.read_text().splitlines()]
        kinds={row['event'] for row in rows}
        self.assertTrue({'spawn_requested','spawn_created','actor_attached','command_requested',
                         'movement_sample','leg_replaced','actor_unloaded','cleanup_complete'} <= kinds)
        self.assertEqual(len({row['test_id'] for row in rows}),1)
        samples=[row for row in rows if row['event']=='movement_sample']
        self.assertTrue(any(row['active']=='true' for row in samples))
        self.assertTrue(all(row['role']=='unavailable' for row in samples))
        self.assertTrue(all(row['destination_distance'] >= 0 for row in samples))

    def test_trace_rotation_budget_and_failure_do_not_block_cleanup(self):
        try: h=LuaHarness()
        except RuntimeError as e:self.skipTest(str(e))
        self.addCleanup(h.close)
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        trace=Path(directory.name)/'injury.jsonl'
        trace.write_text('x'*262140)
        module=Path(__file__).resolve().parents[1]/'mods/night_city_underworld/injury_test.lua'
        h.run('MODULE='+json.dumps(str(module))+'; TRACE='+json.dumps(str(trace)))
        h.run('''
CName={new=function(x)return x end}
local deleted=0
Game={GetDynamicEntitySystem=function()return {DeleteTagged=function()deleted=deleted+1 end}end}
local t=dofile(MODULE);t.tracePath=TRACE
-- A full log rotates into one bounded previous file.
t.cleanup();assert(deleted==1 and not t.traceError)
-- Record budget prevents unbounded writes within a test.
t.traceCount=1024;t.cleanup();assert(deleted==2 and t.traceCount==1024)
-- Encoder/storage failure is visible, but owned-actor cleanup still executes.
t.traceCount=0;json.encode=function()error('disk unavailable')end
t.cleanup();assert(deleted==3 and t.traceError:find('disk unavailable'))
''')
        self.assertEqual(trace.with_name('injury.jsonl.previous').stat().st_size,262140)
        rows=[json.loads(line) for line in trace.read_text().splitlines()]
        self.assertEqual([row['event'] for row in rows],['cleanup_requested','cleanup_complete'])
        self.assertLess(trace.stat().st_size,262144)

    def test_readiness_timeout_and_invalid_delta_are_bounded(self):
        try: h=LuaHarness()
        except RuntimeError as e:self.skipTest(str(e))
        self.addCleanup(h.close)
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        trace=Path(directory.name)/'injury.jsonl'
        module=Path(__file__).resolve().parents[1]/'mods/night_city_underworld/injury_test.lua'
        h.run('MODULE='+json.dumps(str(module))+'; TRACE='+json.dumps(str(trace)))
        h.run('''
CName={new=function(x)return x end}
local reads,deleted=0,0
local s={IsTagged=function()return true end,GetEntity=function()reads=reads+1;return nil end,
DeleteTagged=function()deleted=deleted+1 end}
Game={GetDynamicEntitySystem=function()return s end,GetPlayer=function()return {}end}
print=function()end
local t=dofile(MODULE);t.tracePath=TRACE;t.id='owned'
t.update(0/0);t.update(-1);t.update(math.huge);assert(t.age==0)
t.update(2);local first=reads
t.update(.1);assert(reads==first) -- readiness retry limited to 2 Hz
t.update(8);assert(t.id==nil and deleted==1)
''')
        rows=[json.loads(line) for line in trace.read_text().splitlines()]
        self.assertIn('readiness_timeout', [row['event'] for row in rows])
