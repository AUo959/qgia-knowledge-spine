# Iran War Scenario Taxonomy

## Purpose

This document defines a canonical `scenario_id` taxonomy for Iran War 2026 assessments. It is intended for use across QGIA forecasting workflows, including probability ledgers, actor cards, QSFE scenario sets, ABCP updates, and runtime simulation contracts.

## Design Principles

- Scenario identifiers must be stable over time.
- IDs must be machine-readable and human-interpretable.
- Strategic, operational, and tactical layers must remain distinct.
- Mutually exclusive scenario sets should be explicitly labeled when intended for Dirichlet modeling.
- Binary event scenarios may coexist with multi-class regime or war-outcome scenarios.

## Naming Convention

Format: `[THEATER]_[LAYER]_[SCENARIO_NAME]`

Examples:
- `IRN_REGIME_H1_HARDLINE_SURVIVAL`
- `IRN_WAR_HORMUZ_CLOSURE_GE_60D`
- `IRN_MODE_PROXY_ESCALATION_SLOW_BURN`

### Prefix Rules

| Prefix | Meaning |
|---|---|
| `IRN` | Iran theater |
| `REGIME` | Internal political trajectory |
| `WAR` | Operational or strategic war outcome |
| `MODE` | Tactical or behavioral pathway |
| `ISR` | Israel actor |
| `US` | United States actor |

## Regime Trajectory Set

This set is intended to be treated as **mutually exclusive and collectively exhaustive** for 12-month trajectory modeling. Use Dirichlet priors when modeling this family.

| ID | Description |
|---|---|
| `IRN_REGIME_H1_HARDLINE_SURVIVAL` | Islamic Republic survives with hardline consolidation. Indicators: increased IRGC dominance, succession stabilization, high repression. |
| `IRN_REGIME_H2_MANAGED_TRANSITION` | Regime survives but undergoes controlled rebalancing or partial elite opening. |
| `IRN_REGIME_H3_REVOLUTIONARY_COLLAPSE` | Existing regime falls through revolutionary or quasi-revolutionary transition. |
| `IRN_REGIME_H4_FRAGMENTED_AUTHORITY` | No consolidated successor authority by end of forecast window; prolonged instability or regional fragmentation. |

## War Outcome Set (0–180 days)

These scenarios track major operational outcomes. Model as independent Beta/Bernoulli events unless explicitly grouped.

| ID | Description |
|---|---|
| `IRN_WAR_CEASEFIRE_0_60D` | Negotiated or de facto ceasefire within 0–60 days |
| `IRN_WAR_PROTRACTED_AIR_CAMPAIGN_60_180D` | Ongoing air/missile campaign without decisive settlement |
| `IRN_WAR_HORMUZ_CLOSURE_GE_60D` | Strait of Hormuz functionally closed ≥ 60 days |
| `IRN_WAR_CARRIER_COMBAT_LOSS` | Combat loss or incapacitation of a US/Allied carrier in theater |
| `IRN_WAR_REGION_WIDE_CONFLICT_GE_6_STATES` | Sustained strikes involving ≥ 6 regional states |
| `IRN_WAR_NUCLEAR_DECISION_WITHIN_12M` | Strategic decision to move from nuclear latency to active weaponization |

## Tactical / Modality Set

These IDs describe action pathways or behavioral modes for actor cards, RL environments, and scenario branching.

### Iran / IRGC Modes

| ID | Description |
|---|---|
| `IRN_MODE_NO_ESCALATION` | No active escalation |
| `IRN_MODE_PROXY_ESCALATION_SLOW_BURN` | Increased proxy use at sustainable tempo |
| `IRN_MODE_HORMUZ_HARASSMENT` | Recurrent harassment of shipping short of major losses |
| `IRN_MODE_HIGH_END_NAVAL_GAMBIT` | Attempted high-end naval strike (carrier or major warship) |
| `IRN_MODE_GULF_INFRASTRUCTURE_STRIKES` | Deliberate strikes on Gulf oil/gas infrastructure |

### Israel Modes

| ID | Description |
|---|---|
| `ISR_MODE_SUSTAINED_AIR_CAMPAIGN` | Continued frequent deep strikes on Iran |
| `ISR_MODE_DEEP_STRIKES_IRAN` | Focus on command, missile, and leadership nodes |
| `ISR_MODE_TACTICAL_PAUSE` | Operational pause to absorb pressure |
| `ISR_MODE_EARLY_CEASEFIRE_ACCEPTANCE` | Acceptance of a relatively early ceasefire window |

### U.S. Executive Modes

| ID | Description |
|---|---|
| `US_MODE_ESCALATE_RHETORIC` | Escalatory public signaling |
| `US_MODE_SIGNAL_CEASEFIRE` | Public or back-channel ceasefire signaling |
| `US_MODE_NAVAL_CONVOY_THREAT` | Threat or activation of naval convoy operations |
| `US_MODE_FORCE_POSTURE_ADJUST` | Material adjustment to force posture in theater |

## Modeling Guidance

### Dirichlet-Compatible Sets

Use Dirichlet priors only where the scenario family is explicitly defined as mutually exclusive and collectively exhaustive:
- Regime trajectory set (H1–H4)

### Beta-Compatible Events

Use separate Beta priors or equivalent Bernoulli event tracking for:
- `IRN_WAR_HORMUZ_CLOSURE_GE_60D`
- `IRN_WAR_CARRIER_COMBAT_LOSS`
- `IRN_WAR_NUCLEAR_DECISION_WITHIN_12M`
- `IRN_WAR_CEASEFIRE_0_60D`

### Update Thresholds

Log a scenario probability update when any of the following conditions hold:
- Absolute probability change ≥ 0.03
- A new observable materially changes the scenario tree
- An event changes status from hypothetical to active

## Versioning

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Status | Draft |
| Owner | QGIA Knowledge Spine |
| Review cycle | Event-driven during active conflict; monthly otherwise |
