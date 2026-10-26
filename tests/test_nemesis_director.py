import unittest
from underworld.nemesis import NemesisStore
from underworld.nemesis_director import NemesisDirector
from tests import test_nemesis_core as fixtures


class NemesisDirectorTest(unittest.TestCase):
    setUp = fixtures.NemesisTest.setUp

    def person(self, index, simulated=True):
        entity = "body-" + str(index)
        person = self.store.hit(fixtures.hit("shot-" + str(index), entity=entity, verified=True))["person_id"]
        if simulated:
            self.store.dematerialize(person, "game-session", entity, {"x": 0, "y": 0, "z": 0},
                                     visible=False, original_gone=True)
        return person

    def routes(self, people):
        return {person: {"x": 1000, "y": 0, "z": 0} for person in people}

    def test_budget_round_robin_and_deterministic_sorted_order(self):
        people = [self.person(i) for i in range(5)]
        routes = self.routes(people)
        director = NemesisDirector(self.store, max_people=2)
        results = [director.tick(10, routes) for _ in range(3)]
        expected = sorted(people)
        self.assertEqual(results[0]["processed"], expected[:2])
        self.assertEqual(results[1]["processed"], expected[2:4])
        self.assertEqual(results[2]["processed"], [expected[4], expected[0]])
        self.assertTrue(all(len(r["processed"]) <= 2 and r["deferred"] == 3 for r in results))
        self.assertTrue(all(self.store.get(p)["last_simulation_tick"] == 10 for p in people))

    def test_restart_retry_and_regression_use_durable_clock(self):
        person = self.person(1)
        routes = self.routes([person])
        director = NemesisDirector(self.store)
        director.tick(100, routes)
        director.tick(110, routes)
        before = self.store.get(person)
        self.assertEqual(before["position"]["x"], 14)
        other = NemesisStore(self.path, "save-a", "branch-a")
        try:
            restarted = NemesisDirector(other)
            self.assertEqual(restarted.tick(110, routes)["processed"], [person])
            self.assertEqual(other.get(person), before)
            rejected = restarted.tick(109, routes)
            self.assertEqual(len(rejected["errors"]), 1)
            self.assertEqual(other.get(person), before)
        finally:
            other.close()

    def test_only_simulated_namespace_people_with_supplied_routes(self):
        original = self.person(1, False)
        dead = self.person(2)
        self.store.mark_dead(dead)
        spawning = self.person(3)
        self.store.reserve_spawn(spawning, {"x": 0, "y": 0, "z": 0}, 0,
                                           spawn_visible=False, nav_verified=True, budget_available=True)
        materialized = self.person(4)
        lease = self.store.reserve_spawn(materialized, {"x": 0, "y": 0, "z": 0}, 0,
                                         spawn_visible=False, nav_verified=True, budget_available=True)
        self.store.confirm_spawn(materialized, lease["lease"]["id"], "game-session", "new-body", 1)
        omitted = self.person(5)
        active = self.person(6)
        people = [original, dead, spawning, materialized, omitted, active]
        before = {p: self.store.get(p) for p in people}
        routes = self.routes([original, dead, spawning, materialized, active, "unknown-person"])
        director = NemesisDirector(self.store)
        self.assertEqual(director.tick(1, routes)["processed"], [active])
        director.tick(11, routes)
        for p in people[:-1]:
            self.assertEqual(self.store.get(p), before[p])
        other = NemesisStore(self.path, "other-save", "branch-a")
        try:
            self.assertEqual(NemesisDirector(other).tick(20, routes)["processed"], [])
        finally:
            other.close()

    def test_bad_route_does_not_stall_other_people_or_fairness(self):
        people = sorted(self.person(i) for i in range(3))
        routes = self.routes(people)
        routes[people[0]] = {"x": float("nan"), "y": 0, "z": 0}
        director = NemesisDirector(self.store, 1)
        failed = director.tick(10, routes)
        self.assertEqual(failed["errors"][0]["person_id"], people[0])
        self.assertEqual(director.tick(10, routes)["processed"], [people[1]])
        self.assertEqual(director.tick(10, routes)["processed"], [people[2]])
        self.assertIsNone(self.store.get(people[0])["last_simulation_tick"])

    def test_invalid_clock_and_budgets_do_not_mutate(self):
        person = self.person(1)
        before = self.store.get(person)
        for maximum in (0, 65, True, 1.0):
            with self.assertRaises(ValueError):
                NemesisDirector(self.store, maximum)
        director = NemesisDirector(self.store)
        for clock in (-1, True, float("nan"), 10 ** 1000):
            with self.assertRaises(ValueError):
                director.tick(clock, self.routes([person]))
        for routes in (None, [], {"": {}}, {str(i): {} for i in range(513)}):
            with self.assertRaises(ValueError):
                director.tick(10, routes)
        self.assertEqual(self.store.get(person), before)

    def test_mode_change_between_selection_and_advance_is_rechecked(self):
        from unittest.mock import patch
        person = self.person(1)
        advance = self.store.advance_to
        def become_visible(*args):
            self.store.mark_dead(person)
            return advance(*args)
        with patch.object(self.store, "advance_to", side_effect=become_visible):
            report = NemesisDirector(self.store).tick(1, self.routes([person]))
        self.assertEqual(report["processed"], [])
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(self.store.get(person)["position"], {"x": 0, "y": 0, "z": 0})

    def test_corrupt_person_does_not_block_other_records(self):
        broken, healthy = sorted(self.person(i) for i in range(2))
        self.store.conn.execute("UPDATE nemesis_people SET state=? WHERE namespace=? AND person=?",
                                ("invalid-json", self.store.namespace, broken))
        self.store.conn.commit()
        report = NemesisDirector(self.store).tick(10, self.routes([broken, healthy]))
        self.assertEqual(report["processed"], [healthy])
        self.assertEqual(report["errors"][0]["person_id"], broken)
