# Flare-Hunt
Detect and Rank early fire flare-ups before they spread.

---

## Engineering Audit & Handover — 2026-11-17

**Reviewed commit:** `d5127fdfac4f87042417ebddd759b56955256e0e` (`main`).

### Confirmed findings
- The reviewed branch contains only `README.md` and `LICENSE`; no executable detection, ranking, data-ingestion, or alerting implementation was found.
- The fire flare-up detection and ranking description is a project objective, not a demonstrated capability on this branch.

### Next actions
1. Define the data source, sensor modality, flare-up label, and alert threshold.
2. Implement a small offline evaluation using sourced, labelled fire/satellite/sensor data.
3. Measure false alarms and missed detections before presenting the tool as an early-warning system.

**Verification status:** source-tree inspection only; no runnable product or test suite verified.
