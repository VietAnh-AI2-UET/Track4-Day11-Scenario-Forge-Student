"""Part C: estimate a rare probability honestly. TODO 4, 6 and 7."""
from __future__ import annotations

import math

import numpy as np

from avsim import space
from .search import proposal_logpdf


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """TODO 4. Wilson score interval for k successes in n trials. Must behave at k = 0 (lower bound 0,
    upper bound > 0) where the plain normal interval collapses to [0, 0]. Return (0, 1) for n = 0."""
    if n == 0:
        return 0.0, 1.0
    proportion = k / n
    z2 = z * z
    denominator = 1.0 + z2 / n
    center = (proportion + z2 / (2.0 * n)) / denominator
    margin = z * math.sqrt(
        proportion * (1.0 - proportion) / n + z2 / (4.0 * n * n)
    ) / denominator
    # Preserve exact endpoints when every trial has the same outcome.
    lo = 0.0 if k == 0 else max(0.0, center - margin)
    hi = 1.0 if k == n else min(1.0, center + margin)
    return lo, hi


def log_weights(Z, Bn, nat: space.Natural, prop: dict, beta: float = 0.2) -> np.ndarray:
    """TODO 6. log p(u) - log q(u) for each row, where q is the DEFENSIVE MIXTURE
    q = (1 - beta) * proposal + beta * natural.

    nat.logpdf(Z, Bn) gives log p; proposal_logpdf(prop, Z, Bn) gives log of the CEM proposal.
    Use np.logaddexp so a weight of 1e-30 does not underflow to 0."""
    log_p = nat.logpdf(Z, Bn)
    log_proposal = proposal_logpdf(prop, Z, Bn)
    # Combine mixture densities in log space to avoid numerical underflow.
    log_q = np.logaddexp(
        np.log1p(-beta) + log_proposal,
        np.log(beta) + log_p,
    )
    return log_p - log_q


def is_estimate(logw: np.ndarray, y: np.ndarray, z: float = 1.96) -> dict:
    """TODO 7. Importance-sampling estimate of P(y = 1) under the natural distribution.

    w = exp(logw); p = mean(w * y)  (NOT normalised by sum(w): that version is biased for small n);
    se = std(w * y, ddof=1) / sqrt(n); CI = [max(0, p - z se), p + z se];
    Kish effective sample size ess = (sum w)^2 / sum(w^2).
    Return dict(p=, lo=, hi=, se=, ess=, n=)."""
    weights = np.exp(logw)
    weighted_events = weights * y
    n = weighted_events.size
    p = float(np.mean(weighted_events))
    se = float(np.std(weighted_events, ddof=1) / math.sqrt(n))
    ess = float(np.sum(weights) ** 2 / np.sum(weights ** 2))
    return dict(
        p=p,
        lo=max(0.0, p - z * se),
        hi=p + z * se,
        se=se,
        ess=ess,
        n=n,
    )


def rule_of_three(n_eff: float) -> float:
    """Given: 95% upper bound on a probability when 0 events were seen in n_eff independent tries."""
    return 3.0 / max(n_eff, 1.0)
