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

---

## Examples Used
- Screening a temperature rate-of-rise during a simulated smouldering event
- Comparing smoke, carbon-monoxide, and flame sensor readings
- Detecting missing or faulty sensor readings in a test dataset


---

## Comparison with Existing Open-Source Projects

Flare-Hunt is documented as an experimental fire-sensor screening tool that ingests local time-series readings from temperature, smoke, carbon-monoxide and flame sensors, then applies transparent rule-based checks. The following projects provide adjacent fire-modelling and sensor-monitoring references.

| Project | Established focus | Relationship to Flare-Hunt |
|---|---|---|
| [Fire Dynamics Simulator (FDS)](https://github.com/firemodels/fds) | Computational fluid-dynamics model of fire-driven fluid flow, heat transfer and smoke transport | A much more detailed physical simulation system; Flare-Hunt is a small sensor-data screening tool, not a fire dynamics simulator. |
| [Grafana](https://github.com/grafana/grafana) | Time-series visualization and monitoring dashboards | A mature observability/visualization platform; Flare-Hunt's proposed distinction is a simple domain-specific screening rule over fire-related sensor fields. |
| [ThingsBoard](https://github.com/thingsboard/thingsboard) | IoT device connectivity, telemetry collection and dashboards | A broader IoT platform; Flare-Hunt currently focuses on local CSV ingestion and an experimental screening calculation rather than fleet/device management. |

### Where Flare-Hunt is different
- **Fire-sensor-specific input model:** the tool expects temperature, smoke, CO and flame readings with explicit units/fields.
- **Transparent screening logic:** temperature rate-of-rise and rule-based checks are inspectable rather than hidden behind a black-box model.
- **Safety-conscious prototype scope:** the README explicitly states that synthetic samples are demonstrations and the score is not a calibrated probability or certified alarm.

### Where established projects are stronger
FDS provides a far deeper physical fire model; Grafana and ThingsBoard have mature telemetry and visualization ecosystems. Flare-Hunt does not replace certified smoke/fire alarms or an approved building safety system.

### Life-safety and evaluation requirements
Build labelled datasets covering normal conditions, smouldering, flare-ups, sensor faults and environmental confounders. Split evaluation by site and time, and report missed-event rate, false alarms per sensor-day and detection lead time. Validate sensor health and calibration, obtain fire-safety engineering review, and keep certified alarms independent. This is a prototype-scope comparison, not a safety certification or detection-accuracy claim.
