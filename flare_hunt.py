"""Offline clustering and ranking of NASA FIRMS VIIRS hotspot CSV records.

This tool ranks satellite hotspot clusters for analyst review. It is not a
fire-spread model, confirmed-fire detector, emergency alert service or dispatch
system. It performs no network requests.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, TextIO
from urllib.parse import urlparse

EARTH_RADIUS_KM = 6371.0088
MAX_INPUT_ROWS = 5000
REQUIRED_COLUMNS = {"latitude", "longitude", "acq_date", "acq_time", "frp", "confidence"}


@dataclass(frozen=True)
class Hotspot:
    latitude: float
    longitude: float
    observed_at: str
    frp_mw: float
    confidence_class: str
    confidence_numeric: float | None
    satellite: str
    version: str
    daynight: str
    source_row: int

    @property
    def timestamp(self) -> datetime:
        return datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))


def _parse_confidence(value: str) -> tuple[str, float | None]:
    normal = value.strip().lower()
    if normal in {"l", "low"}:
        return "low", None
    if normal in {"n", "nominal", "nom"}:
        return "nominal", None
    if normal in {"h", "high"}:
        return "high", None
    try:
        numeric = float(normal)
    except ValueError as exc:
        raise ValueError(f"unrecognized confidence value: {value!r}") from exc
    if not math.isfinite(numeric) or not 0 <= numeric <= 100:
        raise ValueError("numeric confidence must be between 0 and 100")
    return "numeric", numeric


def _parse_hhmm(value: str) -> time:
    text = value.strip()
    if not text.isdigit() or len(text) > 4:
        raise ValueError("acq_time must be HHMM in UTC")
    text = text.zfill(4)
    hour, minute = int(text[:2]), int(text[2:])
    if hour > 23 or minute > 59:
        raise ValueError("acq_time must be a valid HHMM value in UTC")
    return time(hour, minute, tzinfo=timezone.utc)


def parse_hotspot_row(row: dict[str, str], source_row: int) -> Hotspot:
    lower = {key.strip().lower(): value for key, value in row.items() if key is not None}
    try:
        latitude = float(lower["latitude"])
        longitude = float(lower["longitude"])
        frp = float(lower["frp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("latitude, longitude and frp must be numeric") from exc
    if not math.isfinite(latitude) or not -90 <= latitude <= 90:
        raise ValueError("latitude must be finite and between -90 and 90")
    if not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise ValueError("longitude must be finite and between -180 and 180")
    if not math.isfinite(frp) or frp < 0:
        raise ValueError("frp must be a finite non-negative MW value")
    try:
        acquired_date = date.fromisoformat(lower["acq_date"].strip())
        acquired_time = _parse_hhmm(lower["acq_time"])
    except (KeyError, ValueError) as exc:
        raise ValueError("acq_date/acq_time must contain a valid UTC acquisition date and HHMM time") from exc
    observed_at = datetime.combine(acquired_date, acquired_time).isoformat()
    confidence_class, confidence_numeric = _parse_confidence(lower.get("confidence", ""))
    return Hotspot(
        latitude=latitude,
        longitude=longitude,
        observed_at=observed_at,
        frp_mw=frp,
        confidence_class=confidence_class,
        confidence_numeric=confidence_numeric,
        satellite=lower.get("satellite", "").strip(),
        version=lower.get("version", "").strip(),
        daynight=lower.get("daynight", "").strip().upper(),
        source_row=source_row,
    )


def load_firms_csv(stream: TextIO) -> tuple[list[Hotspot], list[dict[str, Any]]]:
    reader = csv.DictReader(stream)
    columns = {name.strip().lower() for name in (reader.fieldnames or [])}
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
    hotspots: list[Hotspot] = []
    rejected: list[dict[str, Any]] = []
    for row_number, row in enumerate(reader, start=2):
        if row_number - 1 > MAX_INPUT_ROWS:
            raise ValueError(f"input exceeds the safety limit of {MAX_INPUT_ROWS} data rows")
        if not row or not any((value or "").strip() for value in row.values()):
            continue
        try:
            hotspots.append(parse_hotspot_row(row, row_number))
        except ValueError as exc:
            rejected.append({"source_row": row_number, "reason": str(exc), "record": row})
    return hotspots, rejected


def haversine_km(a: Hotspot, b: Hotspot) -> float:
    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    term = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(min(1.0, term)))


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        root_left, root_right = self.find(left), self.find(right)
        if root_left == root_right:
            return
        if self.rank[root_left] < self.rank[root_right]:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        if self.rank[root_left] == self.rank[root_right]:
            self.rank[root_left] += 1


def cluster_hotspots(hotspots: list[Hotspot], radius_km: float = 1.0, time_window_hours: float = 24.0) -> list[dict[str, Any]]:
    if not math.isfinite(radius_km) or radius_km <= 0:
        raise ValueError("radius_km must be a positive finite number")
    if not math.isfinite(time_window_hours) or time_window_hours <= 0:
        raise ValueError("time_window_hours must be a positive finite number")
    if len(hotspots) > MAX_INPUT_ROWS:
        raise ValueError(f"at most {MAX_INPUT_ROWS} hotspots can be clustered in one run")
    union = _UnionFind(len(hotspots))
    time_window = timedelta(hours=time_window_hours)
    for left in range(len(hotspots)):
        for right in range(left + 1, len(hotspots)):
            delta = abs(hotspots[left].timestamp - hotspots[right].timestamp)
            if delta <= time_window and haversine_km(hotspots[left], hotspots[right]) <= radius_km:
                union.union(left, right)

    groups: dict[int, list[Hotspot]] = defaultdict(list)
    for index, hotspot in enumerate(hotspots):
        groups[union.find(index)].append(hotspot)

    clusters = []
    for members in groups.values():
        ordered = sorted(members, key=lambda item: item.timestamp)
        total_frp = round(sum(item.frp_mw for item in members), 3)
        high_count = sum(item.confidence_class == "high" for item in members)
        nominal_count = sum(item.confidence_class == "nominal" for item in members)
        numeric_confidences = [item.confidence_numeric for item in members if item.confidence_numeric is not None]
        clusters.append({
            "centroid": {
                "latitude": round(sum(item.latitude for item in members) / len(members), 6),
                "longitude": round(sum(item.longitude for item in members) / len(members), 6),
            },
            "hotspot_count": len(members),
            "total_frp_mw": total_frp,
            "peak_frp_mw": round(max(item.frp_mw for item in members), 3),
            "high_confidence_count": high_count,
            "nominal_confidence_count": nominal_count,
            "numeric_confidence_mean": round(sum(numeric_confidences) / len(numeric_confidences), 3) if numeric_confidences else None,
            "observed_start_utc": ordered[0].observed_at,
            "observed_end_utc": ordered[-1].observed_at,
            "satellites": sorted({item.satellite for item in members if item.satellite}),
            "source_rows": [item.source_row for item in ordered],
            "hotspots": [asdict(item) for item in ordered],
        })
    clusters.sort(key=lambda cluster: (
        -cluster["hotspot_count"],
        -cluster["total_frp_mw"],
        -cluster["high_confidence_count"],
        -datetime.fromisoformat(cluster["observed_end_utc"]).timestamp(),
    ))
    for rank, cluster in enumerate(clusters, start=1):
        cluster["rank"] = rank
    return clusters


def analyze_file(input_path: Path, radius_km: float, time_window_hours: float) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as stream:
        hotspots, rejected = load_firms_csv(stream)
    clusters = cluster_hotspots(hotspots, radius_km=radius_km, time_window_hours=time_window_hours)
    return {
        "tool": "Flare-Hunt",
        "input_file": input_path.name,
        "input_format": "NASA FIRMS VIIRS-style CSV subset",
        "configuration": {"cluster_radius_km": radius_km, "time_window_hours": time_window_hours, "max_input_rows": MAX_INPUT_ROWS},
        "summary": {
            "valid_hotspot_records": len(hotspots),
            "rejected_records": len(rejected),
            "candidate_clusters": len(clusters),
        },
        "ranking_basis": ["hotspot_count_desc", "total_frp_mw_desc", "high_confidence_count_desc", "observed_end_utc_desc"],
        "clusters": clusters,
        "rejected_records": rejected,
        "limitations": [
            "A satellite hotspot is not a confirmed ground fire or a prediction that a fire will spread.",
            "Satellite acquisition time is an overpass observation time in UTC; it is not necessarily the time a fire started or when data became available.",
            "Clusters use spatial-temporal connected components; chaining can make a cluster's full extent larger than the configured pairwise radius.",
            "This version only analyzes a local CSV. It does not fetch live data, send alerts, estimate spread, or replace local emergency services.",
            "Ranking is a transparent heuristic ordering, not a calibrated probability or risk score.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cluster and rank satellite fire-hotspot records for analyst review.")
    parser.add_argument("input", type=Path, help="Local NASA FIRMS VIIRS-style CSV file")
    parser.add_argument("--radius-km", type=float, default=1.0)
    parser.add_argument("--time-window-hours", type=float, default=24.0)
    parser.add_argument("--output", type=Path, required=True, help="New JSON report path")
    parser.add_argument("--force", action="store_true", help="allow replacing an existing report")
    args = parser.parse_args(argv)
    try:
        if args.output.resolve() == args.input.resolve():
            raise ValueError("output report path must differ from input CSV path")
        if args.output.exists() and not args.force:
            raise FileExistsError("output report already exists; choose a new path or pass --force")
        result = analyze_file(args.input, args.radius_km, args.time_window_hours)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result["summary"], indent=2))
        return 0
    except (OSError, ValueError, csv.Error) as exc:
        print(f"flare-hunt: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
