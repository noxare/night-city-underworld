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
''')
