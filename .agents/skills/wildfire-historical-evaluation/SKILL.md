---
name: wildfire-historical-evaluation
description: Design leakage-resistant historical evaluation for event clustering and future wildfire research. Use when defining ground truth, metrics, data splits or forecasting claims.
---

# wildfire-historical-evaluation

## Separate scientific tasks
1. Satellite hotspot detection.
2. Event association/grouping.
3. Future fire-occurrence forecasting.
4. Spread forecasting for an existing fire.

Never report one task's score as evidence for another.

## Ground truth
Use independently documented incident records, fire perimeters or authoritative event datasets with provenance, temporal/geographic coverage and known reporting limitations. A hotspot feed is not its own ground truth.

## Leakage-resistant splits
- Prefer temporal and/or geographic holdouts.
- Keep every observation from one incident/event in a single split.
- Avoid random row-level splits that put nearby detections from one event into both train and test.
- Record data versions, download dates, preprocessing, matching rules and seeds.
- Inspect label delay and satellite revisit time.

## Metrics
At pixel level, report precision, recall and false-positive rate only with suitable labels. At event level, report event precision/recall, false alarms per area/time, detection delay and explicit event-matching criteria. Report uncertainty and denominators.

## Baselines
Use simple transparent baselines such as raw hotspot counts and fixed spatial-temporal grouping. A learned model must outperform a meaningful baseline on held-out data.

No public warning, evacuation advice or operational dispatch use without domain-expert validation, calibrated uncertainty, local authority governance and a dedicated safety case.
