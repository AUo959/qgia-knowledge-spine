# Probability Ledger Schema

## Purpose

The probability ledger is the canonical event log for forecasted scenarios, baseline priors, posterior updates, confidence metrics, and change tracking across QGIA assessments.

## Core Columns

| Column | Type | Description |
|---|---|---|
| `timestamp` | ISO-8601 string | Update timestamp |
| `theater` | string | Theater name (e.g. `Iran`) |
| `scenario_id` | string | Canonical scenario identifier |
| `scenario_label` | string | Human-readable scenario name |
| `window` | string | Forecast horizon (e.g. `0-60d`, `0-180d`, `12m`) |
| `probability` | float | Current probability, 0.00–1.00 |
| `previous_probability` | float | Previous logged value |
| `delta_probability` | float | Change since prior logged value |
| `distribution_type` | string | `beta`, `dirichlet_component`, `hazard`, `bernoulli` |
| `distribution_params` | string/json | Serialized parameter block |
| `confidence_band` | float | Analyst-composite confidence, 0.00–1.00 |
| `data_quality` | float | Data quality component score |
| `source_reliability` | float | Source reliability component score |
| `methodological_rigor` | float | Methodological rigor component score |
| `temporal_stability` | float | Temporal stability component score |
| `quantum_coherence` | float | Inter-model coherence score |
| `notes` | text | Update rationale or driving observation |

## Event Types

### Binary Event Rows

Used for individual probability tracking of scenarios such as:
- `IRN_WAR_HORMUZ_CLOSURE_GE_60D`
- `IRN_WAR_CARRIER_COMBAT_LOSS`
- `IRN_WAR_NUCLEAR_DECISION_WITHIN_12M`

Set `distribution_type` to `bernoulli` or `beta`.

### Multi-Class Rows

Used for Dirichlet-family scenario sets where rows share a forecast window and must sum to 1.0:
- `IRN_REGIME_H1_HARDLINE_SURVIVAL`
- `IRN_REGIME_H2_MANAGED_TRANSITION`
- `IRN_REGIME_H3_REVOLUTIONARY_COLLAPSE`
- `IRN_REGIME_H4_FRAGMENTED_AUTHORITY`

Set `distribution_type` to `dirichlet_component`.

## Update Rules

Log a new row when any of the following conditions hold:
- Absolute delta ≥ 0.03
- A scenario changes active/inactive status
- A major exogenous shock alters the model state
- A forecast window rolls into a new temporal phase

## Confidence Components

Composite confidence is derived from the geometric mean:

```
C_composite = (DQ × SR × MR × TS)^(1/4) × Coherence
```

Where:
- `DQ` = Data Quality
- `SR` = Source Reliability
- `MR` = Methodological Rigor
- `TS` = Temporal Stability
- `Coherence` = Quantum Coherence (inter-model agreement)

All components are scored 0.00–1.00.

## Minimal CSV Example

```csv
timestamp,theater,scenario_id,scenario_label,window,probability,previous_probability,delta_probability,distribution_type,confidence_band,notes
2026-04-19T00:00:00Z,Iran,IRN_WAR_HORMUZ_CLOSURE_GE_60D,Hormuz closure >= 60 days,0-180d,0.37,0.31,0.06,beta,0.72,Closure sustained via attack risk and insurance shock
```

## Brier Score Integration

Once resolved events are observable, compute Brier scores against ledger entries:

| Range | Quality |
|---|---|
| BS < 0.10 | Excellent |
| BS 0.10–0.15 | Good |
| BS 0.15–0.20 | Acceptable |
| BS > 0.25 | Requires recalibration |

QGIA benchmark: BS ≈ 0.089 at 12-month horizon.

## Versioning

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Status | Draft |
| Owner | QGIA Knowledge Spine |
| Review cycle | Event-driven; append-only log |
