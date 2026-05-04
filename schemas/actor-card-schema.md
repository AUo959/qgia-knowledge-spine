# Actor Card Schema

## Purpose

This schema standardizes how actor behavior is encoded for QGIA forecasting, scenario simulation, and runtime ingestion. The actor card is a compact representation of decision style, utility ordering, hard constraints, and trigger-dependent behavioral shifts.

## Required Fields

| Field | Type | Description |
|---|---|---|
| `actor_id` | string | Stable unique identifier |
| `display_name` | string | Human-readable actor name |
| `type` | string | Actor class (e.g. `state_executive`, `sub_state_military`, `non_state_armed`) |
| `decision_mode` | array[string] | Behavioral descriptors (e.g. `reactive`, `strategic`, `ideological`) |
| `utilities` | object | Named utility weights on a 1–5 ordinal scale |
| `risk_appetite` | string | Risk posture: `low`, `medium`, `medium_high`, `high` |
| `time_horizon` | array[string] | One or more of: `short`, `medium`, `long` |
| `info_inputs` | array[string] | Indicators the actor actually reacts to |
| `hard_constraints` | array[string] | Operational or political no-go conditions |
| `trigger_rules` | array[object] | Conditional probability update rules |

## Optional Fields

- `notes` — Free-text analytical context
- `source_context` — Source material references
- `validation_status` — `draft`, `reviewed`, `validated`
- `owner` — Maintaining analytical cell
- `updated_at` — ISO-8601 timestamp
- `related_scenarios` — Array of linked `scenario_id` values

## Utility Encoding

Utilities use ordinal weights from 1 to 5:

| Weight | Meaning |
|---|---|
| 1 | Low salience |
| 2 | Marginal consideration |
| 3 | Meaningful secondary objective |
| 4 | High-priority objective |
| 5 | Dominant / near-absolute objective |

Utility weights are relative within an actor card and are not globally comparable across actors.

## Trigger Rule Schema

Each entry in `trigger_rules` follows this structure:

```json
{
  "condition_id": "US_ANTI_WAR_MOBILIZATION",
  "if": {
    "indicator": "us_domestic_division",
    "operator": ">=",
    "threshold": 0.7
  },
  "then": {
    "increase_probabilities": {
      "scenario_ids": ["IRN_MODE_PROXY_ESCALATION_SLOW_BURN"],
      "delta": 0.05
    },
    "decrease_probabilities": {
      "scenario_ids": ["IRN_MODE_HIGH_END_NAVAL_GAMBIT"],
      "delta": 0.03
    }
  }
}
```

Supported operators: `>=`, `<=`, `>`, `<`, `==`

## Validation Rules

- `actor_id` must be unique within a package.
- `utilities` must contain at least three named entries.
- Utility values must be integers from 1 to 5.
- `delta` values in trigger rules should normally fall between 0.01 and 0.15.
- Trigger rules must reference `scenario_id` values defined in the canonical scenario taxonomy.
- `hard_constraints` should be phrased as explicit operational prohibitions or escalation boundaries.

## Minimal Valid Example

```json
{
  "actor_id": "IRGC_QF",
  "display_name": "IRGC-Qods Force / IRGC High Command",
  "type": "sub_state_military",
  "decision_mode": ["reactive", "ideological"],
  "utilities": {
    "regime_survival": 5,
    "deterrent_image": 4,
    "regional_influence": 4,
    "economic_stability": 2,
    "ideological_mission": 3
  },
  "risk_appetite": "medium_high",
  "time_horizon": ["medium"],
  "info_inputs": [
    "us_domestic_division",
    "regional_ally_signals",
    "irgc_casualty_index"
  ],
  "hard_constraints": [
    "avoid_first_strike_carrier_kill_unless_regime_survival_at_risk"
  ],
  "trigger_rules": []
}
```

## Versioning

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Status | Draft |
| Owner | QGIA Knowledge Spine |
| Review cycle | Quarterly or on schema revision |
