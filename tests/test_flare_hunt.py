"""Tests for Flare-Hunt's transparent sensor screening prototype."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from flare_hunt import Reading, analyze_csv, analyze_readings, score_reading


def reading(
    sensor_id="A",
    minutes=0,
    temp=25.0,
    smoke=0.0,
    co=0.0,
    flame=False,
):
    return Reading(
        sensor_id=sensor_id,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=minutes),
        temperature_c=temp,
        smoke_index=smoke,
        co_ppm=co,
        flame_signal=flame,
    )


def test_normal_readings_do_not_raise_alert():
    result = score_reading(reading(), None)

    assert result.level == "normal"
    assert result.alert is False
    assert result.score == 0


def test_multiple_independent_signals_raise_critical_screening_level():
    result = score_reading(
        reading(temp=75, smoke=0.8, co=55, flame=True),
        rate_of_rise_c_per_min=9.0,
    )

    assert result.level == "critical"
    assert result.alert is True
    assert result.score == 100
    assert "flame_sensor_active" in result.signals


def test_temperature_rate_of_rise_is_calculated_per_sensor():
    results = analyze_readings(
        [
            reading("A", 0, temp=30),
            reading("A", 1, temp=39),
            reading("B", 0, temp=20),
            reading("B", 1, temp=21),
        ]
    )

    by_sensor = {(item.sensor_id, item.timestamp): item for item in results}
    a_last = next(item for item in results if item.sensor_id == "A" and item.rate_of_rise_c_per_min is not None)
    b_last = next(item for item in results if item.sensor_id == "B" and item.rate_of_rise_c_per_min is not None)

    assert a_last.rate_of_rise_c_per_min == 9.0
    assert b_last.rate_of_rise_c_per_min == 1.0


def test_duplicate_timestamp_for_one_sensor_is_rejected():
    with pytest.raises(ValueError, match="timestamps"):
        analyze_readings([reading("A", 0), reading("A", 0, temp=30)])


def test_sensor_values_are_range_checked():
    with pytest.raises(ValueError, match="smoke_index"):
        score_reading(reading(smoke=1.5), None)


def test_csv_ingestion_and_output(tmp_path):
    csv_file = tmp_path / "readings.csv"
    csv_file.write_text(
        "sensor_id,timestamp,temperature_c,smoke_index,co_ppm,flame_signal\n"
        "A,2026-01-01T00:00:00Z,30,0.1,2,0\n"
        "A,2026-01-01T00:01:00Z,40,0.5,30,0\n",
        encoding="utf-8",
    )

    results = analyze_csv(csv_file)

    assert len(results) == 2
    assert results[1].rate_of_rise_c_per_min == 10.0
    assert results[1].level == "watch" or results[1].level == "elevated"


def test_empty_csv_data_is_rejected(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(
        "sensor_id,timestamp,temperature_c,smoke_index,co_ppm,flame_signal\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="no sensor readings"):
        analyze_csv(csv_file)
