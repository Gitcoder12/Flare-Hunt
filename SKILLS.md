# Flare-Hunt — Skills Index

Read `AGENTS.md` first, then select the matching workflow.

## `firms-product-ingestion`

Ingest and validate local NASA FIRMS VIIRS-style hotspot files while preserving product semantics and provenance. Use when adding fields, products, versions or metadata.

- Canonical: [`.agents/skills/firms-product-ingestion/SKILL.md`](.agents/skills/firms-product-ingestion/SKILL.md)
- Claude Code discovery: [`.claude/skills/firms-product-ingestion/SKILL.md`](.claude/skills/firms-product-ingestion/SKILL.md)

## `hotspot-spatiotemporal-analysis`

Develop and review hotspot clustering, geospatial calculations, event grouping and ranking. Use when changing radius, time windows, connected components, indexes or GeoJSON.

- Canonical: [`.agents/skills/hotspot-spatiotemporal-analysis/SKILL.md`](.agents/skills/hotspot-spatiotemporal-analysis/SKILL.md)
- Claude Code discovery: [`.claude/skills/hotspot-spatiotemporal-analysis/SKILL.md`](.claude/skills/hotspot-spatiotemporal-analysis/SKILL.md)

## `wildfire-historical-evaluation`

Design leakage-resistant historical evaluation for event clustering and future wildfire research. Use when defining ground truth, metrics, data splits or forecasting claims.

- Canonical: [`.agents/skills/wildfire-historical-evaluation/SKILL.md`](.agents/skills/wildfire-historical-evaluation/SKILL.md)
- Claude Code discovery: [`.claude/skills/wildfire-historical-evaluation/SKILL.md`](.claude/skills/wildfire-historical-evaluation/SKILL.md)


## Required workflow
Inspect product/source metadata, state the scientific task, preserve raw provenance, add regression fixtures, run exact tests and document limitations. Codex discovers `.agents/skills`; Claude Code discovers `.claude/skills`; other models should read this index and open canonical skill text.

## `multi-agent-review-handoff`

Coordinate satellite-product research, geospatial implementation and independent wildfire-evaluation review for Flare-Hunt. Use for ingestion, clustering, validation or forecasting work.

- Canonical: [`.agents/skills/multi-agent-review-handoff/SKILL.md`](.agents/skills/multi-agent-review-handoff/SKILL.md)
- Claude discovery: [`.claude/skills/multi-agent-review-handoff/SKILL.md`](.claude/skills/multi-agent-review-handoff/SKILL.md)
