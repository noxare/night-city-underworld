-- Automatic original-actor encounter adapter. No spawning, no follower conversion.
-- API basis: docs/MOD_SOURCE_RESEARCH.md. Every engine outcome remains unverified.
local E={actors={},queue={},clock=0,sequence=0,registered=false}
local session=tostring(os.time())..'-'..tostring({}):gsub('[^%w]','')
local status={mode='capture_only',session_id=session,tracked=0,hits=0,identity_scope='session_binding',
    body_persistence='unsupported_existing_entity',last='Warte auf direkten Treffer durch V'}
local MAX_ACTORS,MAX_QUEUE,MAX_BYTES=8,8,1048576
local tag='underworld_injury_test'
local function text(v)return tostring(v):sub(1,160)end
local function log(kind,row,extra)
    local ok,err=pcall(function()
        E.sequence=E.sequence+1
        local data={schema_version=1,session_id=session,event_id=session..'-'..E.sequence,
            kind=kind,time=E.clock,entity_id=row and row.key or nil,
            person_key=row and row.person or nil,record_id=row and row.record or nil,
            body_persistence='unsupported_existing_entity',details=extra or {}}
        local raw=json.encode(data)..'\n'
        assert(#raw<=16384,'Trace record too large')
        local f=io.open('nemesis-trace.jsonl','a+')
        assert(f,'Trace file unavailable')
        local size=f:seek('end') or 0
        if size+#raw>MAX_BYTES then
            f:close();os.remove('nemesis-trace.previous.jsonl')
            assert(os.rename('nemesis-trace.jsonl','nemesis-trace.previous.jsonl'))
            f=assert(io.open('nemesis-trace.jsonl','w'))
        end
        local wrote=f:write(raw);local closed=f:close()
        assert(wrote and closed,'Trace write failed')
    end)
    if not ok then status.log_error=text(err) end
end
local function persistQueue(queue)
    local ok,err=pcall(function()
        local raw=json.encode({schema_version=1,queue=queue or E.queue})..'\n'
        assert(#raw<=16384,'Outbox budget exceeded')
        local f=assert(io.open('nemesis-outbox.json.tmp','w'))
        local wrote=f:write(raw);local closed=f:close()
        assert(wrote and closed,'Outbox write failed')
        local previous=io.open('nemesis-outbox.json','r')
        if previous then
            previous:close()
            os.remove('nemesis-outbox.json.previous')
            assert(os.rename('nemesis-outbox.json','nemesis-outbox.json.previous'),'Outbox backup failed')
        end
        local renamed,renameErr=os.rename('nemesis-outbox.json.tmp','nemesis-outbox.json')
        if not renamed then
            if previous then os.rename('nemesis-outbox.json.previous','nemesis-outbox.json')end
            error(renameErr or 'Outbox replace failed')
        end
    end)
    if not ok then status.log_error=text(err)end
    return ok
end
local function count()local n=0;for _ in pairs(E.actors)do n=n+1 end;return n end
local function safe(fn)local ok,v=pcall(fn);if ok then return v end;return nil end
local function zone(event)
    -- All shapes must resolve to the same exact anatomical zone; never map collider text.
    local result=nil
    local shapes=event.hitRepresentationResult.hitShapes
    if not shapes or #shapes==0 then return 'unknown' end
    local checks={{'head','IsHitReactionZoneHead'},{'torso','IsHitReactionZoneTorso'},
        {'left_arm','IsHitReactionZoneLeftArm'},{'right_arm','IsHitReactionZoneRightArm'},
        {'left_leg','IsHitReactionZoneLeftLeg'},{'right_leg','IsHitReactionZoneRightLeg'}}
    for _,shape in ipairs(shapes)do
        local data=DamageSystemHelper.GetHitShapeUserDataBase(shape)
        local found=nil
        for _,pair in ipairs(checks)do
            if HitShapeUserDataBase[pair[2]](data) then
                if found then return 'unknown' end
                found=pair[1]
            end
        end
        if not found or (result and result~=found) then return 'unknown' end
        result=found
    end
    return result or 'unknown'
end
local function release(row,reason)
    -- Original NPC is never deleted or respawned. Only a selected adapter owns cleanup.
    local actor=safe(function()return Game.FindEntityByID(row.id)end)
    if row.reactionProfile and not row.reactionReleased then
        row.reactionReleased=true
        local ok,err=pcall(row.reactionProfile.release,actor,row)
        if not ok then log('reaction_cleanup_error',row,{error=text(err)})end
    end
    if row.hitQueued and (reason=='unloaded' or reason=='dead') then
        E.sequence=E.sequence+1
        -- Queue lifecycle even if the hit budget is full: no silent resurrection.
        if #E.queue>=MAX_QUEUE+MAX_ACTORS then status.last='Lifecycle outbox full';return false end
        E.queue[#E.queue+1]={key=row.key,kind='body_ended',context=row.context,event={
            event_id=session..'-ended-'..E.sequence,session_id=row.bindingSession,entity_id=row.key,
            position=row.last and {x=row.last.x,y=row.last.y,z=row.last.z} or row.capturedPosition,
            dead=reason=='dead'}}
        if not persistQueue()then table.remove(E.queue);return false end
    end
    log('released',row,{reason=reason});E.actors[row.key]=nil;status.tracked=count()
end
-- No native Run/effect fallback: an independently verified adapter must own
-- the entire navigating injury behavior and its cleanup for an explicit record.
local function react(actor,row)
    local profile=E.reactionProfile
    if row.validatedZone=='unknown' or row.plan.gait=='unknown' or not profile or profile.records[row.record]~=true
        or ((row.plan.injured_side or row.plan.gait=='limp') and profile.injured_gait_verified~=true) then
        log('reaction_blocked',row,{reason='No verified original-actor reaction profile',gait_verified=false})
        return false
    end
    row.reactionReleased=false
    row.reactionProfile=profile -- retain cleanup ownership if apply partially fails
    profile.apply(actor,row.plan,row)
    log('reaction_requested',row,{profile=profile.id,evidence=profile.evidence})
    return true
end
function E.configureReaction(profile)
    assert(next(E.actors)==nil,'Cannot replace reaction ownership during encounters')
    if profile==nil then E.reactionProfile=nil;status.mode='capture_only';return end
    assert(type(profile)=='table' and type(profile.id)=='string' and #profile.id>0
        and type(profile.evidence)=='string' and #profile.evidence>0
        and profile.original_actor_verified==true and type(profile.records)=='table'
        and type(profile.apply)=='function' and type(profile.release)=='function',
        'Explicit verified profile, evidence, record allowlist, apply and release required')
    E.reactionProfile=profile;status.mode='verified_profile'
end
local function readJSON(path)
    return safe(function()
        local f=io.open(path,'r');if not f then return nil end
        local raw=f:read(16385);f:close()
        if not raw or #raw>16384 or raw:sub(-1)~='\n' then return nil end
        return json.decode(raw)
    end)
end
local function sameContext(a,b)
    return a and b and a.slot==b.slot and a.timeline==b.timeline and a.session_id==b.session_id
end
local function capture(actor,event)
    local ok,err=pcall(function()
        if not actor or not event or not actor:IsNPC() or not actor:IsCrowd() then return end
        local instigator=event.attackData:GetInstigator()
        if not instigator or not instigator:IsPlayer() then return end
        if AttackData.IsAreaOfEffect(event.attackData:GetAttackType())then return end
        if actor:IsDead() then return end
        -- Ignore our old manual experiment; it must not race automatic control.
        local id=actor:GetEntityID()
        if safe(function()return Game.GetDynamicEntitySystem():IsTagged(id,CName.new(tag))end)then return end
        local context=readJSON('nemesis-context.json')
        if not context or context.schema_version~=1 or type(context.slot)~='string'
            or type(context.timeline)~='string' or type(context.session_id)~='string' or context.slot=='underworld-bridge-demo' then
            status.last='Treffer beobachtet; Nemesis-Spielstandkontext fehlt'
            log('hit_without_context',nil,{entity_id=text(id.hash)})
            return
        end
        local key=text(id.hash)
        local row=E.actors[key]
        if row and not sameContext(row.context,context)then
            log('context_changed_capture_rejected',row,{});return
        end
        if not row then
            if count()>=MAX_ACTORS then log('budget_rejected',nil,{entity_id=key});return end
            row={id=id,key=key,person='candidate:'..session..':'..key,record=text(actor:GetRecordID()),
                ownedEffects={},context=context,bindingSession=context.session_id}
            E.actors[key]=row;status.tracked=count()
            log('person_candidate',row,{relationship='V_injured_me',body_persistence='unsupported_existing_entity',
                appearance=safe(function()return text(actor:GetCurrentAppearanceName())end),
                template=safe(function()return text(actor:GetTemplatePath())end)})
        end
        if #E.queue>=MAX_QUEUE then log('queue_rejected',row,{});return end
        local body=safe(function()return zone(event)end) or 'unknown'
        local p=actor:GetWorldPosition()
        row.capturedPosition={x=p.x,y=p.y,z=p.z}
        E.sequence=E.sequence+1
        E.queue[#E.queue+1]={key=key,kind='hit',context=context,event={event_id=session..'-hit-'..E.sequence,
            session_id=context.session_id,entity_id=key,zone=body,
            zone_source=body=='unknown' and 'unknown' or 'engine_hit_shapes',
            instigator='V',position={x=p.x,y=p.y,z=p.z},
            appearance={record=row.record,
                template=safe(function()return text(actor:GetTemplatePath())end) or 'unavailable',
                appearance=safe(function()return text(actor:GetCurrentAppearanceName())end) or 'unavailable',
                reconstruction_verified=false}}}
        if not persistQueue()then table.remove(E.queue);return end
        row.hitQueued=true
        status.hits=status.hits+1
    end)
    if not ok then status.last_error=text(err);log('capture_error',nil,{error=text(err)})end
end
function E.initialize()
    if E.registered then return end
    local ok,err=pcall(function()ObserveAfter('ScriptedPuppet','OnHit',capture)end)
    E.registered=ok;status.hook_registered=ok
    if not ok then status.last_error=text(err) end
    local restored=readJSON('nemesis-outbox.json') or readJSON('nemesis-outbox.json.previous')
    if restored and restored.schema_version==1 and type(restored.queue)=='table' and #restored.queue<=16 then
        for _,item in ipairs(restored.queue)do
            if type(item)=='table' and type(item.event)=='table' and type(item.context)=='table'
                and (item.kind=='hit' or item.kind=='body_ended') then E.queue[#E.queue+1]=item end
        end
    end
    log('session_started',nil,{hook_registered=ok})
end
function E.update(delta)
    if type(delta)~='number' or delta<0 or delta~=delta or delta==math.huge then return end
    E.clock=E.clock+delta
    if not Game.GetPlayer()then E.cleanup('player_unavailable');return end
    if not E.pending and #E.queue>0 then
        local context=E.queue[1].context
        if context and context.schema_version==1 and type(context.slot)=='string'
            and type(context.timeline)=='string' and context.slot~='underworld-bridge-demo' then
            local hit=E.queue[1]
            E.pending={hit=hit,context=context}
            local ok,err=pcall(function()
                local raw=json.encode({schema_version=1,slot=context.slot,
                    timeline=context.timeline,kind=hit.kind,event=hit.event})..'\n'
                assert(#raw<=16384,'Request budget exceeded')
                local f=assert(io.open('nemesis-request.json','w'),'Request unavailable')
                local wrote=f:write(raw);local closed=f:close()
                assert(wrote and closed,'Request write failed')
            end)
            if not ok then E.pending=nil;status.last_error=text(err)end
        else status.last='Treffer erfasst; expliziter Nemesis-Spielstandkontext fehlt' end
    end
    if E.pending then
        local reply=readJSON('nemesis-response.json')
        local hit,context=E.pending.hit,E.pending.context
        if reply and reply.schema_version==1 and reply.event_id==hit.event.event_id
            and reply.slot==context.slot and reply.timeline==context.timeline
            and type(reply.result)=='table' and type(reply.result.person_id)=='string'
            and (hit.kind=='body_ended' or type(reply.result.plan)=='table') then
            local row=E.actors[hit.key]
            local remaining={};for i=2,#E.queue do remaining[#remaining+1]=E.queue[i]end
            if not persistQueue(remaining)then return end
            E.queue=remaining;E.pending=nil
            if row and hit.kind=='hit' and hit.event.session_id==row.bindingSession then
                row.person=reply.result.person_id;row.plan=reply.result.plan;row.validatedZone=hit.event.zone
                local actor=safe(function()return Game.FindEntityByID(row.id)end)
                log('person_promoted',row,{zone=hit.event.zone,relationship='V_injured_me',
                    identity='persistent_person',body='session_bound_original',
                    position=hit.event.position,appearance=hit.event.appearance})
                if not sameContext(readJSON('nemesis-context.json'),context) or not sameContext(row.context,context)then
                    log('context_changed_reaction_blocked',row,{})
                elseif actor and safe(function()return actor:IsAttached()end) and not actor:IsDead() then
                    local ok,activated=pcall(react,actor,row)
                    local err=activated
                    if not ok then log('reaction_error',row,{error=text(err)});status.last_error=text(err)end
                    status.last='Nemesis '..row.person..' | '..hit.event.zone..(ok and activated and ' | Profilwirkung unbestaetigt' or ' | Nur erfasst; Reaktion gesperrt')
                end
            end
        end
    end
    local currentContext=readJSON('nemesis-context.json')
    for _,row in pairs(E.actors)do
        local actor=safe(function()return Game.FindEntityByID(row.id)end)
        if not sameContext(row.context,currentContext)then release(row,'context_changed')
        elseif not actor or not safe(function()return actor:IsAttached()end)then release(row,'unloaded')
        elseif actor:IsDead()then log('dead',row,{});release(row,'dead')
        elseif E.clock>=(row.sampleAt or 0)then
            row.sampleAt=E.clock+.5
            local ok,p=pcall(function()return actor:GetWorldPosition()end)
            if ok and p then
                row.last={x=p.x,y=p.y,z=p.z,at=E.clock}
                log('position_sample',row,{x=p.x,y=p.y,z=p.z,scope='observed_native_position'})
            else log('position_unavailable',row,{})end
        end
    end
end
function E.cleanup(reason)
    local rows={};for _,row in pairs(E.actors)do rows[#rows+1]=row end
    for _,row in ipairs(rows)do release(row,reason or 'shutdown')end
    -- Keep durable pending hits/lifecycle events for the worker/reload.
    persistQueue()
end
function E.status()return status end
return E
