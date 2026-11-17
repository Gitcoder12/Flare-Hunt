"""Transparent experimental fire-flare screening from time-series sensor CSV.

This is a research prototype, not a certified fire alarm or life-safety system.
Thresholds must be calibrated against labelled data for the intended sensors,
environment and deployment. Never use it as the sole emergency warning channel.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {
    "sensor_id",
    "timestamp",
    "temperature_c",
    "smoke_index",
    "co_ppm",
    "flame_signal",
}


@dataclass(frozen=True)
class Reading:
    sensor_id: str
    timestamp: datetime
    temperature_c: float
    smoke_index: float
    co_ppm: float
    flame_signal: bool


@dataclass(frozen=True)
class FlareAssessment:
    sensor_id: str
    timestamp: str
    score: int
    level: str
    alert: bool
    rate_of_rise_c_per_min: float | None
    signals: tuple[str, ...]
    explanation: str


def _finite_number(value: str, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def _parse_reading(row: dict[str, str], line_number: int) -> Reading:
    missing = REQUIRED_COLUMNS - row.keys()
    if missing:
        raise ValueError(f"CSV line {line_number}: missing columns {', '.join(sorted(missing))}")
    sensor_id = row["sensor_id"].strip()
    if not sensor_id:
        raise ValueError(f"CSV line {line_number}: sensor_id cannot be empty")
    try:
        timestamp = datetime.fromisoformat(row["timestamp"].strip().replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"CSV line {line_number}: timestamp must be ISO-8601") from exc

    temperature = _finite_number(row["temperature_c"], "temperature_c")
    smoke = _finite_number(row["smoke_index"], "smoke_index")
    co_ppm = _finite_number(row["co_ppm"], "co_ppm")
    if not 0 <= smoke <= 1:
        raise ValueError("smoke_index must be between 0 and 1")
    if co_ppm < 0:
        raise ValueError("co_ppm cannot be negative")
    flame = row["flame_signal"].strip().casefold()
    if flame not in {"0", "1", "true", "false"}:
        raise ValueError("flame_signal must be 0/1/true/false")
    return Reading(sensor_id, timestamp, temperature, smoke, co_ppm, flame in {"1", "true"})


def score_reading(
    reading: Reading, rate_of_rise_c_per_min: float | None
) -> FlareAssessment:
    """Apply documented threshold rules; the score is not a probability."""
    score = 0
    signals: list[str] = []

    if reading.temperature_c >= 70:
        score += 35
        signals.append("very_high_temperature")
    elif reading.temperature_c >= 55:
        score += 20
        signals.append("high_temperature")

    if rate_of_rise_c_per_min is not None:
        if rate_of_rise_c_per_min >= 8:
            score += 30
            signals.append("rapid_temperature_rise")
        elif rate_of_rise_c_per_min >= 4:
            score += 20
            signals.append("elevated_temperature_rise")

    if reading.smoke_index >= 0.65:
        score += 25
        signals.append("high_smoke_index")
    elif reading.smoke_index >= 0.35:
        score += 15
        signals.append("smoke_signal")

    if reading.co_ppm >= 50:
        score += 20
        signals.append("high_co")
    elif reading.co_ppm >= 25:
        score += 10
        signals.append("co_signal")

    if reading.flame_signal:
        score += 30
        signals.append("flame_sensor_active")

    score = min(score, 100)
    if score >= 70:
        level = "critical"
    elif score >= 45:
        level = "elevated"
    elif score >= 25:
        level = "watch"
    else:
        level = "normal"

    return FlareAssessment(
        sensor_id=reading.sensor_id,
        timestamp=reading.timestamp.isoformat(),
        score=score,
        level=level,
        alert=level in {"elevated", "critical"},
        rate_of_rise_c_per_min=(
            round(rate_of_rise_c_per_min, 3)
            if rate_of_rise_c_per_min is not None
            else None
        ),
        signals=tuple(signals),
        explanation=(
            "Rule-based screening result only; confirm with independent sensors "
            "and an approved fire-safety system."
        ),
    )


def analyze_readings(readings: list[Reading]) -> list[FlareAssessment]:
    """Analyze each sensor independently and calculate its temperature rise."""
    by_sensor: dict[str, list[Reading]] = defaultdict(list)
    for reading in readings:
        by_sensor[reading.sensor_id].append(reading)

    output: list[FlareAssessment] = []
    for sensor_id in sorted(by_sensor):
        series = sorted(by_sensor[sensor_id], key=lambda item: item.timestamp)
        previous: Reading | None = None
        for current in series:
            rate = None
            if previous is not None:
                delta_seconds = (current.timestamp - previous.timestamp).total_seconds()
                if delta_seconds <= 0:
                    raise ValueError(
                        f"sensor {sensor_id} has duplicate or non-increasing timestamps"
                    )
                rate = (
                    current.temperature_c - previous.temperature_c
                ) / (delta_seconds / 60.0)
            output.append(score_reading(current, rate))
            previous = current
    return sorted(output, key=lambda item: (item.timestamp, item.sensor_id))


def analyze_csv(path: Path) -> list[FlareAssessment]:
    """Read CSV data and return assessments."""
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError("CSV file must have a header row")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
        readings = [
            _parse_reading(row, line_number)
            for line_number, row in enumerate(reader, start=2)
        ]
    if not readings:
        raise ValueError("CSV contains no sensor readings")
    return analyze_readings(readings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Experimental fire-flare sensor screening")
    parser.add_argument("csv_file", type=Path, help="Sensor CSV file")
    args = parser.parse_args(argv)
    try:
        results = analyze_csv(args.csv_file)
        print(json.dumps([asdict(item) for item in results], indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"flare-hunt: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
