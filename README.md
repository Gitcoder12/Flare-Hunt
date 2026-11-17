# Flare-Hunt

**Experimental fire-flare sensor screening.** This project starts with local CSV time-series from temperature, smoke, carbon-monoxide and flame sensors. It calculates per-sensor temperature rate-of-rise and applies a transparent rule-based screen.

## Run

Install with `python -m pip install -e .[dev]`, then run `flare-hunt data/sample_readings.csv`.

CSV columns: sensor_id, timestamp (ISO-8601), temperature_c, smoke_index (0..1), co_ppm, flame_signal (0/1/true/false).

The sample dataset is synthetic and is only a demonstration. The score is not a probability, calibrated model, certified detector or life-safety alarm. Do not use this project as the sole warning system. Before any real deployment, collect labelled data for the actual sensor models and environment, calibrate thresholds, measure false positives/false negatives, test sensor faults, and obtain fire-safety engineering review.

## Evaluation priorities

1. Build a labelled dataset with normal, smouldering, flare-up and sensor-fault conditions.
2. Split by site and time, not random rows, to reduce leakage.
3. Report precision, recall, missed-event rate, false alarms per sensor-day and detection lead time.
4. Add sensor health checks, missing-data alarms, drift monitoring and hysteresis.
5. Keep certified alarms and emergency response systems independent of this prototype.

Run tests with `pytest -q`.
