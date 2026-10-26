"""Opt-in bounded offscreen coordinator; no timers, workers or engine mutations."""
from bisect import bisect_right
import json
import sqlite3

from underworld.nemesis import MAX_PEOPLE, finite, token

MAX_TICK_PEOPLE = 64


class NemesisDirector:
    """Caller owns game time and routes; this object owns only scheduling fairness.

    The cursor is process-local. Restart resets ordering, but each person's durable
    clock in NemesisStore prevents double movement when a timestamp is retried.
    Missing routes are left untouched; coordinates are never generated here.
    """

    def __init__(self, store, max_people=16):
        if type(max_people) is not int or not 1 <= max_people <= MAX_TICK_PEOPLE:
            raise ValueError("invalid director tick budget")
        self.store = store
        self.max_people = max_people
        self._cursor = None

    def tick(self, timestamp, destinations):
        if not finite(timestamp) or timestamp < 0:
            raise ValueError("invalid game simulation timestamp")
        if not isinstance(destinations, dict) or len(destinations) > MAX_PEOPLE:
            raise ValueError("invalid destination budget")
        for person in destinations:
            token(person)
        # The durable store already bounds total population. Limit reads as well
        # and fail closed if an externally edited database violates that contract.
        rows = self.store.conn.execute(
            "SELECT person,state FROM nemesis_people WHERE namespace=? ORDER BY person LIMIT ?",
            (self.store.namespace, MAX_PEOPLE + 1)).fetchall()
        if len(rows) > MAX_PEOPLE:
            raise ValueError("director population budget exceeded")
        eligible = []
        for person, encoded in rows:
            if person not in destinations:
                continue
            try:
                state = json.loads(encoded)
                # Malformed state is attempted through the store below, so its
                # failure cannot prevent valid people from getting their turn.
                if not isinstance(state, dict) or state.get("mode") == "simulated":
                    eligible.append(person)
            except (ValueError, TypeError):
                eligible.append(person)
        start = 0 if self._cursor is None else bisect_right(eligible, self._cursor)
        ordered = eligible[start:] + eligible[:start]
        selected = ordered[:self.max_people]
        report = {"timestamp": timestamp, "processed": [], "errors": [],
                  "deferred": max(0, len(eligible) - len(selected))}
        for person in selected:
            # Advance the scheduler even on failure; one bad route cannot starve
            # later people. Store rechecks mode transactionally against races.
            self._cursor = person
            try:
                self.store.advance_to(person, timestamp, destinations[person])
                report["processed"].append(person)
            except (ValueError, TypeError, KeyError, sqlite3.Error) as error:
                report["errors"].append({"person_id": person, "error": str(error)[:240]})
        return report
