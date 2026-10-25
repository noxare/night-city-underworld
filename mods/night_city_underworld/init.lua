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
    if ImGui.Begin('Night City: Underworld - Bridge', ImGuiWindowFlags.AlwaysAutoResize) then
        ImGui.Text('UNDERWORLD Bridge ' .. version)
        ImGui.Text(connected and 'Python-Kern: verbunden' or 'Python-Kern: offline / startet')
        ImGui.Text('Separates Demo-Profil - keine Kampagnen-Synchronisierung')
        ImGui.Text('Kontakt: Mara Quinn (Testkontakt)')
        if state then
            ImGui.Text('Ruf vom Python-Kern: ' .. state.reputation)
            ImGui.Text('In SQLite gespeicherte Ereignisse: ' .. state.event_count .. ' / 100')
            if state.shipment then ImGui.Text('Hinweis: illegale Cyberware-Lieferung bekannt') end
            if state.clinic then ImGui.Text('Lieferpapiere nennen eine Hinterhof-Klinik') end
            if state.discovered then ImGui.Text('Klinik-Kontakt entdeckt (Testdaten)') end
        else
            ImGui.Text('Noch kein bestaetigter Zustand vom Python-Kern')
        end
        ImGui.Text('V-Position: ' .. position)
        if overlay then
            if ImGui.Button('V-Position aus Spiel lesen') then
                local ok, value = pcall(function()
                    local player = Game.GetPlayer()
                    if not player then return 'Kein geladener Spielstand' end
                    local p = player:GetWorldPosition()
                    return string.format('X %.1f / Y %.1f / Z %.1f', p.x, p.y, p.z)
                end)
                position = ok and value or 'Spiel-API nicht verfuegbar'
            end
            if pending then
                if ImGui.Button('Anfrage erneut senden') then writePending() end
            elseif connected and state then
                if ImGui.Button('Kontakt helfen (+15)') then queue('civilian_helped') end
                if ImGui.Button('Kontakt schaedigen (-20)') then queue('civilian_harmed') end
                if ImGui.Button('Lieferung untersuchen') then queue('shipment_investigated') end
                if ImGui.Button('Klinik aufdecken') then queue('clinic_discovered') end
                if lastEvent and ImGui.Button('Letztes Ereignis wiederholen') then queue(lastEvent) end
                if ImGui.Button('Status vom Kern laden') then queue(false) end
            else
                if ImGui.Button('Status vom Kern laden') then queue(false) end
            end
            if ImGui.Button('Fenster ausblenden') then visible = false end
        else
            ImGui.Text('Zum Bedienen das CET-Overlay oeffnen.')
        end
        ImGui.Separator()
        ImGui.Text(message)
    end
    ImGui.End()
end)
return {version = version}
