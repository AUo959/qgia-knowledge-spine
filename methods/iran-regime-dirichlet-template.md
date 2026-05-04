# Iran Regime Trajectory — Dirichlet Template

## Purpose

This template defines a four-scenario Dirichlet structure for 12-month Iran regime trajectory forecasting. It is designed to be used as an initializable prior within ABCP and QSFE, updatable as new OSINT or SIGINT evidence arrives.

## Scenario Set

This family is mutually exclusive and collectively exhaustive:

| ID | Label |
|---|---|
| `IRN_REGIME_H1_HARDLINE_SURVIVAL` | Hardline survival |
| `IRN_REGIME_H2_MANAGED_TRANSITION` | Managed internal transition |
| `IRN_REGIME_H3_REVOLUTIONARY_COLLAPSE` | Revolutionary collapse |
| `IRN_REGIME_H4_FRAGMENTED_AUTHORITY` | Fragmented authority |

## Initial Prior

Choose a Dirichlet prior with moderate total mass (α₀ = 9.0) to allow rapid posterior movement under conflict conditions:

| Scenario | α | E[p] |
|---|---:|---:|
| H1 — Hardline survival | 4.0 | 0.444 |
| H2 — Managed transition | 2.0 | 0.222 |
| H3 — Revolutionary collapse | 1.8 | 0.200 |
| H4 — Fragmented authority | 1.2 | 0.133 |
| **Total** | **9.0** | **1.000** |

Note: `E[p]` values are rounded to three decimals for readability, so displayed row values may not sum to `1.000` exactly.

## Update Logic

### Conditions favoring H1 (increase α₁)
- IRGC remains cohesive; no observable factional splits
- Mojtaba succession track stabilizes
- Repression successfully contains protests
- Wartime nationalism reinforces regime legitimacy

### Conditions favoring H3 (increase α₃)
- Sustained nationwide unrest exceeding 2026-04 baseline
- Observable elite fragmentation or defections
- Coercive organs exhibit internal non-compliance
- IRGC suffers severe casualties undermining institutional cohesion

### Conditions favoring H4 (increase α₄)
- No faction achieves national consolidation
- Regional warlordism or de facto territorial fragmentation
- Collapse of central government services and authority signals

### Conditions favoring H2 (increase α₂)
- Visible intra-elite negotiation or power-sharing signals
- Partial diplomatic opening or ceasefire acceptance
- Clerical coalition shifts away from full hardline position

## Implementation Notes

- Initialize as `Dir(4.0, 2.0, 1.8, 1.2)`
- Recompute posterior means after each substantive OSINT update
- Log updated α vector with timestamp to the probability ledger
- Flag when any single scenario accumulates > 0.70 posterior mass (concentrated outcome)
- Flag when H3 + H4 combined exceed 0.45 (elevated instability signal)

## Versioning

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Status | Draft |
| Owner | QGIA Knowledge Spine — Middle East Cell |
| Review cycle | Event-driven during active conflict |
