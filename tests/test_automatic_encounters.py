import json
from pathlib import Path
import unittest
from lua_harness import LuaHarness


class AutomaticEncountersTest(unittest.TestCase):
    def test_capture_only_by_default(self):
        self.run_scenario('default')

    def test_unverified_injured_gait_cannot_mutate(self):
        self.run_scenario('unverified_gait')

    def test_record_allowlist_cannot_mutate_other_actor(self):
        self.run_scenario('wrong_record')

    def test_explicit_verified_callback_owns_reaction_and_cleanup(self):
        self.run_scenario('verified')

    def test_ambiguous_shapes_remain_unknown(self):
        self.run_scenario('ambiguous')

    def test_context_change_blocks_acknowledged_reaction(self):
        self.run_scenario('context_changed')

    def run_scenario(self, mode):
        try:
            h = LuaHarness()
        except RuntimeError as error:
            self.skipTest(str(error))
        self.addCleanup(h.close)
        module = Path(__file__).resolve().parents[1] / "mods/night_city_underworld/encounters.lua"
        h.run("MODULE=" + json.dumps(str(module)) + "; MODE=" + json.dumps(mode))
        h.run(r'''
local hooks,files={},{}
local failWrites=false
local failReplace=false
local failRequest=false
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
    if failRequest and path=='nemesis-request.json' then error('request storage unavailable')end
    if failWrites and path=='nemesis-outbox.json.tmp' then return nil end
    if mode=='r' and not files[path] then return nil end
    if mode=='w' then files[path]='' end
    return {read=function()return files[path]end,seek=function()return #(files[path] or '')end,
        write=function(_,data)files[path]=(files[path] or '')..data;return true end,
        close=function()return true end}
end
os.remove=function(path)files[path]=nil end
os.rename=function(a,b)
    if failReplace and a=='nemesis-outbox.json.tmp' then return nil,'replace failed' end
    if not files[a] then return nil,'missing' end
    files[b]=files[a];files[a]=nil;return true end
print=function()end
local e=dofile(MODULE);e.initialize()
assert(e.status().mode=='capture_only')
assert(not pcall(e.configureReaction,{original_actor_verified=true}))
if MODE~='default' then
    e.configureReaction({id='mock-profile',evidence='test-fixture-only',original_actor_verified=true,
        injured_gait_verified=MODE~='unverified_gait',records={crowd=MODE~='wrong_record'},
        apply=function(a,plan,row)assert(a==actor and plan.injured_side=='Left');sent=sent+1 end,
        release=function(a,row)assert(a==actor);removed=removed+1 end})
end
local event={attackData={GetInstigator=function()return player end,GetAttackType=function()return 'bullet'end},
    hitRepresentationResult={hitShapes=MODE=='ambiguous' and {'LeftLeg','Torso'} or {'LeftLeg'}}}
local expectedZone=MODE=='ambiguous' and 'unknown' or 'left_leg'
local replyPlan=MODE=='ambiguous' and {gait='unknown'} or {movement='Run',gait='limp',injured_side='Left'}
hooks.hit(actor,event)
assert(e.status().hits==0 and e.status().tracked==0)
e.update(.1)
assert(sent==0 and applied==0) -- no context or durable promotion acknowledgement
files['nemesis-context.json']=json.encode({schema_version=1,slot='save-a',timeline='branch-a',session_id='world-session'})..'\n'
-- Lua long strings above intentionally use real JSON newline below.
files['nemesis-context.json']=files['nemesis-context.json']:gsub('\\n$','\n')
-- A failed durable outbox write cannot become a mailbox request or reaction.
failWrites=true;hooks.hit(actor,event);e.update(.1)
assert(e.status().hits==0 and not files['nemesis-request.json'])
failWrites=false
hooks.hit(actor,event)
failRequest=true;e.update(.1);assert(not e.pending and #e.queue==1)
failRequest=false;e.update(.1)
local raw=files['nemesis-request.json']
assert(raw,'automatic mailbox request missing')
local request=json.decode(raw)
assert(request.event.entity_id=='original-1' and request.event.zone==expectedZone)
assert(request.event.appearance.appearance=='specific-face')
assert(request.event.zone_source==(MODE=='ambiguous' and 'unknown' or 'engine_hit_shapes'))
if MODE=='ambiguous'then assert(not replyPlan.injured_side)end
files['nemesis-response.json']=json.encode({schema_version=1,slot='wrong-save',timeline='branch-a',
    event_id=request.event.event_id,result={person_id='person-1',plan=replyPlan}})..'\n'
files['nemesis-response.json']=files['nemesis-response.json']:gsub('\\n$','\n')
e.update(.1);assert(sent==0) -- stale/wrong-save acknowledgement cannot mutate NPC
files['nemesis-response.json']=json.encode({schema_version=1,slot='save-a',timeline='branch-a',
    event_id=request.event.event_id,result={person_id='person-1',plan=replyPlan}})..'\n'
files['nemesis-response.json']=files['nemesis-response.json']:gsub('\\n$','\n')
-- Acknowledgement removal must remain retryable if atomic replacement fails.
local durable=files['nemesis-outbox.json']
if MODE=='context_changed'then
    files['nemesis-context.json']=json.encode({schema_version=1,slot='save-b',timeline='branch-a',session_id='new-session'})..'\n'
    hooks.hit(actor,event);assert(e.status().hits==1) -- existing row cannot change identity/session
end
failReplace=true;e.update(.1)
assert(sent==0 and files['nemesis-outbox.json']==durable)
failReplace=false;e.update(.1)
assert(sent==(MODE=='verified' and 1 or 0) and applied==0 and spawned==0 and deleted==0)
assert(#e.queue==0)
assert(MODE=='context_changed' or not pcall(e.configureReaction,nil)) -- ownership cannot change mid-encounter
assert(files['nemesis-trace.jsonl']:find('person_promoted',1,true))
-- An offscreen hit is read from its event, never the current crosshair target.
local stranger={IsPlayer=function()return false end}
event.attackData.GetInstigator=function()return stranger end
hooks.hit(actor,event);assert(e.status().hits==1)
-- Capture-only observations update the final native position, without commands.
pos.x=9;e.update(.6)
if MODE~='context_changed'then
    assert(e.actors['original-1'].last.x==9)
    actor=nil;e.update(.6)
    assert(e.queue[#e.queue].kind=='body_ended' and e.queue[#e.queue].event.position.x==9)
end
e.cleanup();assert(removed==(MODE=='verified' and 1 or 0) and e.status().tracked==0 and deleted==0)
'''.replace("return 'crowd'return end", "return 'crowd'end"))

    def test_reload_recovers_previous_complete_outbox(self):
        try: h=LuaHarness()
        except RuntimeError as error: self.skipTest(str(error))
        self.addCleanup(h.close)
        module=Path(__file__).resolve().parents[1]/"mods/night_city_underworld/encounters.lua"
        h.run("MODULE="+json.dumps(str(module)))
        h.run(r'''
local files={['nemesis-outbox.json']='partial',
    ['nemesis-outbox.json.tmp']='partial replacement'}
local envelope={schema_version=1,queue={{key='actual-hit-actor',kind='hit',
    context={schema_version=1,slot='save-a',timeline='branch-a',session_id='old-session'},
    event={event_id='durable-hit-1',session_id='old-session',entity_id='actual-hit-actor'}}}}
files['nemesis-outbox.json.previous']=json.encode(envelope)..'\n'
-- The minimal harness represents tables as JSON objects; normalize its numeric
-- queue keys to Lua array indices to model CET's array decoder here.
local decode=json.decode
json.decode=function(raw)
    local value=decode(raw)
    if value.queue then local queue={};for k,item in pairs(value.queue)do queue[tonumber(k)]=item end;value.queue=queue end
    return value
end
io.open=function(path,mode)
    if not files[path]then return nil end
    return {read=function()return files[path]end,close=function()return true end}
end
ObserveAfter=function()end
local e=dofile(MODULE);e.initialize()
assert(#e.queue==1 and e.queue[1].event.event_id=='durable-hit-1')
assert(e.status().mode=='capture_only' and e.status().tracked==0)
''')
