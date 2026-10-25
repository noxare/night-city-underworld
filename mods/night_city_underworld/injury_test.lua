-- Controlled native-status experiment. Only our tagged, nonpersistent crowd clone is mutable.
local Test={message='Bereit: generischen Crowd-NPC ansehen',age=0,id=nil}
local walk
local tag=CName.new('underworld_injury_test')
local function system() return Game.GetDynamicEntitySystem() end
local function owned()
    if not Test.id then return nil end
    local s=system()
    if not s:IsTagged(Test.id,tag) then error('Test-NPC Eigentum nicht bestaetigt') end
    return s:GetEntity(Test.id)
end
function Test.cleanup()
    local s=system()
    -- The tag is reserved exclusively for this module.
    s:DeleteTagged(tag)
    Test.id=nil;Test.age=0;Test.walkStarted=false;Test.command=nil;Test.origin=nil;Test.distance=0
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
    Test.id=s:CreateEntity(spec);Test.age=0;Test.walkStarted=false;Test.distance=0;Test.origin=nil
    Test.message='Test-NPC angefordert; Spawn erfolgt asynchron. Automatische Entfernung nach 60 s.'
end
walk=function()
    local actor=owned()
    if not actor then error('Test-NPC noch nicht gespawnt') end
    local controller=actor:GetAIControllerComponent()
    if Test.command then controller:CancelCommand(Test.command);Test.command=nil end
    local position=actor:GetWorldPosition()
    local forward=Game.GetPlayer():GetWorldForward()
    local world=WorldPosition.new()
    world:SetVector4(Vector4.new(position.x+forward.x*6,position.y+forward.y*6,position.z,1))
    local target=AIPositionSpec.new();target:SetWorldPosition(world)
    local command=AIMoveToCommand.new()
    command.movementTarget=target
    command.movementType=moveMovementType.Walk
    command.desiredDistanceFromTarget=.5
    command.finishWhenDestinationReached=true
    command.ignoreNavigation=false
    command.useStart=true;command.useStop=true
    controller:SendCommand(command)
    Test.command=command
    Test.origin={x=position.x,y=position.y,z=position.z}
    Test.distance=0;Test.walkStarted=true
    Test.message='Gehbefehl gesendet (6 m, Navigation aktiv); tatsaechliche Bewegung wird gemessen'
end
local function effect(side,remove)
    local actor=owned()
    if not actor then error('Test-NPC noch nicht gespawnt') end
    local id=TweakDBID.new('BaseStatusEffect.CrippledLeg'..side)
    if not TweakDB:GetRecord(id) then error('Nativer Statuseffekt fehlt') end
    local effects=Game.GetStatusEffectSystem()
    if remove then effects:RemoveStatusEffect(Test.id,id)
    else StatusEffectHelper.ApplyStatusEffect(actor,id) end
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
        if ok and actor then Test.walkStarted=true;run(walk) end
    end
    if Test.origin then
        pcall(function()
            local actor=owned()
            if actor then local p=actor:GetWorldPosition();local o=Test.origin
                Test.distance=math.sqrt((p.x-o.x)^2+(p.y-o.y)^2+(p.z-o.z)^2)
            end
        end)
    end
end
function Test.draw(overlay)
    ImGui.Separator()
    ImGui.Text('Nativer Verletzungstest · nur eigener Crowd-Klon')
    ImGui.Text('Nur auf freier, ebener Flaeche starten. Kein Kampf wird ausgeloest.')
    ImGui.Text(Test.message)
    if Test.origin then ImGui.Text(string.format('Gemessene Wegstrecke: %.2f m',Test.distance or 0)) end
    if not overlay then return end
    if ImGui.Button('Eigenen Test-NPC erzeugen') then run(spawn) end
    if Test.id then
        if ImGui.Button('Test-NPC gehen lassen (6 m)') then run(walk) end
        if ImGui.Button('Linkes Bein: nativen Effekt anwenden') then run(function()effect('Left',false)end) end
        if ImGui.Button('Rechtes Bein: nativen Effekt anwenden') then run(function()effect('Right',false)end) end
        if ImGui.Button('Beineffekte entfernen') then run(function()effect('Left',true);effect('Right',true)end) end
    end
    if ImGui.Button('Test-NPC entfernen / aufraeumen') then run(Test.cleanup) end
end
return Test
