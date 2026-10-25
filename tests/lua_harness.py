"""Small liblua harness: real Lua client + Python JSON codec, no CET engine claims."""
import ctypes as C
import ctypes.util
import json


class LuaHarness:
    def __init__(self):
        library = ctypes.util.find_library('lua5.4')
        if not library:
            raise RuntimeError('system Lua 5.4 unavailable')
        self.lib = C.CDLL(library)
        p, i = C.c_void_p, C.c_int
        def bind(name, result, args):
            function = getattr(self.lib, name)
            function.restype, function.argtypes = result, args
            setattr(self, name, function)
        bind('luaL_newstate', p, [])
        bind('luaL_openlibs', None, [p])
        bind('luaL_loadstring', i, [p, C.c_char_p])
        bind('lua_pcallk', i, [p, i, i, i, C.c_ssize_t, p])
        bind('lua_tolstring', C.c_char_p, [p, i, C.POINTER(C.c_size_t)])
        bind('lua_gettop', i, [p])
        bind('lua_settop', None, [p, i])
        bind('lua_type', i, [p, i])
        bind('lua_toboolean', i, [p, i])
        bind('lua_tonumberx', C.c_double, [p, i, p])
        bind('lua_pushnil', None, [p])
        bind('lua_next', i, [p, i])
        bind('lua_pushlstring', p, [p, C.c_char_p, C.c_size_t])
        bind('lua_pushnumber', None, [p, C.c_double])
        bind('lua_pushinteger', None, [p, C.c_longlong])
        bind('lua_pushboolean', None, [p, i])
        bind('lua_createtable', None, [p, i, i])
        bind('lua_setfield', None, [p, i, C.c_char_p])
        bind('lua_pushcclosure', None, [p, p, i])
        bind('lua_setglobal', None, [p, C.c_char_p])
        bind('lua_close', None, [p])
        self.state = self.luaL_newstate()
        self.luaL_openlibs(self.state)
        self.callbacks, self.errors = [], []
        self.callback('python_encode', lambda: json.dumps(self.read(1), separators=(',', ':')))
        self.callback('python_decode', lambda: json.loads(self.read(1)))
        self.run('json = {encode=python_encode,decode=python_decode}')

    def read(self, index):
        state = self.state
        index = index if index > 0 else self.lua_gettop(state) + index + 1
        kind = self.lua_type(state, index)
        if kind == 0: return None
        if kind == 1: return bool(self.lua_toboolean(state, index))
        if kind == 3:
            number = self.lua_tonumberx(state, index, None)
            return int(number) if number.is_integer() else number
        if kind == 4: return self.lua_tolstring(state, index, None).decode()
        if kind == 5:
            result = {}
            self.lua_pushnil(state)
            while self.lua_next(state, index):
                result[self.read(-2)] = self.read(-1)
                self.lua_settop(state, -2)
            return result
        raise ValueError('unsupported Lua value')

    def push(self, value):
        state = self.state
        if value is None: self.lua_pushnil(state)
        elif isinstance(value, bool): self.lua_pushboolean(state, value)
        elif isinstance(value, int): self.lua_pushinteger(state, value)
        elif isinstance(value, float): self.lua_pushnumber(state, value)
        elif isinstance(value, str):
            raw = value.encode(); self.lua_pushlstring(state, raw, len(raw))
        elif isinstance(value, dict):
            self.lua_createtable(state, 0, len(value))
            for key, item in value.items():
                self.push(item); self.lua_setfield(state, -2, str(key).encode())
        else: raise ValueError('unsupported Python value')

    def callback(self, name, function):
        @C.CFUNCTYPE(C.c_int, C.c_void_p)
        def call(_):
            try:
                self.push(function())
            except Exception as error:
                self.errors.append(error)
                self.lua_pushnil(self.state)
            return 1
        self.callbacks.append(call)
        self.lua_pushcclosure(self.state, C.cast(call, C.c_void_p), 0)
        self.lua_setglobal(self.state, name.encode())

    def run(self, code):
        status = self.luaL_loadstring(self.state, code.encode())
        if status == 0:
            status = self.lua_pcallk(self.state, 0, 0, 0, 0, None)
        if status:
            raise AssertionError(self.lua_tolstring(self.state, -1, None).decode())
        if self.errors:
            raise AssertionError(str(self.errors))

    def close(self):
        self.lua_close(self.state)
