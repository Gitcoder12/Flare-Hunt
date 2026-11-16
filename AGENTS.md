# Flare-Hunt — Agent Engineering Contract

## Mission
An offline geospatial tool that clusters and ranks candidate satellite fire-hotspot records for analyst review. It does not confirm fires, predict spread or issue emergency warnings.

## Codebase map
`flare_hunt.py` parses a VIIRS-style local CSV, validates records, clusters with haversine distance and time windows, and writes JSON. `examples/synthetic_hotspots.csv` is explicitly synthetic. `tests/test_flare_hunt.py` covers parser and clustering behavior.

## Before every task
1. Read this file, `SKILLS.md`, `PROJECT_STATUS.md` and the relevant skill.
2. Inspect current branch and data product; do not assume every CSV is the same product.
3. Trace ingestion, validation, clustering, ranking and report output.
4. State the scientific task being solved and the available ground truth.
5. Make the smallest testable change.

## Non-negotiable invariants
- Hotspots are satellite detections, not confirmed ground fires or individual fire-event ground truth.
- Acquisition date/time is satellite overpass observation time in UTC; it is not necessarily fire start time or data publication time.
- Preserve product, satellite, version, native confidence semantics, source row and FRP unit; never invent confidence thresholds.
- Current input is a documented local CSV subset. Do not imply live FIRMS API ingestion exists.
- Current clustering uses pairwise connected components; chaining can make cluster diameter exceed the configured pairwise radius.
- Current O(n²) pair loop is bounded by MAX_INPUT_ROWS; do not raise the cap without measured algorithmic change.
- No emergency, dispatch, fire-spread or damage-risk claims without validated ground truth and dedicated safety review.

## Verification commands
- `python -m unittest discover -s tests -v`
- `python -m py_compile flare_hunt.py tests/test_flare_hunt.py`
- `python flare_hunt.py --help`
- `python flare_hunt.py examples/synthetic_hotspots.csv --output /tmp/flare-report.json`

Tests must cover date-line and high-latitude cases before geospatial edge handling is claimed. Inspect output and preserve source provenance. If a command cannot run, mark it not run.

## Engineering standards
Keep timestamps timezone-aware; validate coordinates, dates and finite numbers; avoid fabricated fields; retain rejected source rows; guard output overwrite; keep data ingestion separate from analytics. Minimize dependencies and justify any geospatial stack addition by accuracy, licensing and reproducibility.

## Documentation and safety
Update README and PROJECT_STATUS when product support changes. Clearly separate synthetic fixtures, real source data, observed hotspots and inferred fire events. Never present experimental output as public warning or evacuation advice.

## Handoff and permissions
Report files changed, commands and actual results, checks not run, source/product versions, data assumptions, residual risks and manual review steps. Do not edit main or merge without explicit authorization.

## Skills
Canonical instructions live under `.agents/skills/`; Claude discovery entries under `.claude/skills/`. See `SKILLS.md`.