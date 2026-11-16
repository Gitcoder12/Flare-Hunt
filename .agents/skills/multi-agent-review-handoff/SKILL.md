---
name: multi-agent-review-handoff
description: Coordinate satellite-product research, geospatial implementation and independent wildfire-evaluation review for Flare-Hunt. Use for ingestion, clustering, validation or forecasting work.
---

# Multi-Agent Review Handoff — Flare-Hunt

## Roles
- **Remote-sensing research lead (for example, Claude):** verify product field semantics, sensor/platform/version, acquisition-time conventions and authoritative data references. For forecasting research, define independent ground truth and the prediction target.
- **Implementation engineer (for example, ChatGPT/Codex):** implement ingestion, clustering, mapping or evaluation behind tested interfaces; preserve raw source fields and rejected records.
- **Independent reviewer (for example, DeepSeek):** inspect the diff read-only. Challenge confidence misinterpretation, UTC mistakes, geospatial edge cases, event leakage, unsupported performance claims and unsafe warning language.
- **Verifier:** run tests, validate coordinates/timestamps, compare optimized clustering with a reference implementation and inspect GeoJSON/report outputs.
- **Human maintainer:** approves dataset selection, live API access, operational integrations and any public-facing safety claim.

## Handoff contract
Every dataset proposal must specify source URL, product/platform, version/processing level, acquisition and download time, licence/terms, geography, temporal coverage, native confidence meaning and known quality caveats.

Every evaluation proposal must define the target (pixel detection, event association, ignition forecasting or spread forecasting), independent ground truth, matching rule, split strategy, baseline and metrics.

## Parallel-work rules
- One writer per ingestion/schema/algorithm file at a time.
- Researcher establishes semantics before code defaults or thresholds change.
- Reviewer works read-only on a pinned commit.
- Keep event-level splits together; never random-split rows from one fire event across train/test.
- Resolve disagreements using product documentation, geospatial calculations and reproducible tests.

## Release gate
Report product metadata, provenance, rejected rows, spatial/time assumptions, test results, held-out evaluation and residual uncertainty. Satellite hotspots are not confirmed fires; no agent may turn analyst rankings into evacuation, dispatch or public emergency advice.
