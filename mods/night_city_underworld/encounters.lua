-- Automatic original-actor encounter adapter. No spawning, no follower conversion.
-- API basis: docs/MOD_SOURCE_RESEARCH.md. Every engine outcome remains unverified.
local E={actors={},queue={},clock=0,sequence=0,registered=false}
local session=tostring(os.time())..'-'..tostring({}):gsub('[^%w]','')
local status={mode='automatic',session_id=session,tracked=0,hits=0,identity_scope='session_binding',
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
local function persistQueue()
    local ok,err=pcall(function()
        local raw=json.encode({schema_version=1,queue=E.queue})..'\n'
        assert(#raw<=16384,'Outbox budget exceeded')
        local f=assert(io.open('nemesis-outbox.json','w'))
        local wrote=f:write(raw);local closed=f:close()
        assert(wrote and closed,'Outbox write failed')
    end)
    if not ok then status.log_error=text(err)end
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
    -- Original NPC is never deleted or respawned. Remove only effects we introduced.
    local actor=safe(function()return Game.FindEntityByID(row.id)end)
    if actor then
        if row.command then safe(function()actor:GetAIControllerComponent():CancelCommand(row.command)end)end
        for id in pairs(row.ownedEffects)do
            safe(function()Game.GetStatusEffectSystem():RemoveStatusEffect(row.id,TweakDBID.new(id))end)
        end
        if row.wrapperOwned then
            for _,side in ipairs({'l','r'})do
                safe(function()AnimationControllerComponent.SetAnimWrapperWeightOnOwnerAndItems(
                    actor,CName.new('woundedLocomotion_'..side..'_leg'),0)end)
            end
        end
    end
    if row.hitQueued and (reason=='unloaded' or reason=='dead') then
        E.sequence=E.sequence+1
        -- Queue lifecycle even if the hit budget is full: no silent resurrection.
        E.queue[#E.queue+1]={key=row.key,kind='body_ended',context=row.context,event={
            event_id=session..'-ended-'..E.sequence,session_id=row.bindingSession,entity_id=row.key,
            position=row.last and {x=row.last.x,y=row.last.y,z=row.last.z} or row.capturedPosition,
            dead=reason=='dead'}}
        persistQueue()
    end
    log('released',row,{reason=reason});E.actors[row.key]=nil;status.tracked=count()
end
local function wrappers(actor,row)
    -- The original actor's graph is owned by vanilla reaction AI. No verified
    -- wrapper-weight getter/restoration exists here; do not steal that owner.
    if row.plan.injured_side and not row.wrapperNote then
        row.wrapperNote=true
        log('native_gait_delegated',row,{reason='Original actor; native injury behavior owns graph',
            gait_verified=false})
    end
end
local function react(actor,row)
    local plan=row.plan
    if row.command then actor:GetAIControllerComponent():CancelCommand(row.command);row.command=nil end
    log('actor_before_reaction',row,{role=safe(function()return text(actor:GetAIControllerComponent():GetAIRole())end),
        workspot=safe(function()return Game.GetWorkspotSystem():IsActorInWorkspot(actor)end)})
    if plan.injured_side then
        local name='BaseStatusEffect.CrippledLeg'..plan.injured_side
        local effects=Game.GetStatusEffectSystem()
        if not effects:HasStatusEffect(row.id,TweakDBID.new(name)) then
            assert(TweakDB:GetRecord(name),'Injury status record unavailable')
            StatusEffectHelper.ApplyStatusEffect(actor,TweakDBID.new(name))
            row.ownedEffects[name]=true
        end
        log('injury_effect_readback',row,{effect=name,present=effects:HasStatusEffect(row.id,TweakDBID.new(name))})
    end
    if plan.posture then log('unsupported_posture',row,{posture=plan.posture})end
    if not plan.movement then
        log('reaction_blocked',row,{reason=plan.reason});return
    end
    local player=assert(Game.GetPlayer(),'No player')
    local pos,p=actor:GetWorldPosition(),player:GetWorldPosition()
    local dx,dy=pos.x-p.x,pos.y-p.y;local n=math.sqrt(dx*dx+dy*dy)
    if n<.1 then local f=player:GetWorldForward();dx,dy=f.x,f.y;n=math.sqrt(dx*dx+dy*dy)end
    assert(n>.01,'No escape direction')
    local world=WorldPosition.new()
    world:SetVector4(Vector4.new(pos.x+dx/n*12,pos.y+dy/n*12,pos.z,1))
    local dest=AIPositionSpec.new();dest:SetWorldPosition(world)
    local cmd=AIMoveToCommand.new();cmd.movementTarget=dest;cmd.movementType=moveMovementType.Run
    cmd.ignoreNavigation=false;cmd.finishWhenDestinationReached=true
    cmd.desiredDistanceFromTarget=.75;cmd.useStart=true;cmd.useStop=true
    actor:GetAIControllerComponent():SendCommand(cmd)
    row.command=cmd;row.commandAt=E.clock;row.bound=false
    row.origin={x=pos.x,y=pos.y,z=pos.z};row.last=nil
    -- Do not change shared movement policy on an original vanilla actor:
    -- MoveTo owns its requested intent; global policy restoration is not verified.
    wrappers(actor,row)
    log('reaction_requested',row,{gait=plan.gait,movement=plan.movement,
        speed_constraint=plan.speed_constraint})
end
local function readJSON(path)
    return safe(function()
        local f=io.open(path,'r');if not f then return nil end
        local raw=f:read(16385);f:close()
        if not raw or #raw>16384 or raw:sub(-1)~='\n' then return nil end
        return json.decode(raw)
    end)
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
        row.hitQueued=true;persistQueue()
        status.hits=status.hits+1
    end)
    if not ok then status.last_error=text(err);log('capture_error',nil,{error=text(err)})end
end
function E.initialize()
    if E.registered then return end
    local ok,err=pcall(function()ObserveAfter('ScriptedPuppet','OnHit',capture)end)
    E.registered=ok;status.hook_registered=ok
    if not ok then status.last_error=text(err) end
    local restored=readJSON('nemesis-outbox.json')
    if restored and restored.schema_version==1 and type(restored.queue)=='table' and #restored.queue<=16 then
        for _,item in ipairs(restored.queue)do
            if type(item)=='table' and type(item.event)=='table' and type(item.context)=='table'
                and (item.kind=='hit' or item.kind=='body_ended') then E.queue[#E.queue+1]=item end
        end
    end
    log('session_started',nil,{hook_registered=ok})
end
function E.update(delta)
    if type(delta)~='number' or delta<0 or delta~=delta then return end
    E.clock=E.clock+delta
    if not Game.GetPlayer()then E.cleanup('player_unavailable');return end
    if not E.pending and #E.queue>0 then
        local context=E.queue[1].context
        if context and context.schema_version==1 and type(context.slot)=='string'
            and type(context.timeline)=='string' and context.slot~='underworld-bridge-demo' then
            local hit=E.queue[1]
            E.pending={hit=hit,context=context}
            local f=io.open('nemesis-request.json','w')
            if f then
                local wrote=f:write(json.encode({schema_version=1,slot=context.slot,
                    timeline=context.timeline,kind=hit.kind,event=hit.event})..'\n')
                local closed=f:close()
                if not wrote or not closed then E.pending=nil end
            else E.pending=nil end
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
            table.remove(E.queue,1);E.pending=nil;persistQueue()
            if row and hit.kind=='hit' and hit.event.session_id==row.bindingSession then
                row.person=reply.result.person_id;row.plan=reply.result.plan
                local actor=safe(function()return Game.FindEntityByID(row.id)end)
                log('person_promoted',row,{zone=hit.event.zone,relationship='V_injured_me',
                    identity='persistent_person',body='session_bound_original',
                    position=hit.event.position,appearance=hit.event.appearance})
                if actor and safe(function()return actor:IsAttached()end) and not actor:IsDead() then
                    local ok,err=pcall(react,actor,row)
                    if not ok then log('reaction_error',row,{error=text(err)});status.last_error=text(err)end
                    status.last='Nemesis '..row.person..' | '..hit.event.zone..' | Wirkung unbestaetigt'
                end
            end
        end
    end
    for _,row in pairs(E.actors)do
        local actor=safe(function()return Game.FindEntityByID(row.id)end)
        if not actor or not safe(function()return actor:IsAttached()end)then release(row,'unloaded')
        elseif actor:IsDead()then log('dead',row,{});release(row,'dead')
        elseif row.command and E.clock>=(row.sampleAt or 0)then
            row.sampleAt=E.clock+.5
            local ok,err=pcall(function()
                local p=actor:GetWorldPosition()
                local active=AIbehaviorUniqueActiveCommandList.IsActionCommandById(
                    actor:GetAIControllerComponent().activeCommands,row.command.id)
                if active and not row.bound then wrappers(actor,row);row.bound=true end
                local o=row.origin
                local distance=math.sqrt((p.x-o.x)^2+(p.y-o.y)^2+(p.z-o.z)^2)
                local speed=nil
                if row.last then
                    local dt=E.clock-row.last.at
                    if dt>0 then speed=math.sqrt((p.x-row.last.x)^2+(p.y-row.last.y)^2+(p.z-row.last.z)^2)/dt end
                end
                row.last={x=p.x,y=p.y,z=p.z,at=E.clock}
                log('motion_sample',row,{active=active,distance=distance,speed=speed,
                    stalled=E.clock-row.commandAt>=3 and distance<.25})
            end)
            if not ok then log('measurement_error',row,{error=text(err)})end
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
