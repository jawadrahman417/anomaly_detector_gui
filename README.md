# 🧠 Anomaly Detector Suite

A multi-version Python project to detect anomalies in login data using **machine learning (Isolation Forest)**. It includes:

- 🖥️ **GUI Version** (`login_gui.py`)
- 🧑‍💻 **Command-Line Interface (CLI)** (`cli_anomaly_detector.py`)
- 🤖 **Autonomous Analyzer with Visualizations** (notebook-style script)

---

## 📂 Project Structure

| File                     | Description                                      |
|--------------------------|--------------------------------------------------|
| `login_gui.py`           | Full GUI interface for anomaly detection         |
| `cli_anomaly_detector.py`| CLI tool to run detection via terminal           |
| `login_detector.py`      | Shared logic (if modularized)                    |
| `logins.csv`             | Sample login data                                |
| `analyzed_logins.csv`    | Output: processed and labeled data               |
| `anomalies.csv`          | Output: detected anomalies only                  |
| `autonomous_script.py`   | Standalone visual analyzer script                |

---

## 🔍 Detection Method

The system uses **Isolation Forest** to detect outliers based on:

- `username`
- `login_time` (0–23)
- `location`
- Derived feature: `time_of_day` (morning, afternoon, evening, night)

---

## 🧑‍💻 CLI Version Usage

```bash
python cli_anomaly_detector.py -f logins.csv
