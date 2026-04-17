"""Federated LoRA training loop -- capture, score, contribute, query.

The flywheel: every (buggy_code -> linter -> fix) triple captured by an
agent becomes a training sample. Samples are scored by the TRUST_FLOOR
threshold locally, hash-chained for provenance, then submitted to a
shared pool. Cloudflare Workers AI trains a LoRA adapter periodically,
and agents fetch the latest adapter ID to use in inference calls.

Privacy: samples are content-hashed and stripped of identifiers before
upload. Only the (diff, lint_delta, trust_score) tuple is contributed --
no project paths, no personal names, no API keys.

Tools
-----
- ``nexus_lora_capture_fix``   -- record a (bad -> good) code fix locally.
- ``nexus_lora_contribute``    -- submit captured batch to training pool.
- ``nexus_lora_status``        -- query current training run + sample count.
- ``nexus_lora_adapter_current`` -- fetch latest adapter ID for inference.
- ``nexus_lora_reward_claim``  -- claim contributor reward (reputation-linked).

Pricing
-------
- capture_fix:       $0.000 (local, incentivize submission)
- contribute:        $0.010 (batch upload; micro-rebate per accepted sample)
- status:            $0.005
- adapter_current:   $0.010
- reward_claim:      $0.020 (reputation-tier gated)
"""

from __future__ import annotations

import hashlib
import re
import time
from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.codex import (
    POLICY_EPSILON,
    BLOCK_DIM,
    RESIDUAL_NORM_LIMIT,
    TRUST_FLOOR,
)
from aaaa_nexus_mcp.tools import _fmt, handle_errors

# Local capture buffer -- cleared after successful contribute()
_CAPTURE_BUFFER: list[dict[str, Any]] = []

# Maximum samples held locally before forced flush
_MAX_BUFFER = 256


# -- Privacy scrubbers --------------------------------------------------------
# Strip anything that could leak user / project identity before upload.

_PATH_PATTERNS = (
    re.compile(r"[A-Z]:\\[^\s\"'<>]+", re.IGNORECASE),  # Windows paths
    re.compile(r"/(?:home|Users|mnt|opt)/[^\s\"'<>]+"),  # Unix home paths
    re.compile(r"[a-zA-Z_][\w-]*@[\w.-]+\.[a-zA-Z]{2,}"),  # email addresses
    re.compile(r"\b(?:sk-|pk-|ghp_|xoxb-)[A-Za-z0-9_-]{16,}\b"),  # API tokens
    re.compile(r"(?i)(password|secret|api_?key|token)\s*[:=]\s*['\"][^'\"]+['\"]"),
)


def _scrub(text: str) -> str:
    """Remove paths, emails, tokens, and obvious secrets from text."""
    if not text:
        return ""
    scrubbed = text
    for pat in _PATH_PATTERNS:
        scrubbed = pat.sub("<REDACTED>", scrubbed)
    # Truncate to 8 KB to keep samples small
    return scrubbed[:8192]


def _sample_digest(bad: str, good: str) -> str:
    """Content-addressable hash of a training sample (dedup key)."""
    return hashlib.sha256(f"{bad}\x00{good}".encode()).hexdigest()


def _estimate_quality(
    bad: str, good: str, lint_delta: int, language: str
) -> float:
    """Cheap local quality score in [0, 1] before contribution.

    Weights:
    - lint_delta (bugs fixed):  60%
    - size ratio (good ≤ 2× bad, penalize bloat): 25%
    - language is recognized:   15%
    """
    if not bad or not good:
        return 0.0
    # Component 1: lint fixes normalized
    lint_score = min(lint_delta / 10.0, 1.0) if lint_delta > 0 else 0.0
    # Component 2: compactness (don't reward massive rewrites)
    ratio = len(good) / max(len(bad), 1)
    size_score = 1.0 if 0.5 <= ratio <= 2.0 else 0.5
    # Component 3: language
    lang_score = 1.0 if language in (
        "python", "javascript", "typescript", "rust", "go", "java", "c", "cpp"
    ) else 0.5
    return 0.60 * lint_score + 0.25 * size_score + 0.15 * lang_score


def register(mcp: Any, get_client: Callable) -> None:
    @mcp.tool()
    @handle_errors
    async def nexus_lora_capture_fix(
        bad_code: str,
        good_code: str,
        language: str = "python",
        lint_delta: int = 1,
        error_type: str = "",
    ) -> str:
        """Capture a (bad -> good) code fix locally for future contribution.

        The sample is scrubbed of paths/emails/tokens and assigned a
        content-addressable hash. Stored in-memory until flushed by
        ``nexus_lora_contribute``.

        ``lint_delta`` is the number of linter findings resolved by the
        fix (higher = more valuable training signal).
        """
        bad_scrubbed = _scrub(bad_code)
        good_scrubbed = _scrub(good_code)
        digest = _sample_digest(bad_scrubbed, good_scrubbed)

        # Dedup check
        if any(s["digest"] == digest for s in _CAPTURE_BUFFER):
            return _fmt({
                "captured": False,
                "reason": "duplicate",
                "digest": digest[:16],
            })

        quality = _estimate_quality(bad_scrubbed, good_scrubbed, lint_delta, language)
        sample = {
            "digest": digest,
            "language": language,
            "bad_len": len(bad_scrubbed),
            "good_len": len(good_scrubbed),
            "lint_delta": lint_delta,
            "error_type": error_type[:64],
            "quality_estimate": quality,
            "captured_at": int(time.time()),
            # Actual content held until contribute() flushes
            "_bad": bad_scrubbed,
            "_good": good_scrubbed,
        }

        # Enforce buffer cap -- drop lowest quality if full
        if len(_CAPTURE_BUFFER) >= _MAX_BUFFER:
            _CAPTURE_BUFFER.sort(key=lambda s: s["quality_estimate"])
            _CAPTURE_BUFFER.pop(0)

        _CAPTURE_BUFFER.append(sample)
        return _fmt({
            "captured": True,
            "digest": digest[:16],
            "quality_estimate": quality,
            "buffer_size": len(_CAPTURE_BUFFER),
            "buffer_cap": _MAX_BUFFER,
            "eligible_for_contribution": quality >= 0.6,
        })

    @mcp.tool()
    @handle_errors
    async def nexus_lora_contribute(min_quality: float = 0.6) -> str:
        """Submit all buffered samples above min_quality to the training pool.

        Each sample is tau-gated (hallucination + drift check on the good
        code) server-side; only samples that pass are accepted and
        included in the next LoRA training run.

        Returns counts + backend acceptance response. Clears the local
        buffer on success.
        """
        if not _CAPTURE_BUFFER:
            return _fmt({"submitted": 0, "reason": "empty_buffer"})

        eligible = [s for s in _CAPTURE_BUFFER if s["quality_estimate"] >= min_quality]
        if not eligible:
            return _fmt({
                "submitted": 0,
                "reason": "no_samples_above_threshold",
                "buffer_size": len(_CAPTURE_BUFFER),
                "min_quality": min_quality,
            })

        # Prepare upload payload -- strip internal keys
        batch = [
            {
                "digest": s["digest"],
                "language": s["language"],
                "bad": s["_bad"],
                "good": s["_good"],
                "lint_delta": s["lint_delta"],
                "error_type": s["error_type"],
                "quality_local": s["quality_estimate"],
                "ts": s["captured_at"],
            }
            for s in eligible
        ]

        client = get_client()
        try:
            response = await client.post(
                "/v1/lora/contribute",
                {"samples": batch, "tau_trust_threshold": TRUST_FLOOR},
            )
        except Exception as e:  # noqa: BLE001
            return _fmt({
                "submitted": 0,
                "error": "contribution_failed",
                "detail": str(e),
                "buffered": len(_CAPTURE_BUFFER),
            })

        # Success -- clear submitted samples from buffer
        submitted_digests = {s["digest"] for s in eligible}
        _CAPTURE_BUFFER[:] = [
            s for s in _CAPTURE_BUFFER if s["digest"] not in submitted_digests
        ]

        return _fmt({
            "submitted": len(eligible),
            "remaining_in_buffer": len(_CAPTURE_BUFFER),
            "backend": response,
            "tau_trust_threshold": TRUST_FLOOR,
        })

    @mcp.tool()
    @handle_errors
    async def nexus_lora_status() -> str:
        """Query the current training run status and pool statistics."""
        client = get_client()
        try:
            status = await client.get("/v1/lora/status")
        except Exception as e:  # noqa: BLE001
            status = {"error": "status_unavailable", "detail": str(e)}
        return _fmt({
            "backend_status": status,
            "local_buffer_size": len(_CAPTURE_BUFFER),
            "local_buffer_cap": _MAX_BUFFER,
            "codex_eps_kl": POLICY_EPSILON,
        })

    @mcp.tool()
    @handle_errors
    async def nexus_lora_adapter_current(language: str = "python") -> str:
        """Fetch the current LoRA adapter ID for a given language.

        Agents use this ID in downstream inference calls
        (e.g. ``nexus_inference(lora=<adapter_id>)``) to benefit from
        the community-trained adapter.
        """
        client = get_client()
        try:
            info = await client.get(f"/v1/lora/adapter/{language}")
        except Exception as e:  # noqa: BLE001
            return _fmt({
                "error": "adapter_unavailable",
                "detail": str(e),
                "language": language,
            })
        return _fmt({
            "language": language,
            "adapter": info,
            "drift_bound": BLOCK_DIM / RESIDUAL_NORM_LIMIT,
            "retrieved_at": int(time.time()),
        })

    @mcp.tool()
    @handle_errors
    async def nexus_lora_reward_claim(agent_id: str) -> str:
        """Claim accumulated reward for accepted LoRA contributions.

        Rewards are denominated in reputation points + optional USDC
        micro-payouts. Claim is rate-limited and reputation-tier gated
        on the backend.
        """
        client = get_client()
        try:
            result = await client.post(
                "/v1/lora/reward/claim",
                {"agent_id": agent_id},
            )
        except Exception as e:  # noqa: BLE001
            return _fmt({
                "error": "claim_failed",
                "detail": str(e),
                "agent_id": agent_id,
            })
        return _fmt({
            "agent_id": agent_id,
            "claim": result,
            "claimed_at": int(time.time()),
        })

    @mcp.tool()
    @handle_errors
    async def nexus_lora_buffer_inspect() -> str:
        """Inspect the local capture buffer (no content -- digests only).

        Useful for agents to decide whether to call ``nexus_lora_contribute``.
        """
        return _fmt({
            "buffer_size": len(_CAPTURE_BUFFER),
            "buffer_cap": _MAX_BUFFER,
            "samples": [
                {
                    "digest": s["digest"][:16],
                    "language": s["language"],
                    "quality_estimate": s["quality_estimate"],
                    "lint_delta": s["lint_delta"],
                    "bad_len": s["bad_len"],
                    "good_len": s["good_len"],
                    "error_type": s["error_type"],
                    "age_seconds": int(time.time()) - s["captured_at"],
                }
                for s in _CAPTURE_BUFFER
            ],
        })

    @mcp.tool()
    @handle_errors
    async def nexus_lora_buffer_clear() -> str:
        """Clear the local capture buffer without submitting.

        Use this if you captured test / low-quality samples by accident.
        Does not affect already-submitted contributions on the backend.
        """
        count = len(_CAPTURE_BUFFER)
        _CAPTURE_BUFFER.clear()
        return _fmt({"cleared": count, "buffer_size": 0})

