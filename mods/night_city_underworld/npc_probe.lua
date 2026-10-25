-- Opt-in read-only feasibility probe. Never changes NPC AI or animations.
local Probe = {enabled=false, registered=false, elapsed=0, dirty=false}
local session = tostring(os.time()) .. '-' .. tostring({}):gsub('[^%w]','')
local snapshot = {schema_version=1,session_id=session,identity_scope='session_only',
    observed_hits=0,collider_tags={},body_zone='unknown',animation_control='unverified'}

function Probe.enable(value)
    Probe.enabled = value == true
    snapshot.enabled = Probe.enabled
    Probe.dirty = true
end

function Probe.initialize()
    if Probe.registered then return end
    local ok = pcall(function()
        ObserveAfter('ScriptedPuppet','OnHit',function(actor,event)
            if not Probe.enabled or not snapshot.entity_id then return end
            pcall(function()
                if not actor:IsNPC() then return end
                local id=tostring(actor:GetEntityID().hash)
                if id ~= snapshot.entity_id then return end
                snapshot.observed_hits=snapshot.observed_hits+1
                local tag=tostring(event.hitColliderTag):sub(1,80)
                if #snapshot.collider_tags < 16 then
                    snapshot.collider_tags[#snapshot.collider_tags+1]=tag
                end
                snapshot.last_hit_source='ScriptedPuppet.OnHit / gameHitEvent.hitColliderTag'
                -- Raw collider tags are evidence, not an assumed anatomical mapping.
                snapshot.body_zone='unknown'
                Probe.dirty=true
            end)
        end)
    end)
    Probe.registered=ok
    snapshot.hit_observer_registered=ok
    Probe.dirty=true
end

function Probe.update(delta)
    Probe.elapsed=Probe.elapsed+delta
    if Probe.elapsed < .5 then return end
    Probe.elapsed=0
    if Probe.enabled then
        local ok=pcall(function()
            local player=Game.GetPlayer()
            if not player then snapshot.player_loaded=false; return end
            snapshot.player_loaded=true
            local target=Game.GetTargetingSystem():GetLookAtObject(player,false,false)
            if target and target:IsNPC() then
                local id=tostring(target:GetEntityID().hash)
                if id ~= snapshot.entity_id then
                    snapshot.entity_id=id
                    snapshot.observed_hits=0
                    snapshot.collider_tags={}
                    snapshot.last_hit_source=nil
                end
            end
        end)
        snapshot.target_api_available=ok
        Probe.dirty=true
    end
    if not Probe.dirty then return end
    local ok=pcall(function()
        snapshot.updated_at=os.time()
        local encoded=json.encode(snapshot)..'\n'
        if #encoded > 16384 then return end
        local file=io.open('npc-probe.json','w')
        if file then file:write(encoded);file:close() end
    end)
    if ok then Probe.dirty=false end
end

function Probe.status() return snapshot end
return Probe
