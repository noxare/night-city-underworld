-- 0.0.2: CET is a thin file-IPC client. Only Python/SQLite calculate consequences.
local version = '0.0.2'
local slot, timeline = 'underworld-bridge-demo', 'v1'
local visible, overlay, ready = true, false, false
local state, pending, lastEvent = nil, nil, nil
local refreshAfterAck, connected = false, false
local elapsed, sequence = 0, 0
local session = tostring(os.time()) .. '-' .. tostring({}):gsub('[^%w]', '')
local message = 'Python-Kern wird gesucht ...'
local position = 'Noch nicht abgefragt'
local encounters = nil
local encounterError = nil
local debugTools = false -- manual clone controls are development-only
local injuryTest = nil
local injuryTestError = nil
local npcProbe = nil
local npcProbeError = nil

local function readJSON(path)
    local file = io.open(path, 'r')
    if not file then return nil end
    local raw = file:read(16385)
    file:close()
    if not raw or #raw > 16384 or raw:sub(-1) ~= '\n' then return nil end
    local ok, data = pcall(json.decode, raw)
    if ok and type(data) == 'table' then return data end
    return nil
end

local function writePending()
    if not pending then return end
    local file = io.open('bridge-request.json', 'w')
    if not file then message = 'Anfrage konnte nicht geschrieben werden'; return end
    local written = file:write(json.encode(pending) .. '\n')
    local closed = file:close()
    message = written and closed and 'Warte auf Antwort vom Python-Kern ...' or 'Schreibfehler - dieselbe Anfrage erneut senden'
end

local function queue(event)
    if pending then return end
    sequence = sequence + 1
    local id = session .. '-' .. sequence
    if type(event) == 'string' then
        event = {event_id = 'cet-' .. id, npc_id = 'mara-quinn-demo', kind = event}
    end
    pending = {protocol_version = 1, request_id = id, slot = slot, timeline = timeline, event = event or false}
    writePending()
    print('[Underworld] BRIDGE_SEND ' .. id)
end

local function validState(value)
    return type(value) == 'table' and type(value.reputation) == 'number'
        and value.reputation >= -100 and value.reputation <= 100
        and type(value.event_count) == 'number' and value.event_count >= 0 and value.event_count <= 100
        and type(value.shipment) == 'boolean' and type(value.clinic) == 'boolean'
        and type(value.discovered) == 'boolean'
end

local function poll()
    local health = readJSON('bridge-status.json')
    connected = health ~= nil and health.version == version and health.slot == slot
        and health.timeline == timeline and type(health.heartbeat) == 'number'
        and math.abs(os.time() - health.heartbeat) < 6
    if not pending then return end
    local response = readJSON('bridge-response.json')
    if not response or response.protocol_version ~= 1 or response.slot ~= slot
        or response.timeline ~= timeline or response.request_id ~= pending.request_id
        or not validState(response.state) then return end
    if response.status ~= 'applied' and response.status ~= 'duplicate'
        and response.status ~= 'snapshot' and response.status ~= 'rejected' then return end
    state = response.state
    if response.status == 'applied' or response.status == 'duplicate' then lastEvent = pending.event end
    message = 'Python-Kern: ' .. response.status
    print('[Underworld] BRIDGE_ACK ' .. response.request_id .. ' status=' .. response.status .. ' reputation=' .. state.reputation)
    pending = nil
    if refreshAfterAck then refreshAfterAck = false; queue(false) end
end

registerForEvent('onInit', function()
    local autoOK,auto=pcall(require,'encounters')
    if autoOK then
        encounters=auto
        local ok,err=pcall(encounters.initialize)
        if not ok then encounterError=tostring(err) end
    else encounterError=tostring(auto) end
    local loaded,test=pcall(require,'injury_test')
    if loaded then injuryTest=test else injuryTestError=tostring(test);print('[Underworld InjuryTest] LOAD_ERROR '..injuryTestError) end
    local loaded,probe = pcall(require,'npc_probe')
    if loaded and type(probe) == 'table' then
        npcProbe=probe
        local initialized=pcall(npcProbe.initialize)
        if not initialized then npcProbeError='NPC-Probe konnte nicht initialisiert werden' end
    else
        npcProbeError='NPC-Modul nicht installiert oder nicht ladbar'
    end
    -- Resume the durable request instead of losing it on a CET reload.
    local old = readJSON('bridge-request.json')
    if old and old.protocol_version == 1 and old.slot == slot and old.timeline == timeline
        and type(old.request_id) == 'string' and #old.request_id <= 128 then
        pending = old
        refreshAfterAck = true
    else
        queue(false)
    end
    ready = true
    print('[Underworld] INIT v' .. version .. ' external Python bridge')
end)
registerForEvent('onUpdate', function(delta)
    if not ready then return end
    if encounters then
        local ok,err=pcall(encounters.update,delta)
        if not ok then encounterError=tostring(err) end
    end
    if debugTools and injuryTest then
        local ok,err=pcall(injuryTest.update,delta)
        if not ok then injuryTestError=tostring(err) end
    end
    if npcProbe then
        local observed=pcall(npcProbe.update,delta)
        if not observed then npcProbeError='NPC-Probe pausiert nach Lesefehler';pcall(npcProbe.enable,false) end
    end
    elapsed = elapsed + delta
    if elapsed < 0.25 then return end
    elapsed = 0
    local ok = pcall(poll)
    if not ok then connected = false; message = 'Bridge-Lesefehler; Spiel laeuft weiter' end
end)
registerForEvent('onOverlayOpen', function() overlay = true; visible = true end)
registerForEvent('onOverlayClose', function() overlay = false end)
registerHotkey('underworld_toggle', 'Underworld: Testfenster anzeigen', function() visible = not visible end)

registerForEvent('onDraw', function()
    if not ready or not visible then return end
    if ImGui.Begin('Night City: Underworld - Nemesis', ImGuiWindowFlags.AlwaysAutoResize) then
        ImGui.Text('Underworld Build 0.1.0-dev | Automatische Trefferreaktion')
        ImGui.Text('Keine manuelle Spawn-/Verletzungssequenz erforderlich')
        if encounters then
            local value=encounters.status()
            ImGui.Text(value.last)
            ImGui.Text('Verfolgte Original-NPCs: '..tostring(value.tracked))
            ImGui.Text('Direkte Treffer durch V: '..tostring(value.hits))
            ImGui.Text('Person dauerhaft im Kern; Spielkoerper sitzungsgebunden')
            ImGui.Text('Identisches Wiedererzeugen und Gangart noch nicht ingame bestaetigt')
            if value.last_error then ImGui.Text(value.last_error) end
            if value.log_error then ImGui.Text(value.log_error) end
        end
        if encounterError then ImGui.Text('Nemesis-Adapter: '..encounterError) end
        if debugTools and injuryTest then injuryTest.draw(overlay) end
    end
    ImGui.End()
end)
registerForEvent('onShutdown',function()
    if encounters then pcall(encounters.cleanup,'shutdown') end
    if injuryTest then pcall(injuryTest.cleanup) end
end)
return {version = version}
