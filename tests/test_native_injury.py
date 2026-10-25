import json
from pathlib import Path
import unittest
from lua_harness import LuaHarness


class NativeInjuryTest(unittest.TestCase):
    def test_owned_clone_status_application_removal_and_timed_cleanup(self):
        try: h=LuaHarness()
        except RuntimeError as e:self.skipTest(str(e))
        self.addCleanup(h.close)
        p=Path(__file__).resolve().parents[1]/'mods/night_city_underworld/injury_test.lua'
        h.run('MODULE='+json.dumps(str(p)))
        h.run('''
local chosen,deleted,applied,removed,created=nil,0,0,0,0
local sent=0;local pos={x=0,y=0,z=0}
local controller={SendCommand=function(_,cmd)assert(cmd.ignoreNavigation==false);sent=sent+1 end,CancelCommand=function()end}
local actor={GetAIControllerComponent=function()return controller end,GetWorldPosition=function()return pos end}
local player={GetWorldPosition=function()return {x=0,y=0,z=0}end,GetWorldForward=function()return {x=1,y=0}end,GetWorldOrientation=function()return {}end}
local target={IsNPC=function()return true end,IsCrowd=function()return true end,GetRecordID=function()return 'crowd-record'end}
local s={IsReady=function()return true end,IsPopulated=function()return false end,
CreateEntity=function(_,spec)assert(not spec.persistState and not spec.persistSpawn);created=created+1;return 'owned'end,
IsTagged=function(_,id) return id=='owned'end,GetEntity=function()return actor end,DeleteTagged=function()deleted=deleted+1 end}
Game={GetDynamicEntitySystem=function()return s end,GetPlayer=function()return player end,
GetTargetingSystem=function()return {GetLookAtObject=function()return target end}end,
GetStatusEffectSystem=function()return {RemoveStatusEffect=function(_,id)assert(id=='owned');removed=removed+1 end}end}
CName={new=function(x)return x end};TweakDBID=CName
WorldPosition={new=function()return {SetVector4=function()end}end};AIPositionSpec={new=function()return {SetWorldPosition=function()end}end};AIMoveToCommand={new=function()return {}end};moveMovementType={Walk=1}
Vector4={new=function()return {}end};DynamicEntitySpec={new=function()return {}end}
TweakDB={GetRecord=function()return {}end}
StatusEffectHelper={ApplyStatusEffect=function(a)assert(a==actor);applied=applied+1 end}
registerForEvent=nil;print=function()end
ImGui={Separator=function()end,Text=function()end,Button=function(x)return x==chosen end}
local t=dofile(MODULE)
local function click(x)chosen=x;t.draw(true);chosen=nil end
click('Eigenen Test-NPC erzeugen');assert(created==1)
t.update(2);assert(sent==1);pos.x=2;t.update(.1);assert(t.distance==2)
click('Test-NPC gehen lassen (6 m)');assert(sent==2)
click('Eigenen Test-NPC erzeugen');assert(created==1)
click('Linkes Bein: nativen Effekt anwenden');assert(applied==1)
click('Beineffekte entfernen');assert(removed==2)
t.update(61);assert(deleted==1 and t.id==nil)
''')
