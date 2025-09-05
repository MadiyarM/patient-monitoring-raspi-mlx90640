# An Intelligent System for Automated Monitoring and Control of Patient Conditions

**One-liner.** Real-time **IR–RGB fusion** for contactless temperature screening with **face identification**, on-device logging (**SQLite**), alerts, and compact 3D-printed enclosure. *(Springer publication: **in press, 2025**).*

## Highlights
- Parallel capture: **MLX90640 (IR)** + **Pi Camera 2 (RGB)** → aligned ROI → estimation & thresholds.
- **Face ID** module for per-patient tracking; local logs, CSV export.
- Runs on **Raspberry Pi 4**, total HW cost **< $130** (BOM pending).

Minimal on-device pipeline. Pi Camera 2 and MLX90640 watch the patient’s face in parallel and stream into a Raspberry Pi 4. We timestamp and sync frames. 
All while logging {username, temperature_c, record_time, abnormality_notification} to SQLite for later poking around. Runs fully on-device (no cloud, no drama) for privacy and low latency.

<p align="center">
  <img src="docs/figs/fig1_system_architecture.png" alt="System architecture: MLX90640 + Pi Camera 2 → Raspberry Pi → Display" width="86%">
</p>
<p align="center">
  <a href="docs/figs/fig1_system_architecture.png">Open full-size figure →</a>
</p>
---

## Installation

We keep dependencies **strictly** to what the two demo scripts import.

```bash
# Python deps used only by the two demos
pip install -r requirements.txt

# System package required by the OpenCV demo
sudo apt update && sudo apt install -y python3-picamera2
```
## Demo

# 1) IR-only heatmap viewer (Matplotlib)
python examples/matplotlib_thermal_viewer.py

# 2) IR+RGB overlay with blend trackbar (OpenCV)
python examples/opencv_thermal_overlay.py   # press 'q' to quit

Result example (face recognition + temperature annotation):

<p align="center"> <img src="docs/figs/fig3_face_temp_result.png" alt="Face recognition and temperature indicating" width="70%"/> </p>

## Hardware

Physical hardware layout (RPi4 + MLX90640 + Pi Camera 2):

<p align="center"> <img src="docs/figs/fig2_hardware_layout.png" alt="Physical hardware layout" width="82%"/> </p>

## Data Logging (SQLite)

Measurements are stored locally for auditing/analysis.

<p align="center"> <img src="docs/figs/fig4_sqlite_table.png" alt="Measurement data stored in SQLite database" width="80%"/> </p>

## Evaluation
Distance study — RGB & Thermal at 50 cm / 100 cm / 150 cm
<p align="center"> <img src="docs/figs/fig5_distances_grid.png" alt="RGB and thermal outputs at varying distances" width="92%"/> </p>

Ambient conditions — 16 °C, 24 °C, 26 °C
<p align="center"> <img src="docs/figs/fig6_ambient_bars.png" alt="Forehead temperature across ambient conditions" width="70%"/> </p>

## Dataset / Docs

We do not ship private data. For documentation:

Save snapshots from the demos into docs/figs/ (press s in the OpenCV window if you add a save hotkey).

Keep small CSV summaries in docs/results/ for plots and tables.

## Notes

Runs on Raspberry Pi 4 with MLX90640 (24×32 thermal) and Pi Camera 2.

This is not a medical device; anonymize any shared data.
