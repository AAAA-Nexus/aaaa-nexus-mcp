"""Compliance tools — EU AI Act, NIST, fairness, audit, drift, incidents."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_check(system_description: str) -> str:
        """Run EU AI Act / NIST AI RMF / ISO 42001 compliance check (CMP-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/compliance/check", {"system_description": system_description}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_eu_ai_act(system_description: str) -> str:
        """Generate EU AI Act Annex IV conformity certificate. $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/compliance/eu-ai-act", {"system_description": system_description}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_fairness(dataset_description: str) -> str:
        """Calculate disparate impact ratio for fairness proof (FNS-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/compliance/fairness", {"dataset_description": dataset_description}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_explain(output: str, input_features: dict[str, Any]) -> str:
        """Generate GDPR Art.22 explainability certificate (XPL-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/compliance/explain", {"output": output, "input_features": input_features}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_lineage(dataset_stages: list[dict[str, Any]]) -> str:
        """Build SHA-256 hash chain across dataset pipeline stages (LIN-100). $0.040/call."""
        return _fmt(
            await get_client().post("/v1/compliance/lineage", {"dataset_stages": dataset_stages})
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_oversight(reviewer: str, decision: str) -> str:
        """Record a human-in-the-loop review attestation (OVS-100). $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/compliance/oversight", {"reviewer": reviewer, "decision": decision}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_incident(
        system_id: str, description: str, severity: str = "medium"
    ) -> str:
        """File EU AI Act Art.73 incident report (INC-100). $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/compliance/incident",
                {"system_id": system_id, "description": description, "severity": severity},
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_compliance_transparency(system_id: str, period: str) -> str:
        """Generate quarterly transparency report (TRP-100). $0.080/call."""
        return _fmt(
            await get_client().post(
                "/v1/compliance/transparency", {"system_id": system_id, "period": period}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_audit_log(event: dict[str, Any]) -> str:
        """Append to tamper-evident audit trail (GOV-103). $0.040/call."""
        return _fmt(await get_client().post("/v1/audit/log", {"event": event}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_audit_verify() -> str:
        """Verify integrity of the audit trail. $0.040/call."""
        return _fmt(await get_client().post("/v1/audit/verify", {}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_aibom_drift(model_id: str) -> str:
        """Check AIBOM lineage for runtime drift (AIB-401). $0.040/call."""
        return _fmt(await get_client().post("/v1/aibom/drift", {"model_id": model_id}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_drift_check(
        model_id: str,
        reference_data: dict[str, Any] | None = None,
        current_data: dict[str, Any] | None = None,
    ) -> str:
        """PSI-based drift detection (DRG-100). Returns drift score with 0.20 threshold. $0.010/call."""
        return _fmt(
            await get_client().post(
                "/v1/drift/check",
                {
                    "model_id": model_id,
                    "reference_data": reference_data or {},
                    "current_data": current_data or {},
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_drift_certificate(check_id: str) -> str:
        """Get signed drift compliance certificate (DRG-101). $0.010/call."""
        return _fmt(await get_client().get("/v1/drift/certificate", check_id=check_id))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_ethics_compliance(system_description: str) -> str:
        """Prime Axiom audit with formal proof of safety. $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/ethics/compliance", {"system_description": system_description}
            )
        )
