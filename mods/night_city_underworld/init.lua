-- Underworld 0.0.1: visible CET sandbox; no game mutations or background work.
local Demo = require('demo')
local state = Demo.new()
local visible = true
local overlay = false
local ready = false
local writable = true
local message = 'Initialisierung ...'
local version = '0.0.1'
local journal = 'demo-events.jsonl'
local position = 'Noch nicht abgefragt'
local drawLogged = false

local function loadJournal()
    local file = io.open(journal, 'r')
    if not file then return true end
    local contents = file:read(65537)
    file:close()
    if not contents or #contents > 65536 then return false end
    -- A partial last write is never silently ignored or overwritten.
    if #contents > 0 and contents:sub(-1) ~= '\n' then return false end
    for line in contents:gmatch('[^\n]+') do
        local decoded, event = pcall(json.decode, line)
        if not decoded or not Demo.apply(state, event) then return false end
    end
    return true
end

local function emit(kind, replay)
    if not ready or not writable then return end
    local event = replay or {schema_version = 1, event_id = 'demo-' .. (state.count + 1), kind = kind}
    local ok, status = Demo.check(state, event)
    if not ok then message = status; return end
    if status == 'duplicate' then
        message = 'Duplikat ignoriert: Ruf unveraendert'
        print('[Underworld] duplicate ' .. event.event_id)
        return
    end
    local encoded = json.encode(event) .. '\n'
    local file, err = io.open(journal, 'a')
    if not file then message = 'Speichern fehlgeschlagen'; print('[Underworld] IO error: ' .. tostring(err)); return end
    local written = file:write(encoded)
    local closed = file:close()
    if not written or not closed then
        writable = false
        message = 'Schreibfehler: Test gestoppt; Journal pruefen'
        return
    end
    Demo.apply(state, event)
    message = 'Gespeichert: ' .. event.kind
    print('[Underworld] applied ' .. event.event_id .. ' ' .. event.kind)
end

registerForEvent('onInit', function()
    local ok, result = pcall(loadJournal)
    writable = ok and result
    ready = true
    message = writable and 'Bereit - CET hat Underworld geladen' or 'Journal ungueltig: nur Anzeige, Datei bleibt erhalten'
    print('[Underworld] INIT v' .. version .. ' events=' .. state.count .. ' writable=' .. tostring(writable))
end)

registerForEvent('onOverlayOpen', function() overlay = true; visible = true end)
registerForEvent('onOverlayClose', function() overlay = false end)
registerHotkey('underworld_toggle', 'Underworld: Testfenster anzeigen', function() visible = not visible end)

registerForEvent('onDraw', function()
    if not ready or not visible then return end
    if not drawLogged then print('[Underworld] DRAW v' .. version); drawLogged = true end
    if ImGui.Begin('Night City: Underworld - Prototype', ImGuiWindowFlags.AlwaysAutoResize) then
        ImGui.Text('UNDERWORLD ' .. version .. ' | Erster Ingame-Prototyp')
        ImGui.Text('Sandbox-Testdaten - noch keine echten NPC-Aktionen')
        ImGui.Separator()
        ImGui.Text('Kontakt: Mara Quinn (fiktiver Testkontakt)')
        ImGui.Text('Ruf: ' .. Demo.reputation(state) .. ' / -100 bis +100')
        ImGui.Text('Gespeicherte Ereignisse: ' .. state.count .. ' / 100')
        ImGui.Text('V-Position: ' .. position)
        if state.shipment then ImGui.Text('Hinweis: illegale Cyberware-Lieferung bekannt') end
        if state.clinic then ImGui.Text('Spur: Lieferpapiere nennen eine Hinterhof-Klinik') end
        if state.discovered then ImGui.Text('Entdeckt: illegale Klinik / Kontakt freigeschaltet (Testdaten)') end
        if overlay and writable then
            if ImGui.Button('V-Position aus Spiel lesen') then
                local ok, value = pcall(function()
                    local player = Game.GetPlayer()
                    if not player then return 'Kein geladener Spielstand' end
                    local p = player:GetWorldPosition()
                    return string.format('X %.1f / Y %.1f / Z %.1f', p.x, p.y, p.z)
                end)
                position = ok and value or 'Spiel-API nicht verfuegbar'
                print('[Underworld] PLAYER_READ ' .. position)
            end
            if ImGui.Button('Kontakt helfen (+15)') then emit('civilian_helped') end
            if ImGui.Button('Kontakt schaedigen (-20)') then emit('civilian_harmed') end
            if ImGui.Button('Lieferung untersuchen') then emit('shipment_investigated') end
            if ImGui.Button('Klinik aufdecken') then emit('clinic_discovered') end
            if state.count > 0 and ImGui.Button('Letztes Ereignis wiederholen') then
                emit(nil, state.events[state.count])
            end
        else
            ImGui.Text('Zum Bedienen das CET-Overlay oeffnen.')
        end
        ImGui.Separator()
        ImGui.Text(message)
        local first = math.max(1, state.count - 4)
        for i = first, state.count do
            local event = state.events[i]
            ImGui.Text(event.event_id .. ': ' .. event.kind)
        end
        if overlay and ImGui.Button('Fenster ausblenden') then visible = false end
    end
    ImGui.End()
end)

return {version = version}
