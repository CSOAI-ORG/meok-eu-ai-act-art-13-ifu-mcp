# MEOK EU AI Act Article 13 IFU Generator MCP

> ## 🧱 Part of the MEOK Governance Substrate (£499/mo)
> See [meok.ai/governance](https://meok.ai/governance).

# Generate Instructions for Use per Article 13(3) — provider-side compliance

<!-- mcp-name: io.github.CSOAI-ORG/meok-eu-ai-act-art-13-ifu-mcp -->

[![PyPI](https://img.shields.io/pypi/v/meok-eu-ai-act-art-13-ifu-mcp)](https://pypi.org/project/meok-eu-ai-act-art-13-ifu-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What this does

**EU AI Act Article 13(3)** requires providers of high-risk AI systems to supply deployers with **Instructions for Use** containing **7 mandatory content elements** before market placement.

Companion to **meok-eu-ai-act-art-26-fria-mcp** (deployer-side FRIA). Together they cover both sides of the EU AI Act provider/deployer split.

## Tools

| Tool | Purpose |
|---|---|
| `generate_ifu(provider_legal_name, system_name, capabilities, ...)` | Full IFU with 7 Article 13(3) elements |
| `check_ifu_completeness(ifu_doc)` | Validate IFU has all 7 elements |
| `list_art_13_3_elements()` | The 7 mandatory elements |
| `list_art_14_oversight_measures()` | 8 Article 14 human-oversight types |
| `crosswalk_to_fria(ifu_doc)` | Extract fields a deployer can lift into their FRIA |
| `generate_human_oversight_section(oversight_design_type, ...)` | Article 14 oversight block |
| `sign_ifu_chain(ifu_doc, signer_role)` | HMAC-signed audit attestation |

## The 7 mandatory Article 13(3) elements

(a) provider identity + authorised representative · (b) characteristics, capabilities + limitations · (c) pre-determined changes · (d) human-oversight measures (Article 14) · (e) compute requirements + expected lifetime + maintenance · (f) log collection mechanisms · (g) other relevant info.

## Why this exists

Today providers either (1) ship marketing PDF as "IFU" and fail conformity audit, or (2) pay a regulatory consultant £15K-£60K to draft one manually. This MCP produces an auditor-defensible IFU in seconds. Deployer can then lift fields directly into their FRIA — **30-50% drafting time saved across the provider/deployer pair**.

## Sister MCPs

- `meok-eu-ai-act-art-26-fria-mcp` — deployer-side FRIA (consumes this IFU)
- `eu-ai-act-compliance-mcp` — 410 articles + Annex III classifier
- `ai-bom-mcp` — Annex IV technical documentation
- `agent-incident-relay-mcp` — Article 73 5-clock broadcaster

Full catalogue: [meok.ai/anthropic-registry](https://meok.ai/anthropic-registry)

## Pricing

| Option | Price |
|---|---|
| Self-host MIT | £0 |
| Universal PAYG | £29/mo + £0.0002/call |
| Governance Substrate | £499/mo |
| A2A Substrate | £999/mo |
| Defence | £4,990/mo |

Buy: https://meok.ai/governance

## Wire it up — full stack

Pair this with the MEOK chain:

1. **meok-eu-ai-act-art-13-ifu-mcp** — provider ships IFU
2. **meok-eu-ai-act-art-26-fria-mcp** — deployer drafts FRIA (lifts IFU fields)
3. **agent-policy-enforcement-mcp** — gate on FRIA-approved actions
4. **agent-audit-logger-mcp** — chain-of-custody log
5. **a2a-governance-bridge-mcp** — fold all attestations
6. **agent-incident-relay-mcp** — broadcast Article 73 incidents to 5 regimes

See [meok.ai/mcp-stack](https://meok.ai/mcp-stack) for architecture and [meok.ai/mcp-stack/demo](https://meok.ai/mcp-stack/demo) for the live demo.

## Licence

MIT. By [MEOK AI Labs](https://meok.ai) (CSOAI LTD, UK Companies House 16939677).
