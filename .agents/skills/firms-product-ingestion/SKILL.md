---
name: firms-product-ingestion
description: Ingest and validate local NASA FIRMS VIIRS-style hotspot files while preserving product semantics and provenance. Use when adding fields, products, versions or metadata.
---

# firms-product-ingestion

## Source-of-truth rule
Read the official FIRMS product description for the exact sensor, platform, product, collection and processing level. VIIRS and MODIS fields or confidence meanings are not interchangeable by assumption.

## Current MVP contract
The parser expects a documented subset: latitude, longitude, acquisition date/time, FRP and confidence; satellite, version and day/night are optional. Acquisition time is UTC HHMM. FRP is MW. Numeric confidence and categorical confidence labels are retained separately.

## Procedure
1. Record sensor/platform, product name, collection/version, processing level, download time and source URL for each ingestion batch when extending the data contract.
2. Validate headers, coordinates, date/time, finite non-negative FRP and native confidence representation.
3. Preserve numeric confidence; do not convert it to low/nominal/high unless the exact product defines the mapping.
4. Preserve categorical low/nominal/high labels without turning them into invented probabilities.
5. Retain original source row and full rejected record with a specific reason.
6. Never substitute missing fields with plausible values.
7. Add a fixture for each claimed product/version and tests for malformed coordinates, timestamps, headers, FRP and confidence.
8. Keep source files immutable and record parser/config version in output metadata.

Review scan/track footprint information, day/night, satellite, product version, near-real-time versus standard quality and whether a file is actually an active-fire product. If product identity is unknown, do not label it definitively as VIIRS.
