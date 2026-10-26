"""Engine-independent offscreen movement for promoted NPC identities.

No REDengine handles or vanilla NPC mutations. Coordinates are abstract world-space
meters supplied by a *future verified* adapter; appearance is an immutable token.
"""
from dataclasses import dataclass, replace
import math

MAX_STEP_SECONDS = 3600.0
MAX_SPEED = 12.0


@dataclass(frozen=True)
class PersistentNPC:
    npc_id: str
    appearance_id: str
    position: tuple[float, float]
    destination: tuple[float, float]
    speed_mps: float
    last_tick: float
    visible: bool = False


def _point(value):
    if (not isinstance(value, (tuple, list)) or len(value) != 2
            or any(type(x) not in (float, int) or not math.isfinite(x) for x in value)):
        raise ValueError("position must be finite two-dimensional coordinates")
    return (float(value[0]), float(value[1]))


def validate(npc):
    if not isinstance(npc, PersistentNPC):
        raise ValueError("invalid NPC record")
    for value in (npc.npc_id, npc.appearance_id):
        if not isinstance(value, str) or not 1 <= len(value) <= 128:
            raise ValueError("missing stable identity or appearance")
    _point(npc.position)
    _point(npc.destination)
    if type(npc.speed_mps) not in (int, float) or not math.isfinite(npc.speed_mps) or not 0 <= npc.speed_mps <= MAX_SPEED:
        raise ValueError("invalid speed")
    if type(npc.last_tick) not in (int, float) or not math.isfinite(npc.last_tick):
        raise ValueError("invalid simulation timestamp")
    if type(npc.visible) is not bool:
        raise ValueError("invalid visibility")


def simulate_to(npc: PersistentNPC, timestamp: float) -> PersistentNPC:
    """Advance only offscreen actors. Reject time reversal; cap large time jumps.

    Calling again with the same timestamp is idempotent. Visibility transitions
    belong to the engine adapter and must first reconcile the observed position.
    """
    validate(npc)
    if type(timestamp) not in (int, float) or not math.isfinite(timestamp) or timestamp < npc.last_tick:
        raise ValueError("invalid or regressing timestamp")
    if npc.visible:
        return npc  # Never teleport a visible entity or consume time on its behalf.
    delta = min(float(timestamp) - npc.last_tick, MAX_STEP_SECONDS)
    x, y = _point(npc.position)
    tx, ty = _point(npc.destination)
    distance = math.hypot(tx - x, ty - y)
    step = min(distance, delta * npc.speed_mps)
    position = (tx, ty) if distance == 0 or step == distance else (
        x + (tx - x) * step / distance, y + (ty - y) * step / distance)
    if not all(math.isfinite(v) for v in position):
        raise ValueError("movement overflow")
    return replace(npc, position=position, last_tick=float(timestamp))


def leave_view(npc: PersistentNPC, observed_position, timestamp: float) -> PersistentNPC:
    """Record last engine-observed position as NPC leaves V's visibility."""
    validate(npc)
    if type(timestamp) not in (int, float) or not math.isfinite(timestamp) or timestamp < npc.last_tick:
        raise ValueError("invalid transition timestamp")
    return replace(npc, position=_point(observed_position), last_tick=float(timestamp), visible=False)


def enter_view(npc: PersistentNPC, timestamp: float) -> PersistentNPC:
    """Return a spawn candidate; caller must validate safe spawn and quest guards."""
    updated = simulate_to(npc, timestamp)
    return replace(updated, visible=True)
