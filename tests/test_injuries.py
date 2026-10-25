import json
import unittest
from underworld.injuries import InjuryState, apply, replay, visual_intents


def event(id='one', **changes):
    value={'schema_version':1,'session_id':'session','npc_id':'actor','event_id':id,
           'kind':'hit','zone':'left_leg','zone_source':'test_fixture','damage_fraction':0.2}
    value.update(changes)
    return value


class InjuryTest(unittest.TestCase):
    def test_limp_intent_duplicate_and_treatment(self):
        state=InjuryState('session','actor')
        self.assertEqual(apply(state,event()),'applied')
        self.assertEqual(apply(state,event()),'duplicate')
        self.assertEqual(visual_intents(state),[{'intent':'limp','engine_verified':False,'application':'not_applied_by_core'}])
        apply(state,event('treatment',kind='treated',damage_fraction=.2))
        self.assertEqual(visual_intents(state),[])

    def test_generic_damage_does_not_invent_limb_injury(self):
        state=InjuryState('session','actor')
        apply(state,event(zone='unknown',zone_source='unknown'))
        self.assertEqual(state.unknown_hits,1)
        self.assertEqual(visual_intents(state),[])
        with self.assertRaises(ValueError):apply(state,event('wrong',zone_source='unknown'))

    def test_reload_reproduces_injury_and_actor_context_isolated(self):
        records=json.loads(json.dumps([event(),event('arm',zone='right_arm')]))
        state=replay('session','actor',records)
        self.assertEqual([x['intent'] for x in visual_intents(state)],['limp','guard_arm'])
        with self.assertRaises(ValueError):apply(state,event('other',session_id='different'))
        with self.assertRaises(ValueError):apply(state,event(damage_fraction=.5))

    def test_death_is_explicit_and_cannot_be_healed(self):
        state=InjuryState('session','actor')
        apply(state,event(damage_fraction=1))
        self.assertTrue(state.alive)
        apply(state,event('death',kind='killed',zone='unknown',zone_source='unknown',damage_fraction=0))
        self.assertEqual(visual_intents(state)[0]['intent'],'dead')
        with self.assertRaises(ValueError):apply(state,event('heal',kind='treated'))
        self.assertEqual(apply(state,event('death',kind='killed',zone='unknown',zone_source='unknown',damage_fraction=0)),'duplicate')

    def test_nonfinite_boolean_and_unsupported_versions_rejected(self):
        for changes in ({'damage_fraction':float('nan')},{'damage_fraction':True},{'schema_version':True},{'zone':'foot'}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                apply(InjuryState('session','actor'),event(**changes))
