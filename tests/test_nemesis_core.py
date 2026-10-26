import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch
from pathlib import Path
import tempfile
import unittest
from underworld.nemesis import NemesisStore, reaction


def hit(event="shot-1", session="game-session", entity="crowd-1", zone="left_leg", verified=False):
    return {"event_id": event, "session_id": session, "entity_id": entity, "zone": zone,
            "zone_source": "unknown" if zone == "unknown" else "engine_hit_shapes",
            "instigator": "V", "position": {"x": 0, "y": 0, "z": 0},
            "appearance": {"record": "crowd-record", "template": "person.ent",
                           "appearance": "specific-face-outfit", "reconstruction_verified": verified}}


class NemesisTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "nemesis.db"
        self.store = NemesisStore(self.path, "save-a", "branch-a")
        self.addCleanup(self.store.close)

    def test_promotion_is_durable_idempotent_and_records_V_memory(self):
        event = hit()
        result = self.store.hit(event)
        other = NemesisStore(self.path, "save-a", "branch-a")
        try:
            again = other.hit(event)
            self.assertEqual(again["person_id"], result["person_id"])
            self.assertTrue(again["duplicate"])
            state = other.get(result["person_id"])
            self.assertEqual(state["relationship"], "V_injured_me")
            self.assertEqual(len(state["memories"]), 1)
            self.assertEqual(state["plan"]["gait"], "limp")
            self.assertEqual(state["appearance"]["appearance"], "specific-face-outfit")
        finally:
            other.close()
        with self.assertRaises(ValueError):
            self.store.hit(hit(zone="right_leg"))

    def test_shared_record_never_merges_two_people_and_context_isolated(self):
        first = self.store.hit(hit())
        second = self.store.hit(hit("shot-2", entity="crowd-2"))
        self.assertNotEqual(first["person_id"], second["person_id"])
        other = NemesisStore(self.path, "save-b", "branch-a")
        try:
            with self.assertRaises(ValueError):
                other.get(first["person_id"])
        finally:
            other.close()

    def test_unknown_zone_does_not_invent_limb_and_two_legs_do_not_run(self):
        self.assertEqual(reaction({"unknown": 3})["gait"], "unclassified")
        self.assertIsNone(reaction({"left_leg": 1, "right_leg": 1})["movement"])
        bad = hit()
        bad["zone_source"] = "unknown"
        with self.assertRaises(ValueError):
            self.store.hit(bad)
        self.store.hit(hit())
        response = self.store.hit(hit("shot-2", zone="right_leg"))
        self.assertEqual(response["plan"]["intent"], "seek_help")

    def test_offscreen_simulation_and_materialization_preserve_person_and_look(self):
        person = self.store.hit(hit(verified=True))["person_id"]
        for visible, gone in [(True, True), (False, False), (None, True)]:
            with self.assertRaises(ValueError):
                self.store.dematerialize(person, "game-session", "crowd-1",
                                         {"x": 1, "y": 0, "z": 0}, visible=visible, original_gone=gone)
        with self.assertRaises(ValueError):
            self.store.advance(person, 1, {"x": 20, "y": 0, "z": 0})
        self.store.dematerialize(person, "game-session", "crowd-1",
                                 {"x": 1, "y": 0, "z": 0}, visible=False, original_gone=True)
        state = self.store.advance(person, 5, {"x": 20, "y": 0, "z": 0})
        self.assertAlmostEqual(state["position"]["x"], 8)
        request = self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 10,
                                          spawn_visible=False, nav_verified=True, budget_available=True)
        self.assertEqual(request["appearance"]["appearance"], "specific-face-outfit")
        with self.assertRaises(ValueError):
            self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 11,
                                     spawn_visible=False, nav_verified=True, budget_available=True)
        self.store.confirm_spawn(person, request["lease"]["id"], "game-session", "owned-1", 11)
        result = self.store.hit(hit("shot-again", entity="owned-1", verified=True))
        self.assertEqual(result["person_id"], person)
        self.assertEqual(len(self.store.get(person)["memories"]), 2)

    def test_unverified_appearance_and_dead_people_are_never_respawned(self):
        person = self.store.hit(hit())["person_id"]
        self.store.dematerialize(person, "game-session", "crowd-1",
                                 {"x": 0, "y": 0, "z": 0}, visible=False, original_gone=True)
        with self.assertRaisesRegex(ValueError, "appearance"):
            self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 1,
                                     spawn_visible=False, nav_verified=True, budget_available=True)
        self.store.mark_dead(person)
        with self.assertRaises(ValueError):
            self.store.hit(hit("later"))
        with self.assertRaises(ValueError):
            self.store.advance(person, 1, {"x": 20, "y": 0, "z": 0})

    def test_expired_spawn_needs_reconciliation_and_late_ack_rejected(self):
        person = self.store.hit(hit(verified=True))["person_id"]
        self.store.dematerialize(person, "game-session", "crowd-1",
                                 {"x": 0, "y": 0, "z": 0}, visible=False, original_gone=True)
        r = self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 0,
                                    spawn_visible=False, nav_verified=True, budget_available=True)
        with self.assertRaises(ValueError):
            self.store.confirm_spawn(person, r["lease"]["id"], "s", "new", 11)
        with self.assertRaises(ValueError):
            self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 11,
                                     spawn_visible=False, nav_verified=True, budget_available=True)

    def test_body_unload_transfers_position_and_duplicate_lifecycle_is_safe(self):
        person = self.store.hit(hit())["person_id"]
        event = {"event_id": "unload-1", "session_id": "game-session", "entity_id": "crowd-1",
                 "position": {"z": 0, "x": 7, "y": 2}, "dead": False}
        self.store.end_body(event)
        self.assertTrue(self.store.end_body(event)["duplicate"])
        self.assertEqual(self.store.get(person)["mode"], "simulated")
        self.assertEqual(self.store.get(person)["position"], {"x": 7, "y": 2, "z": 0})
        event["dead"] = True
        with self.assertRaises(ValueError):
            self.store.end_body(event)

    def test_recycled_entity_id_cannot_impersonate_retired_person(self):
        person = self.store.hit(hit())["person_id"]
        self.store.end_body({"event_id": "gone", "session_id": "game-session",
                             "entity_id": "crowd-1", "position": {"x": 0, "y": 0, "z": 0}, "dead": False})
        with self.assertRaisesRegex(ValueError, "retired"):
            self.store.hit(hit("new-stranger"))
        self.assertEqual(len(self.store.get(person)["memories"]), 1)




class NemesisHardeningTest(unittest.TestCase):
    setUp = NemesisTest.setUp
    def simulated(self):
        person = self.store.hit(hit(verified=True))["person_id"]
        self.store.dematerialize(person, "game-session", "crowd-1",
                                 {"x": 0, "y": 0, "z": 0}, visible=False, original_gone=True)
        return person

    def test_timestamp_simulation_replay_restart_and_clock_rejection(self):
        person = self.simulated()
        destination = {"x": 100000, "y": 0, "z": 0}
        self.store.advance_to(person, 100, destination)
        moved = self.store.advance_to(person, 110, destination)
        self.assertAlmostEqual(moved["position"]["x"], 14)
        other = NemesisStore(self.path, "save-a", "branch-a")
        try:
            self.assertEqual(other.advance_to(person, 110, destination), moved)
            with self.assertRaisesRegex(ValueError, "regressing"):
                other.advance_to(person, 109, destination)
            with self.assertRaisesRegex(ValueError, "relative"):
                other.advance(person, 1, destination)
            capped = other.advance_to(person, 100000, destination)
            self.assertAlmostEqual(capped["position"]["x"], 14 + 3600 * 1.4)
        finally:
            other.close()

    def test_spawn_reservation_is_atomic_across_independent_connections(self):
        person = self.simulated()
        barrier = Barrier(2)
        def reserve():
            store = NemesisStore(self.path, "save-a", "branch-a")
            try:
                barrier.wait(timeout=5)
                try:
                    return store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 1,
                                               spawn_visible=False, nav_verified=True, budget_available=True)
                except ValueError:
                    return None
            finally:
                store.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: reserve(), range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(self.store.get(person)["mode"], "spawning")

    def test_expiry_boundary_cannot_confirm_spawn(self):
        person = self.simulated()
        request = self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 0,
                                           spawn_visible=False, nav_verified=True, budget_available=True)
        with self.assertRaisesRegex(ValueError, "stale"):
            self.store.confirm_spawn(person, request["lease"]["id"], "game-session", "new", 10)
        self.assertEqual(self.store.get(person)["mode"], "spawning")

    def test_budget_failure_rolls_back_identity_and_event(self):
        with patch("underworld.nemesis.MAX_BINDINGS", 0):
            with self.assertRaisesRegex(ValueError, "budget"):
                self.store.hit(hit())
        for table in ("nemesis_people", "nemesis_events", "nemesis_bindings"):
            self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0], 0)
        self.assertFalse(self.store.hit(hit())["duplicate"])

    def test_future_schema_rejected_before_creating_other_tables(self):
        future = Path(self.tmp.name) / "future.db"
        with sqlite3.connect(future) as connection:
            connection.execute("CREATE TABLE nemesis_meta(version INTEGER NOT NULL)")
            connection.execute("INSERT INTO nemesis_meta VALUES(99)")
        with self.assertRaisesRegex(ValueError, "schema"):
            NemesisStore(future, "save-a", "branch-a")
        with sqlite3.connect(future) as connection:
            tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            self.assertEqual(tables, [("nemesis_meta",)])
            self.assertEqual(connection.execute("SELECT version FROM nemesis_meta").fetchall(), [(99,)])



    def test_spawn_ack_cannot_predate_reservation(self):
        person = self.simulated()
        request = self.store.reserve_spawn(person, {"x": 0, "y": 0, "z": 0}, 20,
                                           spawn_visible=False, nav_verified=True, budget_available=True)
        with self.assertRaisesRegex(ValueError, "stale"):
            self.store.confirm_spawn(person, request["lease"]["id"], "game-session", "new", 19)
        self.assertEqual(self.store.get(person)["mode"], "spawning")

    def test_extreme_coordinate_errors_rollback_and_finite_travel_works(self):
        person = self.simulated()
        before = self.store.get(person)
        with self.assertRaises(ValueError):
            self.store.advance(person, 1, {"x": 10 ** 1000, "y": 0, "z": 0})
        self.assertEqual(self.store.get(person), before)
        moved = self.store.advance(person, 10, {"x": 1e308, "y": 0, "z": 0})
        self.assertAlmostEqual(moved["position"]["x"], 14)
