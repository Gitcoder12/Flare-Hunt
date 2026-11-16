# Project Status — Flare-Hunt

**Updated:** 2026-11-16
**Current stage:** Offline satellite-hotspot clustering MVP

## Implemented
- Parse a local NASA FIRMS VIIRS-style CSV subset.
- Normalize categorical confidence labels and preserve numeric confidence values.
- Validate coordinates, acquisition dates/times (UTC) and FRP (MW).
- Preserve invalid source rows and reason strings.
- Spatial-temporal connected-component clustering with configurable radius/time window.
- Deterministic cluster ranking by count, total FRP, high-confidence count and timestamp.
- JSON report output without modifying the input CSV.
- Five-thousand-row cap to bound pairwise clustering.

## Not implemented
- Live FIRMS API integration or automatic polling.
- Fire ignition/spread prediction or risk probability.
- Weather, wind, fuel, terrain or satellite uncertainty fusion.
- Emergency alerts, dispatch or public safety recommendations.
- Map visualization or geospatial database.

## Known limitations
- Hotspots are satellite detections, not confirmed fires.
- Acquisition time is the satellite observation time, not fire-start time or data-publication time.
- Connected-component chaining may create geographically extended clusters.
- Ranking is a heuristic for analyst review, not a calibrated risk model.
- O(n²) pair comparison is bounded by a 5,000-row input limit.

## Next steps
1. Add spatial indexing to reduce pairwise comparisons while preserving exact cluster results.
2. Add sensor/platform and collection-version awareness with explicit product metadata.
3. Add a map export (GeoJSON) with source rows and provenance.
4. Consider live FIRMS retrieval only with rate/transaction limits, API-key protection, data freshness display and explicit geographic bounds.
5. Evaluate clusters against a labeled historical dataset before making early-detection performance claims.

## Verification
Run `python -m unittest discover -s tests -v` and the documented synthetic CSV example. Do not treat the synthetic fixture as real fire data.
