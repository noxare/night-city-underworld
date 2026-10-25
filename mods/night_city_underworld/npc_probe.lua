-- Opt-in read-only feasibility probe. Never changes NPC AI or animations.
local Probe = {enabled=false, registered=false, elapsed=0, dirty=false}
local session = tostring(os.time()) .. '-' .. tostring({}):gsub('[^%w]','')
local snapshot = {schema_version=1,session_id=session,identity_scope='session_only',
    enabled=false,target_active=false,observed_hits=0,collider_tags={},body_zone='unknown',animation_control='unverified'}

local function clearTarget()
    snapshot.entity_id=nil
    snapshot.target_active=false
    snapshot.observed_hits=0
    snapshot.collider_tags={}
    snapshot.last_hit_source=nil
    snapshot.native_reaction_part=nil
    snapshot.native_reaction_time=nil
    snapshot.native_reaction_source=nil
    snapshot.reaction_mapping_profile=nil
end

function Probe.enable(value)
    Probe.enabled = value == true
    snapshot.enabled = Probe.enabled
    if not Probe.enabled then snapshot.target_active=false end
    Probe.dirty = true
end

function Probe.initialize()
    if Probe.registered then return end
    local ok = pcall(function()
        ObserveAfter('ScriptedPuppet','OnHit',function(actor,event)
            if not Probe.enabled or not snapshot.target_active or not snapshot.entity_id then return end
            local readable = pcall(function()
                if not actor:IsNPC() then return end
                local id=tostring(actor:GetEntityID().hash)
                if id ~= snapshot.entity_id then return end
                snapshot.observed_hits=snapshot.observed_hits+1
                local tagOK,tag = pcall(function() return tostring(event.hitColliderTag):sub(1,80) end)
                if tagOK and tag ~= 'nil' and #snapshot.collider_tags < 16 then
                    snapshot.collider_tags[#snapshot.collider_tags+1]=tag
                end
                snapshot.last_hit_source=tagOK and 'ScriptedPuppet.OnHit / gameHitEvent.hitColliderTag' or 'ScriptedPuppet.OnHit / collider unavailable'
                -- Raw collider tags are evidence, not an assumed anatomical mapping.
                snapshot.body_zone='unknown'
                Probe.dirty=true
            end)
            if not readable then snapshot.last_error='Hit-Daten nicht lesbar'; Probe.dirty=true end
        end)
    end)
    -- Observe the native reaction separately: it is not assumed to be the same OnHit.
    local reactionOK=pcall(function()
        ObserveAfter('HitReactionComponent','SendDataToAIBehavior',function(component)
            if not Probe.enabled or not snapshot.entity_id then return end
            pcall(function()
                local owner=component:GetOwner()
                if not owner or tostring(owner:GetEntityID().hash) ~= snapshot.entity_id then return end
                local data=component:GetHitReactionData()
                local part=tonumber(data.hitBodyPart)
                local stamp=tonumber(component:GetLastHitTimeStamp())
                if not part or not stamp or part < 0 or part > 6 then return end
                snapshot.native_reaction_part=part
                snapshot.native_reaction_time=stamp
                snapshot.native_reaction_source='HitReactionComponent.SendDataToAIBehavior'
                snapshot.reaction_mapping_profile='2.11-script-unverified-on-2.5'
                Probe.dirty=true
            end)
        end)
    end)
    snapshot.reaction_observer_registered=reactionOK
    local recordsOK,records=pcall(function()
        return TweakDB:GetRecord('BaseStatusEffect.CrippledLegLeft') ~= nil
            and TweakDB:GetRecord('BaseStatusEffect.CrippledLegRight') ~= nil
    end)
    snapshot.cripple_records_available=recordsOK and records or false
    Probe.registered=ok
    snapshot.hit_observer_registered=ok
    if not ok then snapshot.last_error='Trefferbeobachtung nicht verfuegbar' end
    Probe.dirty=true
end

function Probe.update(delta)
    Probe.elapsed=Probe.elapsed+delta
    if Probe.elapsed < .5 then return end
    Probe.elapsed=0
    if Probe.enabled then
        local ok=pcall(function()
            local player=Game.GetPlayer()
            if not player then snapshot.player_loaded=false; clearTarget(); return end
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
                snapshot.target_active=true
            else
                clearTarget()
            end
        end)
        snapshot.target_api_available=ok
        if not ok then clearTarget();snapshot.last_error='NPC-Zielerfassung nicht verfuegbar' end
        Probe.dirty=true
    end
    if not Probe.dirty then return end
    local ok,written=pcall(function()
        snapshot.updated_at=os.time()
        local encoded=json.encode(snapshot)..'\n'
        if #encoded > 16384 then return false end
        local file=io.open('npc-probe.json','w')
        if not file then return false end
        local stored=file:write(encoded)
        local closed=file:close()
        return stored ~= nil and closed ~= nil
    end)
    if ok and written then Probe.dirty=false
    else snapshot.last_error='NPC-Protokoll konnte nicht gespeichert werden' end
end

function Probe.status() return snapshot end
return Probe
