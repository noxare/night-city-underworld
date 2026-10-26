"""Persistent Nemesis people and bounded visible/offscreen lifecycle. No engine API."""
import json
import math
import sqlite3
import uuid

ZONES = {"head", "torso", "left_arm", "right_arm", "left_leg", "right_leg", "unknown"}


def token(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 160:
        raise ValueError("invalid identifier")
    return value


def point(value):
    if not isinstance(value, dict) or set(value) != {"x", "y", "z"}:
        raise ValueError("invalid position")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in value.values()):
        raise ValueError("nonfinite position")
    return dict(value)


def appearance(value):
    if not isinstance(value, dict) or set(value) != {"record", "template", "appearance", "reconstruction_verified"}:
        raise ValueError("invalid visual identity")
    for key in ("record", "template", "appearance"):
        token(value[key])
    if type(value["reconstruction_verified"]) is not bool:
        raise ValueError("invalid visual capability")
    return dict(value)


def reaction(hits):
    left, right = hits.get("left_leg", 0) > 0, hits.get("right_leg", 0) > 0
    plan = {"intent": "escape", "movement": "Run", "gait": "unclassified",
            "speed_constraint": "native_effect_unverified", "status": "requested_not_verified"}
    if left and right:
        plan.update(intent="seek_help", movement=None, gait="both_legs_injured",
                    reason="No verified mobile two-leg gait; do not substitute healthy Run")
    elif left or right:
        plan.update(gait="limp", injured_side="Left" if left else "Right")
    elif hits.get("left_arm", 0) + hits.get("right_arm", 0):
        plan["posture"] = "guard_arm"
    elif hits.get("torso", 0):
        plan["posture"] = "guard_torso"
    elif hits.get("head", 0):
        plan["posture"] = "head_pain"
    return plan


class NemesisStore:
    """Caller supplies a verified save slot/timeline; demo context is not inferred."""

    def __init__(self, path, slot, timeline):
        self.namespace = json.dumps([token(slot), token(timeline)], separators=(",", ":"))
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS nemesis_meta(version INTEGER NOT NULL);
        INSERT INTO nemesis_meta SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM nemesis_meta);
        CREATE TABLE IF NOT EXISTS nemesis_people(
            namespace TEXT, person TEXT, state TEXT NOT NULL,
            PRIMARY KEY(namespace,person));
        CREATE TABLE IF NOT EXISTS nemesis_bindings(
            namespace TEXT, session TEXT, entity TEXT, person TEXT NOT NULL,
            PRIMARY KEY(namespace,session,entity));
        CREATE TABLE IF NOT EXISTS nemesis_events(
            namespace TEXT, event TEXT, payload TEXT NOT NULL, response TEXT NOT NULL,
            PRIMARY KEY(namespace,event));
        """)
        if self.conn.execute("SELECT version FROM nemesis_meta").fetchone()[0] != 1:
            self.conn.close()
            raise ValueError("unsupported Nemesis schema")

    def close(self):
        self.conn.close()

    def get(self, person):
        row = self.conn.execute("SELECT state FROM nemesis_people WHERE namespace=? AND person=?",
                                (self.namespace, token(person))).fetchone()
        if not row:
            raise ValueError("unknown person")
        return json.loads(row[0])

    def _save(self, state):
        self.conn.execute("INSERT OR REPLACE INTO nemesis_people VALUES(?,?,?)",
                          (self.namespace, state["person_id"], json.dumps(state, sort_keys=True)))

    def hit(self, event):
        required = {"event_id", "session_id", "entity_id", "zone", "zone_source",
                    "appearance", "position", "instigator"}
        if not isinstance(event, dict) or set(event) != required:
            raise ValueError("invalid hit")
        for key in ("event_id", "session_id", "entity_id"):
            token(event[key])
        if event["instigator"] != "V" or event["zone"] not in ZONES:
            raise ValueError("unsupported instigator/zone")
        if event["zone_source"] != ("unknown" if event["zone"] == "unknown" else "engine_hit_shapes"):
            raise ValueError("unproven body zone")
        visual, pos = appearance(event["appearance"]), point(event["position"])
        payload = json.dumps(event, sort_keys=True)
        with self.conn:
            old = self.conn.execute("SELECT payload,response FROM nemesis_events WHERE namespace=? AND event=?",
                                    (self.namespace, event["event_id"])).fetchone()
            if old:
                if old[0] != payload:
                    raise ValueError("conflicting replay")
                return {**json.loads(old[1]), "duplicate": True}
            binding = self.conn.execute(
                "SELECT person FROM nemesis_bindings WHERE namespace=? AND session=? AND entity=?",
                (self.namespace, event["session_id"], event["entity_id"])).fetchone()
            if binding:
                state = self.get(binding[0])
                if state["mode"] == "dead":
                    raise ValueError("dead person cannot receive new live hits")
                if state["binding"] != {"session_id": event["session_id"], "entity_id": event["entity_id"]}:
                    raise ValueError("retired body binding requires explicit rematerialization")
                if state["appearance"] != visual:
                    raise ValueError("entity identity changed; cannot merge different appearances")
            else:
                person = "uw-" + uuid.uuid4().hex
                state = {"person_id": person, "appearance": visual, "position": pos,
                         "hits": {}, "mode": "original", "relationship": "V_injured_me",
                         "memories": [], "binding": {"session_id": event["session_id"],
                                                    "entity_id": event["entity_id"]},
                         "intent": "escape", "lease": None}
                self.conn.execute("INSERT INTO nemesis_bindings VALUES(?,?,?,?)",
                                  (self.namespace, event["session_id"], event["entity_id"], person))
            if len(state["memories"]) >= 512:
                raise ValueError("person memory budget reached")
            zone = event["zone"]
            state["hits"][zone] = state["hits"].get(zone, 0) + 1
            state["position"] = pos
            state["memories"].append({"event_id": event["event_id"], "kind": "V_injured_me", "zone": zone})
            state["plan"] = reaction(state["hits"])
            state["intent"] = state["plan"]["intent"]
            self._save(state)
            response = {"person_id": state["person_id"], "plan": state["plan"], "duplicate": False,
                        "identity": "persistent_person", "body": "session_bound_original"}
            self.conn.execute("INSERT INTO nemesis_events VALUES(?,?,?,?)",
                              (self.namespace, event["event_id"], payload, json.dumps(response, sort_keys=True)))
            return response

    def dematerialize(self, person, session, entity, position, *, visible, original_gone=False):
        """No original deletion: require offscreen AND confirmation original is gone."""
        if visible is not False or original_gone is not True:
            raise ValueError("cannot abstract a visible or still existing original")
        pos = point(position)
        with self.conn:
            state = self.get(person)
            if state["mode"] not in ("original", "materialized"):
                raise ValueError("person has no live body")
            if state["binding"] != {"session_id": session, "entity_id": entity}:
                raise ValueError("stale actor binding")
            state.update(mode="simulated", position=pos, binding=None, lease=None)
            self._save(state)

    def advance(self, person, seconds, destination):
        """Abstract world movement, not navmesh proof; caller supplies simulation time."""
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 <= seconds <= 3600:
            raise ValueError("invalid simulation step")
        dest = point(destination)
        with self.conn:
            state = self.get(person)
            if state["mode"] != "simulated":
                raise ValueError("never simulate motion while an engine body owns position")
            # Model speeds, intentionally distinct from unverified physical engine speeds.
            gait = state["plan"]["gait"]
            speed = 0 if gait == "both_legs_injured" else 1.4 if gait == "limp" else 3.5
            pos = state["position"]
            distance = math.sqrt(sum((dest[k] - pos[k]) ** 2 for k in pos))
            ratio = min(1, speed * seconds / distance) if distance else 0
            state["position"] = {k: pos[k] + (dest[k] - pos[k]) * ratio for k in pos}
            self._save(state)
            return state

    def reserve_spawn(self, person, player_position, now, *, spawn_visible, nav_verified, budget_available):
        """One pending lease per person; preload within 100m outside known view."""
        player = point(player_position)
        if type(now) not in (int, float) or not math.isfinite(now) or now < 0:
            raise ValueError("invalid simulation clock")
        with self.conn:
            state = self.get(person)
            if state["mode"] == "spawning" and state["lease"]["expires"] <= now:
                # Unknown late spawns must be reconciled before another lease.
                raise ValueError("expired spawn requires adapter reconciliation")
            if state["mode"] != "simulated":
                raise ValueError("body already present or pending")
            if spawn_visible is not False or nav_verified is not True or budget_available is not True:
                raise ValueError("spawn placement not proven safe")
            if not state["appearance"]["reconstruction_verified"]:
                raise ValueError("same appearance reconstruction is not verified")
            if math.sqrt(sum((player[k] - state["position"][k]) ** 2 for k in ("x", "y", "z"))) > 100:
                raise ValueError("outside preload radius")
            lease = {"id": uuid.uuid4().hex, "expires": now + 10}
            state.update(mode="spawning", lease=lease)
            self._save(state)
            return {"person_id": person, "lease": lease, "appearance": state["appearance"],
                    "position": state["position"], "injuries": state["hits"], "plan": state["plan"]}

    def confirm_spawn(self, person, lease_id, session, entity, now):
        token(session); token(entity)
        if type(now) not in (int, float) or not math.isfinite(now) or now < 0:
            raise ValueError('invalid acknowledgement clock')
        with self.conn:
            state = self.get(person)
            if state["mode"] != "spawning" or state["lease"]["id"] != lease_id or now > state["lease"]["expires"]:
                raise ValueError("stale spawn acknowledgement")
            old = self.conn.execute("SELECT person FROM nemesis_bindings WHERE namespace=? AND session=? AND entity=?",
                                    (self.namespace, session, entity)).fetchone()
            if old and old[0] != person:
                raise ValueError("entity already bound to another person")
            self.conn.execute("INSERT OR REPLACE INTO nemesis_bindings VALUES(?,?,?,?)",
                              (self.namespace, session, entity, person))
            state.update(mode="materialized", lease=None, binding={"session_id": session, "entity_id": entity})
            self._save(state)

    def spawn_failed(self, person, lease_id, *, body_absent):
        if body_absent is not True:
            raise ValueError("must prove no pending or spawned body exists")
        with self.conn:
            state = self.get(person)
            if state["mode"] != "spawning" or state["lease"]["id"] != lease_id:
                raise ValueError("stale spawn failure")
            state.update(mode="simulated", lease=None)
            self._save(state)

    def end_body(self, event):
        required = {"event_id", "session_id", "entity_id", "position", "dead"}
        if not isinstance(event, dict) or set(event) != required:
            raise ValueError("invalid body lifecycle event")
        for key in ("event_id", "session_id", "entity_id"):
            token(event[key])
        pos = point(event["position"])
        if type(event["dead"]) is not bool:
            raise ValueError("invalid lifecycle outcome")
        payload = json.dumps({"body_ended": event}, sort_keys=True)
        with self.conn:
            old = self.conn.execute("SELECT payload,response FROM nemesis_events WHERE namespace=? AND event=?",
                                    (self.namespace, event["event_id"])).fetchone()
            if old:
                if old[0] != payload:
                    raise ValueError("conflicting lifecycle replay")
                return {**json.loads(old[1]), "duplicate": True}
            binding = self.conn.execute(
                "SELECT person FROM nemesis_bindings WHERE namespace=? AND session=? AND entity=?",
                (self.namespace, event["session_id"], event["entity_id"])).fetchone()
            if not binding:
                raise ValueError("unknown body")
            state = self.get(binding[0])
            if state["binding"] != {"session_id": event["session_id"], "entity_id": event["entity_id"]}:
                raise ValueError("stale body ended after rematerialization")
            state.update(mode="dead" if event["dead"] else "simulated", position=pos,
                         binding=None, lease=None)
            self._save(state)
            response = {"person_id": state["person_id"], "mode": state["mode"], "duplicate": False}
            self.conn.execute("INSERT INTO nemesis_events VALUES(?,?,?,?)",
                              (self.namespace, event["event_id"], payload, json.dumps(response, sort_keys=True)))
            return response

    def mark_dead(self, person):
        with self.conn:
            state = self.get(person)
            state.update(mode="dead", binding=None, lease=None)
            self._save(state)
