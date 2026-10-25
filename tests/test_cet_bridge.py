import json
from pathlib import Path
import tempfile
import time
import unittest
from lua_harness import LuaHarness
from underworld.mailbox import Mailbox, atomic_json, SLOT, TIMELINE


class CetBridgeTest(unittest.TestCase):
    def test_real_lua_file_ipc_python_sqlite_roundtrip(self):
        try:
            lua = LuaHarness()
        except RuntimeError as error:
            self.skipTest(str(error))
        self.addCleanup(lua.close)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        directory = Path(folder.name)
        box = Mailbox(directory, directory / 'world.sqlite3')
        self.addCleanup(box.close)
        def pump():
            atomic_json(directory / 'bridge-status.json', {'version': '0.0.2', 'slot': SLOT,
                'timeline': TIMELINE, 'heartbeat': time.time()})
            box.poll()
            return True
        lua.callback('pump_python', pump)
        entrypoint = Path(__file__).resolve().parents[1] / 'mods/night_city_underworld/init.lua'
        lua.run('ROOT=' + json.dumps(str(directory)) + '; ENTRY=' + json.dumps(str(entrypoint)))
        lua.run('''
local realOpen = io.open
io.open = function(path, mode) return realOpen(ROOT .. '/' .. path, mode) end
local callbacks, clicked, text = {}, nil, {}
registerForEvent = function(name, fn) callbacks[name] = fn end
registerHotkey = function() end
print = function() end
ImGuiWindowFlags = {AlwaysAutoResize=0}
ImGui = {Begin=function() return true end, End=function() end, Separator=function() end,
         Text=function(value) text[#text+1]=value end, Button=function(label) return label == clicked end}
local function loadClient()
 callbacks={}; clicked=nil
 assert(dofile(ENTRY).version == '0.0.2')
 callbacks.onInit(); callbacks.onOverlayOpen()
end
local function frame(label)
 text={}; clicked=label; callbacks.onDraw(); clicked=nil
end
local function roundtrip()
 assert(pump_python()); callbacks.onUpdate(0.3)
end
loadClient(); roundtrip(); frame(nil)
assert(table.concat(text,';'):find('Python-Kern: verbunden',1,true))
assert(table.concat(text,';'):find('Ruf vom Python-Kern: 0',1,true))
frame('Kontakt helfen (+15)')
-- There is no optimistic Lua consequence before Python has committed.
frame(nil); assert(table.concat(text,';'):find('Ruf vom Python-Kern: 0',1,true))
roundtrip(); frame(nil)
assert(table.concat(text,';'):find('Ruf vom Python-Kern: 15',1,true))
frame('Letztes Ereignis wiederholen'); roundtrip(); frame(nil)
assert(table.concat(text,';'):find('Ruf vom Python-Kern: 15',1,true))
assert(table.concat(text,';'):find('Ereignisse: 1 / 100',1,true))
frame('Lieferung untersuchen'); roundtrip()
frame('Klinik aufdecken'); roundtrip(); frame(nil)
assert(table.concat(text,';'):find('Klinik-Kontakt entdeckt',1,true))
loadClient(); roundtrip(); roundtrip(); frame(nil)
assert(table.concat(text,';'):find('Ruf vom Python-Kern: 15',1,true))
-- A new harm request survives a CET reload before acknowledgement.
frame('Kontakt schaedigen (-20)'); loadClient(); roundtrip(); roundtrip(); frame(nil)
assert(table.concat(text,';'):find('Ruf vom Python-Kern: -5',1,true))
''')
        self.assertEqual(box.snapshot()['reputation'], -5)
        self.assertEqual(box.snapshot()['event_count'], 4)
