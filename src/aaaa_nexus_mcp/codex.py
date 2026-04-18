"""Numerical invariants for the locally-executed system tools.

Public tool responses expose only feature-level metadata (tier counts, block
dimension, thresholds). The identities below are runtime-checked at import
time to catch accidental divergence.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Tier-1: dimension and quantization parameters
# ---------------------------------------------------------------------------
TIER1_MIN_COUNT: int = 196560
RESIDUAL_NORM_LIMIT: int = 196884
FAITHFUL_DIM: int = 196883
BLOCK_DIM: int = RESIDUAL_NORM_LIMIT - TIER1_MIN_COUNT  # 324 = 18^2
TIER_CLOSURE: int = RESIDUAL_NORM_LIMIT - TIER1_MIN_COUNT - BLOCK_DIM  # 0

# ---------------------------------------------------------------------------
# Tier-2: trust / verification
# ---------------------------------------------------------------------------
TRUST_NUM: int = 1820
TRUST_PRIME: int = 1823
TRUST_FLOOR: float = TRUST_NUM / TRUST_PRIME
POLICY_EPSILON: float = 1.0 / RESIDUAL_NORM_LIMIT
DRIFT_LIMIT: float = BLOCK_DIM / RESIDUAL_NORM_LIMIT

# ---------------------------------------------------------------------------
# Tier-3: session / delegation
# ---------------------------------------------------------------------------
QK_BLOCK_DIM: int = 24
DELEGATION_DEPTH_LIMIT: int = 23
RATCHET_PERIOD: int = 47
CFT_COUNT: int = 71
HYPERFACTORIAL_3: int = 108
SEMANTIC_FRICTION: float = 720.0 / BLOCK_DIM
TIER_SIZES: tuple[int, ...] = (
    196560,
    16773120,
    398034000,
    4881795840,
    38620692000,
)

# ---------------------------------------------------------------------------
# Tier-4: 3-fold variant projection (used by nexus_variant_rotate)
# ---------------------------------------------------------------------------
TRIALITY_NEUTRAL: int = 92
TRIALITY_CHARGED: int = 86
TRIALITY_TOTAL: int = TRIALITY_NEUTRAL + 2 * TRIALITY_CHARGED  # 264

# ---------------------------------------------------------------------------
# Runtime invariants
# ---------------------------------------------------------------------------
assert TIER_CLOSURE == 0, "tier closure invariant failed"
assert RESIDUAL_NORM_LIMIT == FAITHFUL_DIM + 1, "faithful dim invariant failed"
assert BLOCK_DIM == 324, "block dim != 324"
assert TRUST_PRIME % 24 == DELEGATION_DEPTH_LIMIT, "trust prime invariant failed"
assert CFT_COUNT == 24 + RATCHET_PERIOD, "cft count invariant failed"
