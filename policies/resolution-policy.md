# QGIA Spine Resolution Policy

## Status

Bootstrap policy for the QGIA closed-loop contract adoption in
`qgia-knowledge-spine`.

This policy defines the semantics for outcome adjudication. Outcome records are
expected to be created in the sibling `qgia-knowledge-library` repo against this
policy surface.

## Scope

This policy governs:

- how binary forecast questions are resolved
- what counts as sufficient linked evidence
- when an outcome must remain ambiguous
- how resolution changes are versioned

It does not define source collection tradecraft or corpus promotion rules.

## Outcome States

- `occurred`: the forecasted event happened within the declared resolution window
- `did_not_occur`: the event did not happen within the declared resolution window
- `ambiguous`: available evidence does not support a stable binary adjudication
- `partial`: the event occurred only in a materially narrower form than the forecast question asserted

## Evidence Hierarchy

Outcome adjudication should prefer:

1. directly linked primary evidence with provenance
2. multiple independent corroborating records
3. explicit time-bounded evidence inside the forecast resolution window
4. resolved contradictions documented in the outcome record basis summary

Single-source resolution is allowed only when the source has unusually strong
provenance and no substantial contradictory evidence is known.

## Binary Resolution Rules

- Resolution must reference the originating `forecast_id`
- Resolution must include the evidence refs used for adjudication
- If the forecast horizon expires without sufficient positive evidence, resolve
  as `did_not_occur` only when the absence is decision-relevant and not merely
  an observation gap
- If ambiguity remains material, use `ambiguous` rather than forcing a binary outcome

## Ambiguity Handling

Use `ambiguous` when:

- the forecast question was underspecified
- key evidence is contradictory and unresolved
- the event boundary is contested
- the observation window closed without enough visibility to justify a binary call

Ambiguous outcomes should be excluded from Brier scoring unless a later explicit
policy revision narrows the handling rule.

## Change Discipline

- Do not overwrite an existing outcome adjudication in place
- Any changed adjudication requires a new outcome record or explicit superseding record
- Prior rebasing and calibration updates must reference the outcome records they used
- Curated corpus updates may summarize resolved lessons, but they may not replace the machine-readable outcome lineage

