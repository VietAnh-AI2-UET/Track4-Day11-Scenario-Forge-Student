"""Part B: physics check. TODO 3."""
from __future__ import annotations

from math import pi

G = 9.81


def is_feasible(p: dict) -> bool:
    """TODO 3. False for scenarios no real road user could produce. Reject if ANY of:

    - the lane change needs more sideways grip than the road has: the cosine lane change of 3.5 m over
      p["cutDur"] seconds peaks at a_lat = (pi / cutDur)^2 * 3.5 / 2; reject if a_lat > mu * g;
    - the post-merge braking p["cutBrake"] exceeds mu * g;
    - the pedestrian runs: p["pedV"] > 2.5 m/s;
    - the cut-in speed p["cutV"] is not in (0, 22] m/s.
    mu is p["mu"]. A search that keeps infeasible scenarios reports failures that cannot happen.
    """
    grip = p["mu"] * G
    # Peak lateral acceleration for a cosine lane change across 3.5 metres.
    a_lat = (pi / p["cutDur"]) ** 2 * 3.5 / 2
    return bool(
        a_lat <= grip
        and p["cutBrake"] <= grip
        and p["pedV"] <= 2.5
        and 0 < p["cutV"] <= 22
    )
