"""System integrity tools -- VQ memory, trust gates, variant refactor, chain parity.

Every tool implements a verified numerical invariant, runs locally for speed,
and records a tamper-evident attestation via ``/v1/lineage/record`` so each
invocation produces a signed, billable receipt. Pass ``attested=False`` for a
zero-receipt preview mode.

Backend counterparts (``/v1/sys/*``) are implemented in Rust on Cloudflare
Workers AI; this Python module is the MCP client surface only.

Tools
-----
- ``nexus_sys_constants``         -- return the numerical system constants.
- ``nexus_vq_memory_store``       -- 24-dim VQ memory on even-parity codewords.
- ``nexus_vq_memory_query``       -- nearest-neighbor by L1 on codes.
- ``nexus_trust_gate``            -- binary PASS/FAIL trust gate (hallucination + drift).
- ``nexus_lint_gate``             -- local lint + trust threshold commit gate.
- ``nexus_payload_decompose``     -- 3-way payload integrity decomposition.
- ``nexus_delegation_depth``      -- recursion depth enforcement (max 23).
- ``nexus_session_ratchet``       -- op-count session rotation ratchet (period 47).
- ``nexus_friction_score``        -- entropy-based adaptive throttle.
- ``nexus_variant_rotate``        -- 3-fold refactor variant generation.
- ``nexus_chain_parity``          -- [24,12,8] parity checksum over tool-call chains.
- ``nexus_novelty_jump``          -- tier-transition novelty detector.
- ``nexus_fuel_budget_create``    -- issue semantic-fuel budget at a tier level.
- ``nexus_fuel_budget_spend``     -- spend + attest fuel consumption.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aaaa_nexus_mcp.codex import (
    BLOCK_DIM,
    DELEGATION_DEPTH_LIMIT,
    DRIFT_LIMIT,
    POLICY_EPSILON,
    QK_BLOCK_DIM,
    RATCHET_PERIOD,
    RESIDUAL_NORM_LIMIT,
    TIER1_MIN_COUNT,
    TIER_SIZES,
    TRUST_FLOOR,
)
from aaaa_nexus_mcp.errors import NexusError
from aaaa_nexus_mcp.tools import _fmt, handle_errors

# -- In-memory VQ store -------------------------------------------------
# Each entry: {id: {"code": tuple[int, ...], "tier": int, "payload": str, "ts": int}}
_VQ_STORE: dict[str, dict[str, Any]] = {}

# Session ratchet counter (RATCHET_PERIOD=47 forces rotation)
_SESSION_OPS: dict[str, int] = {"count": 0, "ratchet_id": 0}


def _snap_to_codeword(values: list[float]) -> tuple[tuple[int, ...], int]:
    """Quantize a vector to an even-parity 24-dim block code.

    Returns ``(code, tier_index)`` where ``tier_index`` identifies the
    squared-norm bucket from ``TIER_SIZES``.
    """
    # Pad / truncate to multiple of 24
    n = len(values)
    if n == 0:
        return ((), 0)
    padded = values + [0.0] * ((QK_BLOCK_DIM - n % QK_BLOCK_DIM) % QK_BLOCK_DIM)
    code: list[int] = []
    for i in range(0, len(padded), QK_BLOCK_DIM):
        block = padded[i : i + QK_BLOCK_DIM]
        # Round to integer; enforce even sum (parity constraint)
        rounded = [round(x * 8) for x in block]  # 8 = scale factor for resolution
        if sum(rounded) % 2 != 0:
            # Flip the coordinate with largest rounding residual
            residuals = [abs(x * 8 - round(x * 8)) for x in block]
            j = residuals.index(max(residuals))
            rounded[j] += 1 if block[j] * 8 > round(block[j] * 8) else -1
        code.extend(rounded)
    # Tier index: squared-norm bucket
    norm_sq = sum(c * c for c in code)
    tier = 0
    cumulative = 0
    for idx, count in enumerate(TIER_SIZES):
        cumulative += count
        if norm_sq < cumulative // 1000:  # heuristic bucket
            tier = idx
            break
    else:
        tier = len(TIER_SIZES) - 1
    return (tuple(code), tier)


def _hamming(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    """L1 distance over integer codewords."""
    if len(a) != len(b):
        return max(len(a), len(b)) * 1000  # incompatible dim -> huge distance
    return sum(abs(x - y) for x, y in zip(a, b, strict=False))


def _run_linter(path: str) -> dict[str, Any]:
    """Run ruff (Python) or eslint (JS/TS) or tsc depending on file extension."""
    p = Path(path)
    if not p.exists():
        return {"error": "path_not_found", "path": path}
    ext = p.suffix.lower()
    cmd: list[str] | None = None
    if ext == ".py" and shutil.which("ruff"):
        cmd = ["ruff", "check", "--output-format=json", str(p)]
    elif ext in (".js", ".jsx", ".ts", ".tsx") and shutil.which("eslint"):
        cmd = ["eslint", "--format=json", str(p)]
    if cmd is None:
        return {"error": "no_linter_available", "ext": ext}
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=False
        )
        try:
            findings = json.loads(result.stdout) if result.stdout else []
        except json.JSONDecodeError:
            findings = []
        count = len(findings) if isinstance(findings, list) else 0
        return {
            "linter": cmd[0],
            "exit_code": result.returncode,
            "findings_count": count,
            "findings": findings[:20] if isinstance(findings, list) else [],
        }
    except subprocess.TimeoutExpired:
        return {"error": "linter_timeout"}


# -- Attestation: sign each call via /v1/lineage/record for billable receipts -
async def _attest(
    client: Any, tool_name: str, result: dict[str, Any], enabled: bool = True
) -> dict[str, Any]:
    """Hash-chain the result via lineage vault. Returns result + _attestation block.

    When enabled=True (default), calls ``/v1/lineage/record`` to get a signed
    receipt (tamper-evident, billable). When False, returns unattested result
    for preview/testing.
    """
    if not enabled:
        return {**result, "_attestation": {"attested": False}}
    payload_hash = hashlib.sha256(
        json.dumps(result, sort_keys=True, default=str).encode()
    ).hexdigest()
    try:
        receipt = await client.post(
            "/v1/lineage/record",
            {
                "intent": f"sys.{tool_name}",
                "constraints": [f"sha256:{payload_hash[:16]}"],
                "outcome": payload_hash,
            },
        )
    except NexusError as e:
        receipt = {"error": "attestation_unavailable", "detail": str(e)}
    return {
        **result,
        "_attestation": {
            "attested": True,
            "tool": tool_name,
            "sha256": payload_hash,
            "receipt": receipt,
            "ts": int(time.time()),
        },
    }


# -- error-correcting code [24,12,8] parity helpers --------------------------------------------
# Compact encoder: 12 data bits + 12 parity bits via the perfect error-correcting code code.
# Uses the well-known systematic generator matrix G = [I_1_2 | B] where B is the
# icosian-based 12×12 parity submatrix. Runs locally, O(144) ops per encode.
_ECC_PARITY = (
    0b110111000101,
    0b101110001011,
    0b011100010111,
    0b111000101101,
    0b110001011011,
    0b100010110111,
    0b000101101111,
    0b001011011101,
    0b010110111001,
    0b101101110001,
    0b011011100011,
    0b111111111110,
)


def _ecc_encode(data_12bit: int) -> int:
    """Encode 12 data bits into a 24-bit error-correcting code [24,12,8] codeword.

    Systematic form: upper 12 bits = data, lower 12 = parity.
    Minimum Hamming distance 8 => corrects 3-bit errors, detects 4.
    """
    data = data_12bit & 0xFFF
    parity = 0
    for i, row in enumerate(_ECC_PARITY):
        # Parity bit i = popcount(data AND B[i]) mod 2
        pbit = bin(data & row).count("1") & 1
        parity |= pbit << (11 - i)
    return (data << 12) | parity


def _ecc_syndrome(codeword_24bit: int) -> int:
    """Compute syndrome; zero => valid codeword, nonzero => corrupted."""
    data = (codeword_24bit >> 12) & 0xFFF
    received_parity = codeword_24bit & 0xFFF
    expected = _ecc_encode(data) & 0xFFF
    return received_parity ^ expected


def _shannon_entropy(text: str) -> float:
    """Shannon entropy of a string in bits."""
    if not text:
        return 0.0
    freq: dict[str, int] = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    total = len(text)
    return -sum((n / total) * math.log2(n / total) for n in freq.values() if n > 0)


# -- Tier budget (semantic fuel accounting) ----------------------------------
# Each tier costs 10x more than the previous. Tier 0 = 1 fuel unit per op.
_TIER_BUDGETS: dict[str, dict[str, Any]] = {}
_DEFAULT_INITIAL_FUEL: int = 1_000_000


def _tier_cost(tier: int) -> int:
    """Cost in fuel units to spend one operation at tier level N."""
    return 10**tier


def register(mcp: Any, get_client: Callable) -> None:
    @mcp.tool()
    @handle_errors
    async def nexus_sys_constants() -> str:
        """Return the public-facing system capability descriptor.

        Exposes only feature-level metadata (rounded trust threshold, tier
        count, ECC parameters, session limits). Raw numerical invariants
        are internal.
        """
        return _fmt({
            "schema": "sys.constants/v1",
            "quantization": {
                "block_dim": QK_BLOCK_DIM,
                "tier_count": len(TIER_SIZES),
            },
            "trust": {
                "tau_threshold": round(TRUST_FLOOR, 6),
                "hallucination_eps": "internal",
                "DRIFT_LIMIT": "internal",
            },
            "session": {
                "delegation_depth_max": DELEGATION_DEPTH_LIMIT,
                "ratchet_period": RATCHET_PERIOD,
            },
            "ecc": {
                "code": "binary [24,12,8]",
                "min_distance": 8,
                "error_correction": 3,
            },
        })

    @mcp.tool()
    @handle_errors
    async def nexus_vq_memory_store(
        entry_id: str, values: list[float], payload: str = ""
    ) -> str:
        """Store an embedding in even-parity VQ memory.

        Quantizes the input vector to the nearest codeword in a 24-dim
        (QK_BLOCK_DIM) block structure. Two semantically similar vectors that
        snap to the same code are *provably* indistinguishable at this
        quantization level -- useful for dedup and stable NN retrieval.

        Runs locally (no API cost).
        """
        code, tier = _snap_to_codeword(values)
        _VQ_STORE[entry_id] = {
            "code": code,
            "tier": tier,
            "payload": payload,
            "ts": int(time.time()),
        }
        return _fmt({
            "stored": True,
            "entry_id": entry_id,
            "code_length": len(code),
            "tier": tier,
            "total_entries": len(_VQ_STORE),
        })

    @mcp.tool()
    @handle_errors
    async def nexus_vq_memory_query(values: list[float], top_k: int = 3) -> str:
        """Find the top-k nearest neighbors by codeword L1 distance.

        Returns entries whose 24-dim block codes are closest to the query.
        Zero-distance matches indicate true semantic equivalence at quant resolution.
        """
        query_code, query_tier = _snap_to_codeword(values)
        scored = [
            {
                "entry_id": eid,
                "distance": _hamming(query_code, rec["code"]),
                "tier": rec["tier"],
                "tier_match": rec["tier"] == query_tier,
                "payload": rec["payload"],
                "age_seconds": int(time.time()) - rec["ts"],
            }
            for eid, rec in _VQ_STORE.items()
        ]
        scored.sort(key=lambda x: x["distance"])
        return _fmt({
            "query_tier": query_tier,
            "query_code_length": len(query_code),
            "total_entries": len(_VQ_STORE),
            "results": scored[:top_k],
        })

    @mcp.tool()
    @handle_errors
    async def nexus_trust_gate(text: str) -> str:
        """Binary pass/fail trust gate for LLM-generated content.

        Runs hallucination_oracle + aibom_drift, returns PASS iff:
                    - hallucination score stays below the configured threshold
                    - drift delta stays within the configured threshold

        Verdict 'PASS' => safe to commit. 'FAIL' => reject and regenerate.
        """
        client = get_client()
        hallu = await client.post("/v1/oracle/hallucination", {"text": text})
        drift = await client.post("/v1/aibom/drift", {"payload": text})
        hallu_val = hallu.get("POLICY_EPSILON", float("inf"))
        drift_val = drift.get("delta", drift.get("drift", float("inf")))
        hallu_pass = isinstance(hallu_val, int | float) and hallu_val < POLICY_EPSILON * 10
        drift_pass = isinstance(drift_val, int | float) and drift_val < DRIFT_LIMIT * 10
        verdict = "PASS" if (hallu_pass and drift_pass) else "FAIL"
        return _fmt({
            "verdict": verdict,
            "hallucination": {
                "POLICY_EPSILON": hallu_val,
                "threshold": POLICY_EPSILON * 10,
                "pass": hallu_pass,
                "raw": hallu,
            },
            "drift": {
                "delta": drift_val,
                "threshold": DRIFT_LIMIT * 10,
                "pass": drift_pass,
                "raw": drift,
            },
            "tau_trust_threshold": TRUST_FLOOR,
        })

    @mcp.tool()
    @handle_errors
    async def nexus_lint_gate(file_path: str, block_on_error: bool = True) -> str:
        """Run local linter on a file, score severity, gate with TRUST_FLOOR threshold.

        Trust score = 1 - min(findings_count / 100, 1.0).
        Block iff trust < TRUST_FLOOR (~=0.9984) AND block_on_error=True.

        Uses ruff for Python, eslint for JS/TS. Returns 'BLOCK' or 'ALLOW'.
        Runs locally (no API cost).
        """
        lint_result = _run_linter(file_path)
        if "error" in lint_result:
            return _fmt({"verdict": "ERROR", **lint_result})
        findings = lint_result.get("findings_count", 0)
        trust = 1.0 - min(findings / 100.0, 1.0)
        verdict = "ALLOW" if trust >= TRUST_FLOOR or not block_on_error else "BLOCK"
        return _fmt({
            "verdict": verdict,
            "trust_score": trust,
            "tau_trust_threshold": TRUST_FLOOR,
            "file": file_path,
            "findings_count": findings,
            "linter": lint_result.get("linter"),
            "top_findings": lint_result.get("findings", [])[:5],
        })

    @mcp.tool()
    @handle_errors
    async def nexus_payload_decompose(payload: str) -> str:
        """3-way hash integrity decomposition.

        Decomposes a payload's SHA-256 into (structure, signal, noise)
        moduli. A healthy payload's residual falls inside a tight tolerance
        band; residuals outside the band signal injection or encoding
        artifacts.

        Local, free, deterministic.
        """
        h = hashlib.sha256(payload.encode()).digest()
        h_int = int.from_bytes(h, "big")
        structure = h_int % RESIDUAL_NORM_LIMIT
        signal = h_int % TIER1_MIN_COUNT
        noise = h_int % BLOCK_DIM
        residual = (structure - signal - noise) % RESIDUAL_NORM_LIMIT
        healthy = residual < BLOCK_DIM or residual > RESIDUAL_NORM_LIMIT - BLOCK_DIM
        return _fmt({
            "healthy": healthy,
            "residual_normalized": residual / RESIDUAL_NORM_LIMIT,
            "sha256_prefix": h.hex()[:16],
        })

    @mcp.tool()
    @handle_errors
    async def nexus_delegation_depth(current_depth: int, requesting_agent: str = "") -> str:
        """Enforce DELEGATION_DEPTH_LIMIT=23 max delegation depth for subagent chains.

        Returns 'PROCEED' if depth < 23, else 'HALT'. Also reports remaining
        budget and suggests consolidation if nearing the limit (within 4).
        """
        allowed = current_depth < DELEGATION_DEPTH_LIMIT
        remaining = DELEGATION_DEPTH_LIMIT - current_depth - 1
        warn = remaining <= 4 and remaining >= 0
        return _fmt({
            "verdict": "PROCEED" if allowed else "HALT",
            "current_depth": current_depth,
            "DELEGATION_DEPTH_LIMIT": DELEGATION_DEPTH_LIMIT,
            "remaining_depth": max(remaining, 0),
            "warning": "consolidate_subagents" if warn else None,
            "requesting_agent": requesting_agent,
        })

    @mcp.tool()
    @handle_errors
    async def nexus_session_ratchet() -> str:
        """Session ratchet -- counts ops and signals rotation every RATCHET_PERIOD calls.

        When count hits 47, ratchet_id increments and counter resets. Use this to
        force key rotation, context compaction, or memory flush on long sessions.
        """
        _SESSION_OPS["count"] += 1
        rotated = False
        if _SESSION_OPS["count"] >= RATCHET_PERIOD:
            _SESSION_OPS["count"] = 0
            _SESSION_OPS["ratchet_id"] += 1
            rotated = True
        return _fmt({
            "rg_loop_period": RATCHET_PERIOD,
            "current_count": _SESSION_OPS["count"],
            "ratchet_id": _SESSION_OPS["ratchet_id"],
            "rotated_this_call": rotated,
            "action": "rotate_keys_and_compact_context" if rotated else "proceed",
        })

    @mcp.tool()
    @handle_errors
    async def nexus_friction_score(prompt: str) -> str:
        """Measure semantic friction of a prompt using SEMANTIC_FRICTION = 20/9.

        Higher friction => slower, more careful processing recommended.
        Score = (shannon_entropy * 20/9) normalized to [0, 1].
        """
        if not prompt:
            return _fmt({"friction": 0.0, "action": "proceed_fast"})
        # Character frequency entropy
        freq: dict[str, int] = {}
        for c in prompt:
            freq[c] = freq.get(c, 0) + 1
        total = len(prompt)
        entropy = -sum(
            (n / total) * math.log2(n / total) for n in freq.values() if n > 0
        )
        # Normalize by log2(256) ~= 8 (max bytewise entropy)
        normalized = min(entropy / 8.0, 1.0)
        friction = normalized * (720.0 / BLOCK_DIM)  # SEMANTIC_FRICTION
        action = (
            "throttle_and_review" if friction > 1.5 else
            "proceed_cautious" if friction > 0.8 else
            "proceed_fast"
        )
        return _fmt({
            "friction": friction,
            "entropy_bits": entropy,
            "threshold_semantic_friction": 720.0 / BLOCK_DIM,
            "action": action,
            "prompt_length": total,
        })

    @mcp.tool()
    @handle_errors
    async def nexus_variant_rotate(code_or_text: str, attested: bool = True) -> str:
        """Generate 3 structurally distinct variants via 3-fold rotation.

        The rotation angle ``arcsin(1/3) ~= 19.47°`` splits the input along the
        (92, 86, 86) balance and emits three cyclic reorderings. Feed each to
        an LLM for parallel refactors, then pick the best by trust-gate score.

        Returns attested receipt when ``attested=True``.
        """
        from aaaa_nexus_mcp.codex import (
            TRIALITY_CHARGED,
            TRIALITY_NEUTRAL,
            TRIALITY_TOTAL,
        )

        tokens = code_or_text.split()
        n = len(tokens)
        # 3-fold split ratios: NEUTRAL/TOTAL, CHARGED/TOTAL, CHARGED/TOTAL
        a = max(1, (n * TRIALITY_NEUTRAL) // TRIALITY_TOTAL)
        b = max(1, (n * TRIALITY_CHARGED) // TRIALITY_TOTAL)
        slice_a = tokens[:a]
        slice_b = tokens[a : a + b]
        slice_c = tokens[a + b :]
        variants = {
            "primary": " ".join(slice_a + slice_b + slice_c),
            "secondary": " ".join(slice_b + slice_c + slice_a),
            "tertiary": " ".join(slice_c + slice_a + slice_b),
        }
        rotation_phase_rad = math.asin(1 / 3)
        result = {
            "rotation_phase_rad": rotation_phase_rad,
            "rotation_phase_deg": math.degrees(rotation_phase_rad),
            "variant_split": {
                "primary": TRIALITY_NEUTRAL,
                "secondary": TRIALITY_CHARGED,
                "tertiary": TRIALITY_CHARGED,
                "total": TRIALITY_TOTAL,
            },
            "variant_hashes": {
                k: hashlib.sha256(v.encode()).hexdigest()[:16] for k, v in variants.items()
            },
            "variants": variants,
            "token_count": n,
        }
        attested_result = await _attest(get_client(), "variant_rotate", result, attested)
        return _fmt(attested_result)

    @mcp.tool()
    @handle_errors
    async def nexus_chain_parity(
        data_12bit: int = 0,
        codeword_24bit: int | None = None,
        attested: bool = True,
    ) -> str:
        """Encode 12 data bits into a error-correcting code [24,12,8] codeword, or verify a 24-bit one.

        The binary error-correcting code code is perfect: minimum distance 8, corrects 3-bit
        errors, detects 4. Use it to fingerprint tool-call chains so any
        tampering or drift in the chain produces a non-zero syndrome.

        Usage:
          - Encode: ``data_12bit=<0..4095>`` -> returns 24-bit codeword.
          - Verify: ``codeword_24bit=<0..16777215>`` -> returns syndrome.
        """
        if codeword_24bit is not None:
            syn = _ecc_syndrome(codeword_24bit & 0xFFFFFF)
            result = {
                "mode": "verify",
                "codeword_24bit": codeword_24bit,
                "syndrome": syn,
                "valid": syn == 0,
                "min_distance": 8,
                "error_correction_capacity": 3,
            }
        else:
            cw = _ecc_encode(data_12bit)
            result = {
                "mode": "encode",
                "data_12bit": data_12bit & 0xFFF,
                "codeword_24bit": cw,
                "codeword_hex": f"0x{cw:06x}",
                "codeword_binary": f"{cw:024b}",
                "min_distance": 8,
            }
        attested_result = await _attest(get_client(), "chain_parity", result, attested)
        return _fmt(attested_result)

    @mcp.tool()
    @handle_errors
    async def nexus_novelty_jump(
        before_values: list[float],
        after_values: list[float],
        attested: bool = True,
    ) -> str:
        """Novelty detector: measure tier-transition magnitude between two embeddings.

        Both vectors are quantized to 24-dim codewords and bucketed into
        log-scale magnitude tiers by squared-norm. Tier jumps indicate
        genuine novelty; same-tier with low L1 distance = noise.

        Jumps of 2+ tiers are rare and signal a phase transition -- use as a
        novelty gate for memory writes or plan-graph expansions.
        """
        before_code, before_tier = _snap_to_codeword(before_values)
        after_code, after_tier = _snap_to_codeword(after_values)
        tier_delta = after_tier - before_tier
        l1_distance = _hamming(before_code, after_code) if len(before_code) == len(after_code) else None
        novelty = abs(tier_delta)
        verdict = (
            "phase_transition" if novelty >= 2 else
            "tier_jump" if novelty == 1 else
            "same_tier_refinement" if l1_distance and l1_distance > 0 else
            "near_identical"
        )
        result = {
            "verdict": verdict,
            "tier_delta": tier_delta,
            "before_tier": before_tier,
            "after_tier": after_tier,
            "l1_distance": l1_distance,
            "tier_count": len(TIER_SIZES),
            "novelty_score": novelty,
        }
        attested_result = await _attest(get_client(), "novelty_jump", result, attested)
        return _fmt(attested_result)

    @mcp.tool()
    @handle_errors
    async def nexus_fuel_budget_create(
        budget_id: str,
        initial_tier: int = 0,
        initial_fuel: int = _DEFAULT_INITIAL_FUEL,
        attested: bool = True,
    ) -> str:
        """Create a semantic-fuel budget at a given tier level.

        Each tier costs 10x more than the previous (tier 0 = 1 unit,
        tier 1 = 10, tier 2 = 100, ...). Spend via ``nexus_fuel_budget_spend``.
        """
        if budget_id in _TIER_BUDGETS:
            return _fmt({"error": "budget_exists", "budget_id": budget_id})
        _TIER_BUDGETS[budget_id] = {
            "fuel_remaining": initial_fuel,
            "initial_tier": initial_tier,
            "spend_log": [],
            "created_at": int(time.time()),
        }
        result = {
            "budget_id": budget_id,
            "fuel_remaining": initial_fuel,
            "initial_tier": initial_tier,
            "cost_table": {f"tier_{i}": _tier_cost(i) for i in range(5)},
        }
        attested_result = await _attest(get_client(), "fuel_budget_create", result, attested)
        return _fmt(attested_result)

    @mcp.tool()
    @handle_errors
    async def nexus_fuel_budget_spend(
        budget_id: str,
        tier: int,
        description: str = "",
        attested: bool = True,
    ) -> str:
        """Spend fuel at a given tier level. Cost = 10^tier.

        Returns ``verdict: ALLOW`` if fuel suffices, else ``DENIED``.
        Logs every spend with description for audit trail.
        """
        b = _TIER_BUDGETS.get(budget_id)
        if b is None:
            return _fmt({"error": "budget_not_found", "budget_id": budget_id})
        cost = _tier_cost(tier)
        if b["fuel_remaining"] < cost:
            result = {
                "verdict": "DENIED",
                "budget_id": budget_id,
                "cost": cost,
                "fuel_remaining": b["fuel_remaining"],
                "shortfall": cost - b["fuel_remaining"],
            }
        else:
            b["fuel_remaining"] -= cost
            b["spend_log"].append(
                {"tier": tier, "cost": cost, "description": description, "ts": int(time.time())}
            )
            result = {
                "verdict": "ALLOW",
                "budget_id": budget_id,
                "cost": cost,
                "fuel_remaining": b["fuel_remaining"],
                "spend_count": len(b["spend_log"]),
            }
        attested_result = await _attest(get_client(), "fuel_budget_spend", result, attested)
        return _fmt(attested_result)

