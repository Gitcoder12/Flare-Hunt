# Flare-Hunt

Detect and rank candidate satellite fire-hotspot clusters for analyst review.

Flare-Hunt currently analyzes a **local NASA FIRMS VIIRS-style CSV**. It groups nearby detections observed within a configured time window and ranks clusters using hotspot count, summed fire-radiative power (FRP), high-confidence detection count and observation time.

## Important scope boundary

A satellite hotspot is not a confirmed ground fire and is not a prediction that a fire will spread. Satellite acquisition time is the overpass observation time in UTC; it is not necessarily when a fire started or when the data became available. Flare-Hunt is an offline analysis tool, not an emergency-warning or dispatch service.

## MVP features

- Parse a documented subset of NASA FIRMS VIIRS CSV fields: latitude, longitude, acquisition date/time, FRP, confidence, satellite, version and day/night.
- Validate coordinates, timestamps, confidence values and non-negative FRP.
- Preserve rejected rows with their original source row and reason.
- Cluster hotspots with a configurable spatial radius and time window.
- Rank clusters transparently; no hidden ML model or calibrated risk score is claimed.
- Write a JSON report without modifying the source CSV.
- Use a row limit (5,000) to bound the pairwise clustering cost.

## Requirements

- Python 3.10 or later
- Standard library only

## Run

```bash
python flare_hunt.py path/to/firms_viirs.csv \
  --radius-km 1.0 \
  --time-window-hours 24 \
  --output report.json
```

A clearly synthetic fixture is included for testing the pipeline:

```bash
python flare_hunt.py examples/synthetic_hotspots.csv --output /tmp/flare-report.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

The output path must be new unless `--force` is passed. The input CSV is read-only.

## Ranking rule

Clusters are ordered by:
1. hotspot count (descending);
2. total FRP in MW (descending);
3. high-confidence hotspot count (descending);
4. latest observation time (descending).

This is a transparent review-priority heuristic, not a probability of ignition, spread or damage. Spatial clustering uses connected components, so chained neighboring detections can create a cluster whose full extent exceeds the configured pairwise radius.

## NASA FIRMS field notes

NASA FIRMS describes VIIRS fire-pixel latitude/longitude as the center of a nominal 375 m pixel at nadir; scan and track describe actual pixel size. Acquisition date/time is the satellite overpass time in UTC. FRP is reported in megawatts, and confidence is an algorithm-derived quality indicator for an individual hotspot. Numeric confidence values are retained numerically; categorical values remain low/nominal/high. See the official [VIIRS FIRMS field description](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html) and [FIRMS API guidance](https://firms2.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html).

This version does not call the FIRMS API or retrieve live data. Users download a CSV from NASA FIRMS and provide it locally.
