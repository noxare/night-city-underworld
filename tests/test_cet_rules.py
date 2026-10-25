"""Run actual Lua rules using system liblua when available; never imply CET verification."""
import ctypes
import ctypes.util
import json
from pathlib import Path
import unittest


class CetRulesTest(unittest.TestCase):
    def test_lua_rules_and_entrypoint_syntax(self):
        library = ctypes.util.find_library('lua5.4')
        if not library:
            self.skipTest('system Lua 5.4 not installed; run on the development host')
        lua = ctypes.CDLL(library)
        lua.luaL_newstate.restype = ctypes.c_void_p
        lua.luaL_openlibs.argtypes = [ctypes.c_void_p]
        lua.luaL_loadstring.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        lua.lua_pcallk.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ssize_t, ctypes.c_void_p]
        lua.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_size_t)]
        lua.lua_tolstring.restype = ctypes.c_char_p
        lua.lua_close.argtypes = [ctypes.c_void_p]
        root = Path(__file__).resolve().parents[1] / 'mods/night_city_underworld'
        code = '''
local Demo = dofile(DEMO_PATH)
assert(loadfile(INIT_PATH))
local state = Demo.new()
local function event(id, kind) return {schema_version=1,event_id='demo-'..id,kind=kind} end
assert(not Demo.apply(state, event(1, 'clinic_discovered')))
assert(not Demo.apply(state, event(1, 'shipment_investigated')))
assert(Demo.apply(state, event(1, 'civilian_helped')))
assert(Demo.reputation(state) == 15 and state.shipment)
local ok, status = Demo.apply(state, event(1, 'civilian_helped'))
assert(ok and status == 'duplicate' and state.count == 1)
assert(not Demo.apply(state, event(1, 'civilian_harmed')))
assert(not Demo.apply(state, event(9, 'civilian_helped')))
assert(Demo.apply(state, event(2, 'shipment_investigated')))
assert(Demo.apply(state, event(3, 'clinic_discovered')))
assert(state.discovered)
assert(not Demo.apply(state, event(4, 'clinic_discovered')))
assert(Demo.apply(state, event(4, 'civilian_harmed')))
assert(Demo.reputation(state) == -5)
local restored = Demo.new()
for _, e in ipairs(state.events) do assert(Demo.apply(restored, e)) end
assert(restored.discovered and Demo.reputation(restored) == -5)
for i=5,100 do assert(Demo.apply(restored, event(i,'civilian_helped'))) end
assert(Demo.reputation(restored) == 100)
assert(not Demo.apply(restored, event(101,'civilian_helped')))
assert(not Demo.validate({schema_version=99,event_id='demo-1',kind='civilian_helped'}))
assert(not Demo.validate({schema_version=1,event_id='demo-1',kind='civilian_helped',extra=1}))
'''.replace('DEMO_PATH', json.dumps(str(root / 'demo.lua'))).replace('INIT_PATH', json.dumps(str(root / 'init.lua'))).replace('PACKAGE_DIR', json.dumps(str(root)))
        state = lua.luaL_newstate()
        self.assertTrue(state)
        try:
            lua.luaL_openlibs(state)
            result = lua.luaL_loadstring(state, code.encode())
            if result == 0:
                result = lua.lua_pcallk(state, 0, 0, 0, 0, None)
            if result:
                self.fail(lua.lua_tolstring(state, -1, None).decode())
        finally:
            lua.lua_close(state)
