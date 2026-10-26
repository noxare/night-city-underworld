import json
from pathlib import Path
import unittest
from lua_harness import LuaHarness


class AutomaticEncountersTest(unittest.TestCase):
    def test_actual_hit_identity_zone_ack_then_original_actor_reaction(self):
        try:
            h = LuaHarness()
        except RuntimeError as error:
            self.skipTest(str(error))
        self.addCleanup(h.close)
        module = Path(__file__).resolve().parents[1] / "mods/night_city_underworld/encounters.lua"
        h.run("MODULE=" + json.dumps(str(module)))
        h.run(r'''
local hooks,files={},{}
local sent,applied,removed,deleted,spawned=0,0,0,0,0
local original={hash='original-1'}
local pos={x=4,y=0,z=0}
local effects={}
local actor
local controller={SendCommand=function(_,cmd)
    assert(cmd.ignoreNavigation==false and cmd.movementType==2);sent=sent+1;cmd.id='command'
end,CancelCommand=function()end,activeCommands={}}
actor={IsNPC=function()return true end,IsCrowd=function()return true end,
    IsDead=function()return false end,IsAttached=function()return true end,
    GetEntityID=function()return original end,GetRecordID=function()return 'crowd'return end,
    GetWorldPosition=function()return pos end,GetAIControllerComponent=function()return controller end,
    GetTemplatePath=function()return 'person.ent'end,GetCurrentAppearanceName=function()return 'specific-face'end}
local player={IsPlayer=function()return true end,GetWorldPosition=function()return {x=0,y=0,z=0}end,
    GetWorldForward=function()return {x=1,y=0}end}
Game={GetPlayer=function()return player end,FindEntityByID=function(id)assert(id==original);return actor end,
    GetDynamicEntitySystem=function()return {IsTagged=function()return false end,
        CreateEntity=function()spawned=spawned+1 end,DeleteEntity=function()deleted=deleted+1 end}end,
    GetStatusEffectSystem=function()return {
        HasStatusEffect=function(_,_,id)return effects[id]==true end,
        RemoveStatusEffect=function(_,_,id)effects[id]=nil;removed=removed+1 end}end}
CName={new=function(x)return x end};TweakDBID=CName
TweakDB={GetRecord=function()return {}end}
Vector4={new=function(x,y,z,w)return {x=x,y=y,z=z,w=w}end}
WorldPosition={new=function()return {SetVector4=function()end}end}
AIPositionSpec={new=function()return {SetWorldPosition=function()end}end}
AIMoveToCommand={new=function()return {}end};moveMovementType={Run=2}
StatusEffectHelper={ApplyStatusEffect=function(a,id)assert(a==actor);effects[id]=true;applied=applied+1 end}
AnimationControllerComponent={SetAnimWrapperWeightOnOwnerAndItems=function(a)assert(a==actor)end}
AIbehaviorUniqueActiveCommandList={IsActionCommandById=function()return true end}
ObserveAfter=function(class,method,fn)assert(class=='ScriptedPuppet' and method=='OnHit');hooks.hit=fn end
AttackData={IsAreaOfEffect=function(x)return x=='area'end}
DamageSystemHelper={GetHitShapeUserDataBase=function(x)return x end}
HitShapeUserDataBase={}
for _,name in ipairs({'Head','Torso','LeftArm','RightArm','LeftLeg','RightLeg'})do
    HitShapeUserDataBase['IsHitReactionZone'..name]=function(x)return x==name end
end
io.open=function(path,mode)
    if mode=='r' and not files[path] then return nil end
    if mode=='w' then files[path]='' end
    return {read=function()return files[path]end,seek=function()return #(files[path] or '')end,
        write=function(_,data)files[path]=(files[path] or '')..data;return true end,
        close=function()return true end}
end
os.remove=function(path)files[path]=nil end
os.rename=function(a,b)files[b]=files[a];files[a]=nil;return true end
print=function()end
local e=dofile(MODULE);e.initialize()
local event={attackData={GetInstigator=function()return player end,GetAttackType=function()return 'bullet'end},
    hitRepresentationResult={hitShapes={'LeftLeg'}}}
hooks.hit(actor,event)
assert(e.status().hits==0 and e.status().tracked==0)
e.update(.1)
assert(sent==0 and applied==0) -- no context or durable promotion acknowledgement
files['nemesis-context.json']=json.encode({schema_version=1,slot='save-a',timeline='branch-a',session_id='world-session'})..'\n'
-- Lua long strings above intentionally use real JSON newline below.
files['nemesis-context.json']=files['nemesis-context.json']:gsub('\\n$','\n')
hooks.hit(actor,event)
e.update(.1)
local raw=files['nemesis-request.json']
assert(raw,'automatic mailbox request missing')
local request=json.decode(raw)
assert(request.event.entity_id=='original-1' and request.event.zone=='left_leg')
assert(request.event.appearance.appearance=='specific-face')
files['nemesis-response.json']=json.encode({schema_version=1,slot='wrong-save',timeline='branch-a',
    event_id=request.event.event_id,result={person_id='person-1',plan={movement='Run',gait='limp',injured_side='Left'}}})..'\n'
files['nemesis-response.json']=files['nemesis-response.json']:gsub('\\n$','\n')
e.update(.1);assert(sent==0) -- stale/wrong-save acknowledgement cannot mutate NPC
files['nemesis-response.json']=json.encode({schema_version=1,slot='save-a',timeline='branch-a',
    event_id=request.event.event_id,result={person_id='person-1',plan={movement='Run',gait='limp',injured_side='Left'}}})..'\n'
files['nemesis-response.json']=files['nemesis-response.json']:gsub('\\n$','\n')
e.update(.1)
assert(sent==1 and applied==1 and spawned==0 and deleted==0)
assert(files['nemesis-trace.jsonl']:find('person_promoted',1,true))
-- An offscreen hit is read from its event, never the current crosshair target.
local stranger={IsPlayer=function()return false end}
event.attackData.GetInstigator=function()return stranger end
hooks.hit(actor,event);assert(e.status().hits==1)
e.cleanup();assert(removed==1 and e.status().tracked==0 and deleted==0)
'''.replace("return 'crowd'return end", "return 'crowd'end"))
