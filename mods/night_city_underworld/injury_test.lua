-- Controlled native-status experiment. Only our tagged, nonpersistent crowd clone is mutable.
local Test={message='Bereit: generischen Crowd-NPC ansehen',age=0,id=nil}
local walk
local move
local restoreLegEffects
local applyInjuryWrappers
local tag=CName.new('underworld_injury_test')
local function system() return Game.GetDynamicEntitySystem() end
local function owned()
    if not Test.id then return nil end
    local s=system()
    if not s:IsTagged(Test.id,tag) then error('Test-NPC Eigentum nicht bestaetigt') end
    local actor=s:GetEntity(Test.id)
    if actor and not actor:IsAttached() then return nil end
    return actor
end
function Test.cleanup()
    local s=system()
    -- Reset only the owned clone, then delete even if a wrapper reset fails.
    pcall(function()
        local actor=owned()
        if actor then Test.legEffects={};applyInjuryWrappers(actor) end
    end)
    -- The tag is reserved exclusively for this module.
    s:DeleteTagged(tag)
    Test.id=nil;Test.age=0;Test.walkStarted=false;Test.command=nil;Test.origin=nil;Test.distance=0;Test.legEffects={};Test.intent='walk'
    Test.wrapperState=nil;Test.speed=nil;Test.lastPosition=nil;Test.commandAge=nil;Test.motionState=nil;Test.commandState=nil;Test.policyState=nil;Test.lastInjuredSide=nil
    Test.message='Test-NPC entfernt'
end
local function spawn()
    local s=system()
    if not s:IsReady() then error('Codeware DynamicEntitySystem nicht bereit') end
    if Test.id or s:IsPopulated(tag) then error('Erst vorhandenen Test-NPC entfernen') end
    local player=Game.GetPlayer()
    if not player then error('Kein Spielstand geladen') end
    local target=Game.GetTargetingSystem():GetLookAtObject(player,false,false)
    if not target or not target:IsNPC() or not target:IsCrowd() then
        error('Bitte einen generischen Crowd-NPC ansehen; keine Questfigur')
    end
    local record=target:GetRecordID()
    Test.record=tostring(record)
    if not TweakDB:GetRecord(record) then error('NPC-Datensatz nicht verfuegbar') end
    local p=player:GetWorldPosition()
    local forward=player:GetWorldForward()
    local spec=DynamicEntitySpec.new()
    spec.recordID=record
    spec.position=Vector4.new(p.x+forward.x*4,p.y+forward.y*4,p.z,1)
    spec.orientation=player:GetWorldOrientation()
    spec.persistState=false;spec.persistSpawn=false
    spec.alwaysSpawned=false;spec.spawnInView=true;spec.active=true
    spec.tags={tag}
    Test.id=s:CreateEntity(spec);Test.age=0;Test.walkStarted=false;Test.distance=0;Test.origin=nil;Test.legEffects={};Test.intent='walk'
    Test.wrapperState=nil;Test.speed=nil;Test.lastInjuredSide=nil;Test.commandAge=nil;Test.motionState=nil
    Test.message='Test-NPC angefordert; Spawn erfolgt asynchron. Automatische Entfernung nach 60 s.'
end
applyInjuryWrappers=function(actor)
    local left=Test.legEffects and Test.legEffects.Left
    local right=Test.legEffects and Test.legEffects.Right
    -- Only one locomotion wrapper at a time; latest selected leg has priority.
    if left and right then left=Test.lastInjuredSide~='Right';right=not left end
    Test.wrapperState='Native Wrapper-Anbindung wird versucht'
    -- Names verified in installed wounded_entry_se.behavior; method follows native task.
    AnimationControllerComponent.SetAnimWrapperWeightOnOwnerAndItems(actor,CName.new('woundedLocomotion_l_leg'),left and 1.0 or 0.0)
    AnimationControllerComponent.SetAnimWrapperWeightOnOwnerAndItems(actor,CName.new('woundedLocomotion_r_leg'),right and 1.0 or 0.0)
    Test.wrapperState=(left or right) and 'Verletzte Bein-Wrapper angefordert; sichtbares Ergebnis noch zu pruefen' or 'Bein-Wrapper auf 0 zurueckgesetzt'
end
restoreLegEffects=function(actor)
    for side,active in pairs(Test.legEffects or {}) do
        if active then StatusEffectHelper.ApplyStatusEffect(actor,TweakDBID.new('BaseStatusEffect.CrippledLeg'..side)) end
    end
    applyInjuryWrappers(actor)
end
move=function(intent)
    local actor=owned()
    if not actor then error('Test-NPC noch nicht gespawnt') end
    local controller=actor:GetAIControllerComponent()
    if Test.command then controller:CancelCommand(Test.command);Test.command=nil end
    local position=actor:GetWorldPosition()
    local player=Game.GetPlayer()
    local forward=player:GetWorldForward()
    local dx,dy=forward.x,forward.y
    if intent=='flee' then
        local p=player:GetWorldPosition()
        local x,y=position.x-p.x,position.y-p.y
        local length=math.sqrt(x*x+y*y)
        if length>.1 then dx=x/length;dy=y/length end
    end
    local length=intent=='flee' and 10 or 6
    local world=WorldPosition.new()
    world:SetVector4(Vector4.new(position.x+dx*length,position.y+dy*length,position.z,1))
    local target=AIPositionSpec.new();target:SetWorldPosition(world)
    local command=AIMoveToCommand.new()
    command.movementTarget=target
    local injured=Test.legEffects and (Test.legEffects.Left or Test.legEffects.Right)
    command.movementType=intent=='flee' and moveMovementType.Run or moveMovementType.Walk
    command.desiredDistanceFromTarget=.5
    command.finishWhenDestinationReached=true
    command.ignoreNavigation=false
    command.useStart=true;command.useStop=true
    controller:SendCommand(command)
    Test.command=command
    -- A command intent alone may leave the existing crowd movement policy unchanged.
    -- Source: AIControl.MakeFollower; only our disposable clone is modified.
    local policyOk,policyErr=pcall(function()
        actor:GetMovePolicesComponent():ChangeMovementType(command.movementType)
    end)
    Test.policyState=policyOk and 'Bewegungspolicy aktualisiert' or 'Policyfehler: '..tostring(policyErr)
    Test.intent=intent
    Test.wrapperBoundToCommand=false;Test.commandAge=0;Test.motionState='Ausfuehrung noch nicht bestaetigt';Test.diagnosticAfter=0
    Test.origin={x=position.x,y=position.y,z=position.z}
    Test.distance=0;Test.walkStarted=true;Test.lastPosition=nil;Test.speed=0
    -- Keep movement measurement alive even when the animation adapter fails.
    local ok,err=pcall(restoreLegEffects,actor)
    if not ok then Test.wrapperState='Wrapper-/Statuseffektfehler: '..tostring(err) end
    Test.message=intent=='flee' and (injured and 'Flucht-Laufbefehl + nativer Bein-Wrapper angefordert; Wirkung noch pruefen' or 'Unverletzte Flucht: Laufbefehl gesendet') or 'Gehbefehl gesendet; Bewegung wird gemessen'
end
walk=function()move('walk')end
local function effect(side,remove)
    local actor=owned()
    if not actor then error('Test-NPC noch nicht gespawnt') end
    local id=TweakDBID.new('BaseStatusEffect.CrippledLeg'..side)
    if not TweakDB:GetRecord(id) then error('Nativer Statuseffekt fehlt') end
    local effects=Game.GetStatusEffectSystem()
    if remove then effects:RemoveStatusEffect(Test.id,id)
    elseif not Test.command then StatusEffectHelper.ApplyStatusEffect(actor,id) end
    Test.legEffects=Test.legEffects or {}
    Test.legEffects[side]=not remove
    if not remove then Test.lastInjuredSide=side end
    -- Replace our active movement command after every injury-state transition.
    if Test.command then move(Test.intent or 'walk') else applyInjuryWrappers(actor) end
    Test.message=remove and 'Entfernung angefordert; Gangbild beobachten' or 'Nativer Beinstatuseffekt angefordert; Animation ist noch zu pruefen'
end
local function run(fn)
    local ok,err=pcall(fn)
    if not ok then Test.message=tostring(err) end
    print('[Underworld InjuryTest] '..Test.message)
end
function Test.update(delta)
    if not Test.id then return end
    Test.age=Test.age+delta
    if Test.age>=60 or not Game.GetPlayer() then run(Test.cleanup);return end
    if not Test.walkStarted and Test.age>1 then
        local ok,actor=pcall(owned)
        if ok and actor then run(walk) end
    end
    if Test.commandAge then Test.commandAge=Test.commandAge+delta end
    if Test.origin then
        local ok,err=pcall(function()
            local actor=owned()
            if actor then local p=actor:GetWorldPosition();local o=Test.origin
                local last=Test.lastPosition
                if last and delta>0 then
                    Test.speed=math.sqrt((p.x-last.x)^2+(p.y-last.y)^2+(p.z-last.z)^2)/delta
                end
                Test.lastPosition={x=p.x,y=p.y,z=p.z}
                Test.distance=math.sqrt((p.x-o.x)^2+(p.y-o.y)^2+(p.z-o.z)^2)
                if Test.commandAge>=Test.diagnosticAfter then
                    Test.diagnosticAfter=Test.commandAge+1
                    local activeOk,active=pcall(function()
                        return AIbehaviorUniqueActiveCommandList.IsActionCommandById(actor:GetAIControllerComponent().activeCommands,Test.command.id)
                    end)
                    -- Bind after AI activation as well as at request time: activation may
                    -- change the graph. One bounded bind per command, never per frame.
                    if activeOk and active and not Test.wrapperBoundToCommand then
                        Test.wrapperBoundToCommand=true
                        local bound,bindErr=pcall(applyInjuryWrappers,actor)
                        if not bound then Test.wrapperState='Wrapperfehler: '..tostring(bindErr) end
                    end
                    Test.commandState=activeOk and (active and 'aktiv' or 'nicht aktiv') or 'Abfrage nicht verfuegbar'
                    local state=Test.distance>.25 and 'Bewegung gemessen; Gangart separat beurteilen'
                        or (Test.commandAge>=3 and 'Keine Bewegung bestaetigt: KI/Navigation pruefen' or 'Warte auf Bewegung')
                    if state~=Test.motionState then
                        Test.motionState=state
                        print('[Underworld InjuryTest] record='..tostring(Test.record)..' intent='..tostring(Test.intent)..' command='..Test.commandState..' '..state)
                    end
                end
            end
        end)
        if not ok then Test.motionState='Messfehler: '..tostring(err) end
    end
end
function Test.draw(overlay)
    ImGui.Separator()
    ImGui.Text('Nativer Verletzungstest · nur eigener Crowd-Klon')
    ImGui.Text('Nur auf freier, ebener Flaeche starten. Kein Kampf wird ausgeloest.')
    ImGui.Text(Test.message)
    if Test.record then ImGui.Text('NPC-Vorlage: '..Test.record) end
    if Test.policyState then ImGui.Text(Test.policyState) end
    if Test.commandState then ImGui.Text('Bewegungsbefehl: '..Test.commandState) end
    if Test.motionState then ImGui.Text(Test.motionState) end
    if Test.wrapperState then ImGui.Text(Test.wrapperState) end
    if Test.speed then ImGui.Text(string.format('Gemessene Geschwindigkeit: %.2f m/s',Test.speed)) end
    if Test.origin then ImGui.Text(string.format('Gemessene Wegstrecke: %.2f m',Test.distance or 0)) end
    if not overlay then return end
    if ImGui.Button('Eigenen Test-NPC erzeugen') then run(spawn) end
    if Test.id then
        if ImGui.Button('Flucht vom Spieler testen') then run(function()move('flee')end) end
        ImGui.Text('Flucht fordert Run an; nativer Verletzungs-Wrapper bleibt aktiv. Animation und Tempo noch pruefen.')
        if ImGui.Button('Test-NPC gehen lassen (6 m)') then run(walk) end
        if ImGui.Button('Linkes Bein: nativen Effekt anwenden') then run(function()effect('Left',false)end) end
        if ImGui.Button('Rechtes Bein: nativen Effekt anwenden') then run(function()effect('Right',false)end) end
        if ImGui.Button('Beineffekte entfernen') then run(function()effect('Left',true);effect('Right',true)end) end
    end
    if ImGui.Button('Test-NPC entfernen / aufraeumen') then run(Test.cleanup) end
end
return Test
