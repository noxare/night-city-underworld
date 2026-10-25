import json
from pathlib import Path
import unittest
from lua_harness import LuaHarness


class NpcProbeTest(unittest.TestCase):
    def test_opt_in_actor_filter_bounded_hits_and_no_entity_retention(self):
        try: lua=LuaHarness()
        except RuntimeError as error: self.skipTest(str(error))
        self.addCleanup(lua.close)
        path=Path(__file__).resolve().parents[1]/'mods/night_city_underworld/npc_probe.lua'
        lua.run('PROBE='+json.dumps(str(path)))
        lua.run('''
local hit
ObserveAfter=function(class,method,callback)
 assert(class=='ScriptedPuppet' and method=='OnHit'); hit=callback
end
local actor={IsNPC=function()return true end,GetEntityID=function()return {hash='actor-1'} end}
Game={GetPlayer=function()return {} end,GetTargetingSystem=function()return {GetLookAtObject=function()return actor end} end}
io.open=function()return {write=function()return true end,close=function()return true end} end
local p=dofile(PROBE)
p.initialize();p.update(1)
assert(p.status().entity_id==nil)
p.enable(true);p.update(.5)
assert(p.status().entity_id=='actor-1')
for i=1,30 do hit(actor,{hitColliderTag='raw-leg-tag'}) end
assert(p.status().observed_hits==30 and #p.status().collider_tags==16)
assert(p.status().body_zone=='unknown')
p.enable(false);hit(actor,{hitColliderTag='ignored'})
assert(p.status().observed_hits==30)
-- Disabling must not read game targets, and unloading must clear stale identity.
Game.GetPlayer=function()error('must not run while disabled')end
p.update(1)
assert(p.status().enabled==false)
Game.GetPlayer=function()return nil end
p.enable(true);p.update(.5)
assert(p.status().entity_id==nil and p.status().observed_hits==0)
-- A failed hook registration is explicit and does not escape into CET.
ObserveAfter=function()error('hook unavailable')end
local failed=dofile(PROBE)
failed.initialize()
assert(failed.status().hit_observer_registered==false)
assert(failed.status().last_error~=nil)
''')

    def test_entrypoint_exposes_opt_in_controls_without_changing_bridge_version(self):
        try: lua=LuaHarness()
        except RuntimeError as error: self.skipTest(str(error))
        self.addCleanup(lua.close)
        root=Path(__file__).resolve().parents[1]/'mods/night_city_underworld'
        lua.run('ROOT='+json.dumps(str(root)))
        lua.run('''
package.path=ROOT..'/?.lua;'..package.path
local callbacks,clicked,text={},{},{}
registerForEvent=function(name,fn)callbacks[name]=fn end
registerHotkey=function()end
ObserveAfter=function()end
print=function()end
Game={GetPlayer=function()return {}end,GetTargetingSystem=function()return {GetLookAtObject=function()return nil end}end}
io.open=function(_,mode)
 if mode=='r' then return nil end
 return {write=function()return true end,close=function()return true end}
end
ImGuiWindowFlags={AlwaysAutoResize=0}
ImGui={Begin=function()return true end,End=function()end,Separator=function()end,
 Text=function(value)text[#text+1]=value end,Button=function(label)return clicked==label end}
assert(dofile(ROOT..'/init.lua').version=='0.0.2')
callbacks.onInit();callbacks.onOverlayOpen()
clicked='NPC-Erfassung starten';callbacks.onDraw();clicked=nil
callbacks.onUpdate(.5);text={};callbacks.onDraw()
local shown=table.concat(text,';')
assert(shown:find('NPC-Meilenstein Build 0.0.3',1,true))
assert(shown:find('NPC-Erfassung: aktiv',1,true))
''')
