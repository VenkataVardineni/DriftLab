# DriftLab

Production-grade ML monitoring toolkit that generates interactive drift reports (tabular + text), tracks prediction drift, and produces automated alert rules + dashboards you can plug into any model pipeline.

## Features

- **Tabular Drift Detection**: Detect drift in numerical and categorical features using Evidently
- **Text Drift Detection**: NLP-based drift detection for text features (length, vocabulary, embeddings)
- **Interactive Reports**: HTML reports with visualizations
- **Automated Alerts**: Calibrated thresholds with persistence-based alerting
- **Config-Driven**: YAML configuration for flexible pipeline integration
- **Production-Ready**: Docker support and CI/CD integration

## Quick Start

### 1. Generate Demo Data

```bash
python -m driftlab.cli generate --output-dir data --n-samples 1000
```

This creates:
- `data/reference/ref.csv` - Baseline dataset
- `data/current/cur.csv` - Current dataset with controlled drift

### 2. Run Drift Analysis

```bash
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/run_001/
```

This generates:
- `reports/run_001/drift_report.html` - Interactive HTML report
- `reports/run_001/drift_summary.json` - Alert-ready JSON output

The command will print alerts like:
```
ALERT: drift in payload_bytes exceeded threshold
ALERT: drift in run_duration_ms exceeded threshold
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## Usage

### Basic Usage

```bash
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/run_001/
```

### With Configuration

```bash
python -m driftlab.run --config configs/demo.yaml
```

### Using Docker

```bash
# Build image
docker build -t driftlab .

# Run analysis
docker run -v $(pwd)/data:/app/data -v $(pwd)/reports:/app/reports driftlab \
  python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/run_001/
```

## Project Structure

```
driftlab/
├── configs/              # YAML configuration files
├── data/                 # Datasets (reference, current, synthetic)
│   ├── reference/        # Reference/baseline datasets
│   ├── current/          # Current datasets to compare
│   └── synthetic/        # Synthetic data generator
├── driftlab/             # Main package
│   ├── io/               # Data loading and schema validation
│   ├── profiles/         # Drift profiling (tabular, text)
│   ├── reports/          # Report generation (Evidently)
│   ├── alerts/           # Alert rules and thresholds
│   ├── cli.py            # Command-line interface
│   └── run.py            # Main runner
├── reports/              # Generated reports
├── tests/                # Unit tests
└── Dockerfile            # Docker configuration
```

## Configuration

Example `configs/demo.yaml`:

```yaml
# Column type mapping
column_types:
  payload_bytes: numerical
  run_duration_ms: numerical
  status: categorical
  log_message: text

# Text columns for text drift analysis
text_columns:
  - log_message

# Alert settings
alerts:
  dataset_drift_threshold: 0.5
  feature_drift_threshold: 0.3
  consecutive_runs: 3
```

## How to Integrate into Production

### CI/CD Integration

```bash
# In your CI pipeline
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/ci_run/

# Check for alerts
if grep -q "ALERT" reports/ci_run/drift_summary.json; then
  echo "Drift detected! Failing build."
  exit 1
fi
```

### Cron Job

```bash
# Add to crontab
0 0 * * * cd /path/to/driftlab && python -m driftlab.run --config configs/production.yaml
```

### Model Pipeline Integration

```python
from driftlab.run import run_drift_analysis

# After model inference
run_drift_analysis(
    ref_path="data/reference/ref.csv",
    cur_path="data/current/cur.csv",
    output_dir="reports/run_001/",
    config_path="configs/production.yaml"
)

# Check alerts
import json
with open("reports/run_001/drift_summary.json") as f:
    summary = json.load(f)
    if summary.get("alerts"):
        # Trigger notification
        send_alert(summary["alerts"])
```

## Development

```bash
# Run tests
pytest tests/ -v

# Generate demo data
python -m driftlab.cli generate

# Run demo
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/demo/
```

## License

MIT

