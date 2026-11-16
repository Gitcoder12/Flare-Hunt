---
name: hotspot-spatiotemporal-analysis
description: Develop and review hotspot clustering, geospatial calculations, event grouping and ranking. Use when changing radius, time windows, connected components, indexes or GeoJSON.
---

# hotspot-spatiotemporal-analysis

## Current semantics
The MVP uses haversine distance and union-find connected components. Two records are joined if pairwise distance and time difference satisfy thresholds. Chaining means endpoints of one component may be farther apart than the configured radius.

## Procedure
1. State what a cluster represents: neighboring pixels, a candidate hotspot group or an independently documented fire event. These are not interchangeable.
2. Keep timestamps timezone-aware and UTC.
3. Test geodesic calculations at high latitudes and across longitude wraparound near ±180°.
4. Document connected-component chaining. If maximum cluster diameter is required, design and test a different algorithm.
5. Treat centroids carefully near the date line and high latitudes; arithmetic longitude averaging can be wrong there.
6. Keep categorical confidence separate from numeric confidence.
7. Define ranking as a transparent ordered tuple with units and tie-breakers. It is not a probability.
8. Respect the current 5,000-record O(n²) cap until an exact spatial-index optimization has correctness tests and benchmarks.

## Required tests
Identical coordinates; known short/long distances; date-line and high-latitude cases; same location outside time window; exact radius/time boundary; chained A-B/B-C but not A-C; duplicate detections; deterministic ranking ties.

For optimizations, compare results with a simple reference implementation on seeded fixtures and report runtime/complexity.
