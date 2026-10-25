-- Pure deterministic sandbox rules. No game handles or vanilla state.
local Demo = {}
local kinds = {civilian_helped = 15, civilian_harmed = -20,
               shipment_investigated = 0, clinic_discovered = 0}

function Demo.new()
    return {schema_version = 1, events = {}, seen = {}, total = 0,
            shipment = false, clinic = false, discovered = false, count = 0}
end

function Demo.validate(event)
    if type(event) ~= 'table' or event.schema_version ~= 1 then
        return false, 'Ungueltige Ereignisversion'
    end
    if type(event.event_id) ~= 'string' or not event.event_id:match('^demo%-%d+$')
       or #event.event_id > 32 or kinds[event.kind] == nil then
        return false, 'Ungueltiges Testereignis'
    end
    local fields = 0
    for _ in pairs(event) do fields = fields + 1 end
    if fields ~= 3 then return false, 'Unerwartete Ereignisfelder' end
    return true
end

function Demo.check(state, event)
    local valid, message = Demo.validate(event)
    if not valid then return false, message end
    local previous = state.seen[event.event_id]
    if previous then
        if previous ~= event.kind then return false, 'Ereignis-ID hat anderen Inhalt' end
        return true, 'duplicate'
    end
    if state.count >= 100 then return false, 'Testlimit erreicht (100 Ereignisse)' end
    if event.event_id ~= 'demo-' .. (state.count + 1) then return false, 'Falsche Ereignisreihenfolge' end
    if event.kind == 'shipment_investigated' and (not state.shipment or state.clinic) then
        return false, 'Keine offene Lieferung bekannt'
    end
    if event.kind == 'clinic_discovered' and (not state.clinic or state.discovered) then
        return false, 'Zuerst die Lieferung untersuchen'
    end
    return true, 'applied'
end

function Demo.apply(state, event)
    local ok, status = Demo.check(state, event)
    if not ok or status == 'duplicate' then return ok, status end
    state.seen[event.event_id] = event.kind
    state.count = state.count + 1
    state.events[state.count] = event
    state.total = state.total + kinds[event.kind]
    if event.kind == 'civilian_helped' then state.shipment = true end
    if event.kind == 'shipment_investigated' then state.clinic = true end
    if event.kind == 'clinic_discovered' then state.discovered = true end
    return true, status
end

function Demo.reputation(state)
    return math.max(-100, math.min(100, state.total))
end

return Demo
