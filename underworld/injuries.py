"""Deterministic injury evidence and visual intent; never controls game animations."""
from dataclasses import dataclass, field
import math

ZONES = {'head', 'torso', 'left_arm', 'right_arm', 'left_leg', 'right_leg', 'unknown'}
KINDS = {'hit', 'treated', 'incapacitated', 'killed'}


@dataclass
class InjuryState:
    session_id: str
    npc_id: str
    damage: dict = field(default_factory=dict)
    seen: dict = field(default_factory=dict)
    alive: bool = True
    incapacitated: bool = False
    unknown_hits: int = 0


def validate(event):
    required = {'schema_version','session_id','npc_id','event_id','kind','zone','zone_source','damage_fraction'}
    if not isinstance(event, dict) or set(event) != required:
        raise ValueError('invalid injury envelope')
    if type(event['schema_version']) is not int or event['schema_version'] != 1:
        raise ValueError('unsupported injury schema')
    for key in ('session_id','npc_id','event_id'):
        if not isinstance(event[key],str) or not 1 <= len(event[key]) <= 128:
            raise ValueError('invalid injury identity')
    if not isinstance(event['kind'],str) or event['kind'] not in KINDS:
        raise ValueError('unsupported injury kind')
    if not isinstance(event['zone'],str) or event['zone'] not in ZONES:
        raise ValueError('invalid body zone')
    if event['zone_source'] not in ('engine_hit_zone','unknown','test_fixture'):
        raise ValueError('invalid zone provenance')
    if event['zone'] != 'unknown' and event['zone_source'] == 'unknown':
        raise ValueError('cannot infer body zone from generic HP loss')
    value = event['damage_fraction']
    if type(value) not in (int,float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('damage must be a normalized fraction from verified adapter data')
    if event['kind'] in ('incapacitated','killed') and (value != 0 or event['zone'] != 'unknown'):
        raise ValueError('lifecycle outcomes must not invent limb damage')


def apply(state: InjuryState, event: dict) -> str:
    validate(event)
    if (event['session_id'],event['npc_id']) != (state.session_id,state.npc_id):
        raise ValueError('injury identity context mismatch')
    previous = state.seen.get(event['event_id'])
    if previous is not None:
        if previous != event: raise ValueError('conflicting injury replay')
        return 'duplicate'
    if len(state.seen) >= 512:
        raise ValueError('injury evidence budget reached')
    if not state.alive:
        raise ValueError('dead actors cannot be healed or resurrected by replay')
    kind, zone = event['kind'], event['zone']
    if kind == 'killed':
        state.alive = False
    elif kind == 'incapacitated':
        state.incapacitated = True
    elif zone == 'unknown':
        if kind == 'hit': state.unknown_hits += 1
    else:
        sign = -1 if kind == 'treated' else 1
        state.damage[zone] = min(1.0,max(0.0,state.damage.get(zone,0.0) + sign * event['damage_fraction']))
    state.seen[event['event_id']] = dict(event)
    return 'applied'


def visual_intents(state: InjuryState, verified_capabilities=()):
    """Explain requested behavior separately from verified engine support."""
    supported = set(verified_capabilities)
    if not state.alive: intents = ['dead']
    elif state.incapacitated: intents = ['incapacitated']
    else:
        intents = []
        for zone in ('left_leg','right_leg','left_arm','right_arm','torso','head'):
            if state.damage.get(zone,0) >= 0.15:
                intent = 'limp' if zone.endswith('leg') else 'guard_arm' if zone.endswith('arm') else 'guard_torso' if zone == 'torso' else 'head_pain'
                if intent not in intents: intents.append(intent)
    return [{'intent': intent, 'engine_verified': intent in supported,
             'application': 'not_applied_by_core'} for intent in intents]


def replay(session_id, npc_id, events):
    state = InjuryState(session_id,npc_id)
    for event in events: apply(state,event)
    return state
