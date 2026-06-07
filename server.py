#!/usr/bin/env python3
"""
Buy Pro: https://www.csoai.org/checkout

MEOK EU AI Act Article 13 Instructions for Use Generator MCP
==============================================================

By MEOK AI Labs · https://meok.ai · MIT
<!-- mcp-name: io.github.CSOAI-ORG/meok-eu-ai-act-art-13-ifu-mcp -->

WHAT THIS DOES
--------------
EU AI Act Article 13 requires PROVIDERS of high-risk AI systems to supply
deployers with Instructions for Use (IFU). Article 13(3) lists 7 mandatory
content elements:

  (a) identity + contact details of provider + authorised representative
  (b) characteristics, capabilities + limitations of performance
  (c) any changes to the high-risk AI system + its performance pre-determined
  (d) human-oversight measures referenced in Article 14
  (e) computational + hardware resources needed + expected lifetime + maintenance
  (f) where relevant, mechanisms allowing deployers to collect, store + interpret logs
  (g) any other information relevant to using the system as intended

This MCP auto-generates a structured Article 13 IFU document, validates
completeness, signs it for audit, and crosswalks to the deployer's FRIA
inputs (meok-eu-ai-act-art-26-fria-mcp).

PROVIDER-SIDE companion to FRIA (DEPLOYER-side). Every high-risk AI vendor
shipping into EU markets needs this before market placement.

TOOLS
-----
- generate_ifu(provider_legal_name, system_name, capabilities, ...)
- check_ifu_completeness(ifu_doc)
- list_art_13_3_elements()
- crosswalk_to_fria(ifu_doc) → fields the deployer can lift directly
- generate_human_oversight_section(oversight_design)
- sign_ifu_chain(ifu_doc, signer_role)

PRICING
-------
Free MIT self-host · £29/mo Starter · £79/mo Pro · Governance Substrate £499/mo.
"""

from __future__ import annotations
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from typing import Optional
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("meok-eu-ai-act-art-13-ifu")
_HMAC_SECRET = os.environ.get("MEOK_HMAC_SECRET", "")


# Article 13(3) — 7 mandatory IFU content elements
ART_13_3_ELEMENTS = [
    ("a_provider_identity", "Identity + contact details of provider + authorised representative"),
    ("b_characteristics", "Characteristics, capabilities, limitations of performance"),
    ("c_changes_predetermined", "Any pre-determined changes to the system + its performance"),
    ("d_human_oversight", "Human-oversight measures (Article 14)"),
    ("e_compute_lifecycle", "Compute + hardware resources, expected lifetime, maintenance"),
    ("f_log_mechanisms", "Mechanisms allowing deployers to collect, store + interpret logs"),
    ("g_other_relevant", "Any other relevant info for intended use"),
]

# Article 14 human oversight measures
ART_14_OVERSIGHT_MEASURES = [
    "human_in_loop",            # human approves every output
    "human_on_loop",            # human monitors, can intervene
    "human_in_command",         # high-level go/no-go
    "stop_button",              # hard-stop control
    "output_review",            # post-hoc output review
    "bias_monitoring",          # ongoing bias-metric monitoring
    "drift_detection",          # data/model drift triggers
    "appeals_mechanism",        # affected person can challenge output
]


def _sign(payload: dict) -> str:
    if not _HMAC_SECRET:
        return "unsigned-no-key-configured"
    return hmac.new(_HMAC_SECRET.encode(), json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def generate_ifu(
    provider_legal_name: str,
    provider_contact: str,
    system_name: str,
    system_version: str,
    intended_purpose: str,
    capabilities: list[str],
    limitations: list[str],
    accuracy_metrics: dict,
    human_oversight_design: str,
    pre_determined_changes: Optional[list[str]] = None,
    compute_requirements: Optional[dict] = None,
    expected_lifetime_months: int = 24,
    log_mechanisms: Optional[list[str]] = None,
    authorised_representative: Optional[str] = None,
) -> dict:
    """
    Generate a full Article 13 IFU document.

    Args:
        provider_legal_name: Legal entity name of the provider.
        provider_contact: Contact email + address.
        system_name: Name of the AI system.
        system_version: Semver of the AI system.
        intended_purpose: Article 3(12) intended-purpose statement.
        capabilities: List of system capabilities.
        limitations: List of known limitations / failure modes.
        accuracy_metrics: Dict of accuracy/precision/recall/F1 etc.
        human_oversight_design: Description of Art 14 measures.
        pre_determined_changes: Optional list of pre-cleared system changes.
        compute_requirements: Dict of {cpu_cores, gpu_class, ram_gb, disk_gb}.
        expected_lifetime_months: Expected operational lifetime.
        log_mechanisms: How deployers can collect + interpret system logs.
        authorised_representative: Required if provider outside EU.

    Returns:
        {ifu_document, completeness_score, signature}
    """
    if compute_requirements is None:
        compute_requirements = {"cpu_cores": 4, "ram_gb": 16, "disk_gb": 50, "gpu_class": "optional"}
    if log_mechanisms is None:
        log_mechanisms = [
            "JSON-lines structured logs to provider-supplied collector",
            "stdout + stderr capture",
            "OpenTelemetry tracing endpoint",
        ]
    if pre_determined_changes is None:
        pre_determined_changes = []

    ifu_doc = {
        "spec": "EU_AI_ACT_ART_13_3",
        "spec_version": "Regulation (EU) 2024/1689",
        "system_name": system_name,
        "system_version": system_version,
        "issued_at": _ts(),
        # 7 mandatory Article 13(3) elements
        "art_13_3_elements": {
            "a_provider_identity": {
                "provider_legal_name": provider_legal_name,
                "provider_contact": provider_contact,
                "authorised_representative": authorised_representative or "N/A — provider established in EU",
            },
            "b_characteristics": {
                "intended_purpose": intended_purpose,
                "capabilities": capabilities,
                "limitations": limitations,
                "accuracy_metrics": accuracy_metrics,
            },
            "c_changes_predetermined": pre_determined_changes,
            "d_human_oversight": {
                "design_summary": human_oversight_design,
                "references": "Article 14 + Annex IV section 2(e)",
            },
            "e_compute_lifecycle": {
                "compute_requirements": compute_requirements,
                "expected_lifetime_months": expected_lifetime_months,
                "maintenance_terms": "Provider supports patch + security maintenance for full lifetime; deployer notified 6 months ahead of EOL.",
            },
            "f_log_mechanisms": log_mechanisms,
            "g_other_relevant": "See provider's website for technical documentation + Article 11 + Annex IV docs.",
        },
    }
    ifu_doc["signature"] = _sign(ifu_doc)

    # Completeness score
    score = 100
    if not capabilities:
        score -= 15
    if not limitations:
        score -= 15
    if not accuracy_metrics:
        score -= 10
    if not human_oversight_design:
        score -= 15
    if expected_lifetime_months < 12:
        score -= 5
    score = max(0, score)

    return {
        "ifu_document": ifu_doc,
        "completeness_score": score,
        "signature": ifu_doc["signature"],
        "next_step": (
            "Distribute IFU with the system. Deployer reads + uses as input to FRIA (Art 26(9) via meok-eu-ai-act-art-26-fria-mcp)."
            if score >= 80
            else "Fix missing fields before distributing."
        ),
    }


@mcp.tool()
def check_ifu_completeness(ifu_doc: dict) -> dict:
    """
    Validate an IFU has all 7 Article 13(3) elements.

    Args:
        ifu_doc: An IFU document from generate_ifu().

    Returns:
        {complete, missing, present}
    """
    elements = ifu_doc.get("art_13_3_elements", {})
    expected_keys = {k for k, _ in ART_13_3_ELEMENTS}
    # Presence = key exists (even if value is empty list — empty pre-determined-changes is valid)
    present = sorted(k for k in expected_keys if k in elements)
    missing = sorted(expected_keys - set(present))
    return {
        "complete": len(missing) == 0,
        "present": present,
        "missing": missing,
        "art_13_3_total": len(expected_keys),
    }


@mcp.tool()
def list_art_13_3_elements() -> dict:
    """Return the 7 mandatory Article 13(3) IFU content elements."""
    return {
        "spec": "EU_AI_ACT_ART_13_3",
        "elements": [{"key": k, "description": d} for k, d in ART_13_3_ELEMENTS],
        "count": len(ART_13_3_ELEMENTS),
    }


@mcp.tool()
def list_art_14_oversight_measures() -> dict:
    """Return the catalogue of Article 14 human-oversight measure types."""
    return {
        "spec": "EU_AI_ACT_ART_14",
        "measures": ART_14_OVERSIGHT_MEASURES,
        "count": len(ART_14_OVERSIGHT_MEASURES),
    }


@mcp.tool()
def crosswalk_to_fria(ifu_doc: dict) -> dict:
    """
    Extract fields a deployer can lift directly into their FRIA (Art 26(9)).

    Args:
        ifu_doc: An IFU document.

    Returns:
        {fria_input_fields}
    """
    el = ifu_doc.get("art_13_3_elements", {})
    return {
        "fria_input_fields": {
            "g_provider_ifu_reference": f"{ifu_doc.get('system_name')} IFU v{ifu_doc.get('system_version')} ({ifu_doc.get('issued_at')})",
            "e_human_oversight": el.get("d_human_oversight", {}).get("design_summary"),
            "d_specific_risks_seed": el.get("b_characteristics", {}).get("limitations"),
            "b_period_frequency_seed": f"Expected lifetime {el.get('e_compute_lifecycle', {}).get('expected_lifetime_months')} months — deployer specifies frequency",
        },
        "hint": "These fields prefill the deployer's FRIA via meok-eu-ai-act-art-26-fria-mcp. Saves 30-50% of FRIA drafting time.",
    }


@mcp.tool()
def generate_human_oversight_section(
    oversight_design_type: str,
    operator_qualification: str = "Trained AI Officer",
    stop_button_location: str = "Provider-supplied admin console",
    appeals_endpoint: Optional[str] = None,
) -> dict:
    """
    Build a structured Article 14 human-oversight design block.

    Args:
        oversight_design_type: One of human_in_loop / human_on_loop / human_in_command.
        operator_qualification: Required qualification for the human operator.
        stop_button_location: Where the deployer can hard-stop the system.
        appeals_endpoint: Optional endpoint for affected-person appeals (Art 27(1)(i)).

    Returns:
        {oversight_block}
    """
    valid = {"human_in_loop", "human_on_loop", "human_in_command"}
    if oversight_design_type not in valid:
        return {"error": f"Use one of {valid}"}
    return {
        "oversight_block": {
            "design_type": oversight_design_type,
            "operator_qualification": operator_qualification,
            "stop_button_location": stop_button_location,
            "appeals_endpoint": appeals_endpoint or "appeals@<deployer-domain>",
            "training_required": True,
            "performance_reviews_per_year": 2,
        },
    }


@mcp.tool()
def sign_ifu_chain(ifu_doc: dict, signer_role: str = "provider_compliance_officer") -> dict:
    """HMAC-sign the IFU + emit a publishable audit attestation."""
    att_id = f"IFU_{int(time.time())}_{os.urandom(4).hex()}"
    sealed = {
        "attestation_id": att_id,
        "spec": "EU_AI_ACT_ART_13_3",
        "signer_role": signer_role,
        "ifu_doc": ifu_doc,
        "sealed_at": _ts(),
        "issuer": "MEOK AI Labs (CSOAI LTD)",
    }
    sig = _sign(sealed)
    return {
        "attestation_id": att_id,
        "signature": sig,
        "sealed_at": sealed["sealed_at"],
        "verify_url": f"https://meok-attestation-api.vercel.app/verify/{att_id}",
        "retention_hint": "Retain IFU + signature for the entire system lifetime + 6 years (Art 18).",
    }


if __name__ == "__main__":
    mcp.run()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
