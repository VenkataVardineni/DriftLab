# DriftLab

Production-grade ML monitoring toolkit that generates interactive drift reports (tabular + text), tracks **prediction / score drift**, and produces automated alert rules, optional **Prometheus** textfile metrics, and JSON summaries you can plug into any model pipeline.

## Overview

DriftLab detects data drift in production ML systems. It supports **CSV and Parquet** inputs, tabular and text features, interactive HTML reports via [Evidently AI](https://www.evidentlyai.com/), and alerting with **separate** calibration history vs feature-persistence state. Runs emit **structured logs** (level via `DRIFTLAB_LOG_LEVEL` or CLI), **dataset fingerprints**, and UTC **run metadata** in `drift_summary.json`.

## Core Features

### 1. **Tabular Drift Detection**
- **Statistical drift detection** for numerical features using statistical tests
- **Categorical drift detection** for categorical features using distribution comparisons
- **Column-level drift scores** with drift detection flags
- **Dataset-level drift metrics** to assess overall data quality
- **Implementation**: Powered by [Evidently AI](https://www.evidentlyai.com/) DataDriftPreset

### 2. **Text Drift Detection**
- **Text length statistics**: Mean, std, min, max length comparison between reference and current datasets
- **Vocabulary richness analysis**: Unique words to total words ratio to detect vocabulary shifts
- **N-gram frequency analysis**: Top n-gram frequency shifts to identify term-level changes
- **Embedding-based drift detection**: Uses sentence transformers to compute semantic distribution shifts
  - Centroid distance calculation
  - Variance shift detection
  - Combined embedding shift score
- **Implementation**: Custom implementation using `sentence-transformers` library with `all-MiniLM-L6-v2` model

### 3. **Data Schema Validation & Quality Checks**
- **Loaders**: CSV via `read_csv`; Parquet via `read_parquet` when **`pyarrow`** is installed
- **Column type mapping**: Support for numerical, categorical, text, and timestamp columns
- **Required column validation**: Ensures all required columns are present
- **Empty column detection**: Identifies completely empty columns
- **Timestamp parsing**: Automatic timestamp column parsing and validation
- **Data quality metrics**:
  - Missing percentage per column
  - Unique value counts
  - Min/max values for numerical columns
  - Top value distributions for categorical columns
- **Implementation**: Custom validation layer using `pandas`

### 4. **Interactive HTML Reports**
- **Visual drift reports** with charts and visualizations
- **Column-level drift analysis** with detailed metrics
- **Dataset comparison views** showing reference vs current distributions
- **Export-ready format** for sharing and documentation
- **Implementation**: Generated using Evidently's HTML export functionality

### 5. **Automated Alerting System**
- **Calibrated thresholds**: Dynamic threshold calibration based on historical drift metrics
  - Uses percentile-based calibration (default: 95th percentile)
  - Stores historical metrics for adaptive threshold setting
  - Prevents noisy alerts by learning from past patterns
- **Dataset drift alerts**: Alerts when overall dataset drift exceeds threshold
- **Feature persistence alerts**: Alerts when specific features drift above threshold for consecutive runs
  - Configurable consecutive run count (default: 3)
  - Tracks drift history per feature
  - Prevents false positives from transient drift
- **Alert severity levels**: Critical alerts for actionable drift detection
- **JSON export**: Machine-readable alert format for CI/CD integration
- **Separate persistence store**: Feature drift streaks are stored in `persistence_history_file` (default `.driftlab_persistence.json`), **not** in the threshold calibrator history file, so JSON on disk stays consistent.
- **Implementation**: Custom alert rules with persistence tracking using JSON-based history storage

### 6. **Config-Driven Architecture**
- **YAML configuration** merged over **built-in defaults** (nested keys are deep-merged)
- **Column type mapping**, **text columns**, **prediction columns** (model scores / labels), optional **Evidently `column_mapping`** (`numerical_features`, `categorical_features`, etc.)
- **Alert settings**: thresholds, consecutive runs
- **`history_file`**: append-only list of metric snapshots for threshold calibration
- **`persistence_history_file`**: per-feature drift streak booleans (must differ from `history_file`)
- **Optional `prometheus_textfile`**: write `drift_metrics.prom` next to the JSON summary
- **`fingerprint_sample_rows`**: rows hashed into `fingerprints.*.sample_sha256` (use `0` for counts/dtypes only)
- **Implementation**: `pyyaml` + `driftlab.config_loader`

### 7. **Synthetic Data Generator**
- **Controlled drift generation** for testing and demos
- **Numerical drift**: Mean shifts and variance changes
- **Categorical drift**: Proportion shifts in category distributions
- **Text drift**: Length shifts and vocabulary changes
- **Reproducible**: Seed-based generation for consistent results
- **Implementation**: Custom generator using `numpy` and `pandas`

### 8. **Production-Ready Infrastructure**
- **Docker**: Image runs as non-root user `drift` (uid 10001); build installs `driftlab[parquet]` for Parquet I/O
- **CI/CD**: GitHub Actions runs `pytest` (failures fail the job), generates synthetic data, and runs a full drift job
- **Unit tests**: Schema, profiles, load, config, fingerprints, prediction drift, Prometheus export, alerts, validation
- **Modular architecture**: `Profile` and `AlertRule` interfaces; atomic JSON writes for summaries
- **CLI**: `run`, `generate`, `validate` via `driftlab` or `python -m driftlab.cli`; `python -m driftlab.run …` delegates to `run`

## Prediction drift profile

Configure **`prediction_columns`** in YAML with model outputs (probabilities, logits, or predicted labels). For numeric columns, DriftLab combines a normalized mean shift with a histogram-overlap proxy; for categorical-like columns, it uses a total-variation distance between class proportions. Metrics appear in `drift_summary.json` under keys like `{column}_prediction_drift`.

## Technologies & Libraries Used

### Core Dependencies
- **pandas** (>=1.3.0): Data manipulation and analysis
- **numpy** (>=1.21.0): Numerical computations
- **evidently** (>=0.4.0): Statistical drift detection and report generation
- **pyyaml** (>=5.4.0): YAML configuration file parsing
- **sentence-transformers** (>=2.2.0): Text embedding generation for semantic drift detection
- **scikit-learn** (>=1.0.0): Machine learning utilities (used by Evidently and sentence-transformers)

### Optional
- **`pyarrow`** (via `pip install driftlab[parquet]` or `pip install -e ".[parquet]"`): Parquet input in `load_dataframe`

### Architecture Components
- **Plugin Architecture**: Abstract base classes (`Profile`, `AlertRule`) for extensibility
- **Modular Design**: Separate modules for I/O, profiling, reporting, and alerting
- **Error Handling**: Graceful degradation when optional dependencies are unavailable
- **Type Hints**: Full type annotations for better code maintainability

## Project Structure

```
driftlab/
├── configs/              # YAML configuration files
│   └── demo.yaml         # Example configuration
├── data/                 # Datasets directory
│   ├── reference/        # Reference/baseline datasets
│   ├── current/          # Current datasets to compare
│   └── synthetic/        # Synthetic data generator
│       ├── __init__.py
│       └── generate.py
├── driftlab/             # Main package
│   ├── io/
│   │   ├── load.py       # CSV + Parquet loading
│   │   └── schema.py     # Schema validation and quality checks
│   ├── profiles/
│   │   ├── base.py
│   │   ├── tabular.py
│   │   ├── text.py
│   │   └── prediction.py # Score / label drift
│   ├── reports/
│   │   ├── evidently_report.py
│   │   ├── render.py     # Atomic JSON writes
│   │   └── prometheus_export.py
│   ├── alerts/
│   │   ├── base.py
│   │   ├── rules.py
│   │   └── thresholds.py
│   ├── config_loader.py  # YAML + deep-merge defaults
│   ├── fingerprint.py    # Dataset fingerprints for manifests
│   ├── logutil.py        # DRIFTLAB_LOG_LEVEL / basicConfig
│   ├── validate_datasets.py  # Schema-only validation API
│   ├── cli.py
│   ├── run.py
│   └── __main__.py
├── reports/              # Generated reports (gitignored)
├── tests/                # Unit tests (schema, profiles, load, config, …)
├── .github/workflows/
│   └── ci.yml
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── setup.py
└── README.md
```

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

Logs use a structured line format; **critical** alerts are emitted at **WARNING** level. Override verbosity with **`DRIFTLAB_LOG_LEVEL`** or CLI **`-v`** (DEBUG) / **`-q`** (WARNING only).

## Usage Examples

### Basic Usage

```bash
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/run_001/
# equivalent: driftlab run --ref ... --cur ... --out ...
```

### With Configuration File

```bash
python -m driftlab.run --config configs/demo.yaml
```

### Verbose / quiet logging and CI exit codes

```bash
driftlab run --config configs/demo.yaml -v
driftlab run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/out/ --fail-on-critical
# exits with code 2 if any critical alert fires (useful for gating CI)
```

### Parquet inputs

Reference and current paths may be **`.parquet`** or **`.pq`** when **`pyarrow`** is installed (`pip install driftlab[parquet]`).

### Schema-only validation (no drift run)

```bash
driftlab validate --ref data/reference/ref.csv --cur data/current/cur.csv --config configs/demo.yaml
driftlab validate --ref data/reference/ref.csv --cur data/current/cur.csv --config configs/demo.yaml --json
# exit code 1 if validation fails; optional --json for automation
```

### Using Docker

```bash
docker build -t driftlab .

# Container runs as user `drift` (uid 10001); mount data and reports
docker run -u drift -v $(pwd)/data:/app/data -v $(pwd)/reports:/app/reports driftlab \
  python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/run_001/
```

## Configuration

Example `configs/demo.yaml` (see repository file for comments):

```yaml
input:
  reference: data/reference/ref.csv
  current: data/current/cur.csv

column_types:
  payload_bytes: numerical
  run_duration_ms: numerical
  cpu_usage: numerical
  status: categorical
  region: categorical
  log_message: text

text_columns:
  - log_message

# Model outputs to monitor (scores, logits, predicted labels)
prediction_columns: []

# Optional Evidently column mapping (uncomment keys as needed)
column_mapping:
  # numerical_features: ["payload_bytes", "run_duration_ms", "cpu_usage"]
  # categorical_features: ["status", "region"]

alerts:
  dataset_drift_threshold: 0.5
  feature_drift_threshold: 0.3
  consecutive_runs: 3

prometheus_textfile: false

# Metric snapshots for threshold calibration (JSON list)
history_file: .driftlab_history.json
# Per-feature drift streaks — keep separate from history_file
persistence_history_file: .driftlab_persistence.json

fingerprint_sample_rows: 5

output:
  directory: reports
  format: [html, json]
```

Optional keys for **`driftlab validate`**: `required_columns`, `timestamp_column` (same schema as `Schema` in code).

## Integration Guide

### CI/CD Integration

```bash
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/ci_run/ \
  --fail-on-critical

# Or inspect drift_summary.json (includes meta, fingerprints, alerts)
python -c "import json,sys; d=json.load(open('reports/ci_run/drift_summary.json')); sys.exit(2 if any(a.get('severity')=='critical' for a in d.get('alerts',[])) else 0)"
```

### Cron Job

```bash
# Add to crontab
0 0 * * * cd /path/to/driftlab && python -m driftlab.run --config configs/production.yaml
```

### Model Pipeline Integration

```python
from driftlab.run import run_drift_analysis

summary = run_drift_analysis(
    ref_path="data/reference/ref.csv",
    cur_path="data/current/cur.csv",
    output_dir="reports/run_001/",
    config_path="configs/production.yaml",
    log_level=None,  # or "DEBUG"; also set DRIFTLAB_LOG_LEVEL in the environment
)

# summary is the same dict written to drift_summary.json
for alert in summary.get("alerts", []):
    if alert.get("severity") == "critical":
        send_alert(alert)
```

Quick schema gate without a full run:

```python
from driftlab.validate_datasets import validate_pair

result = validate_pair("ref.csv", "cur.csv", "configs/production.yaml")
assert result["valid"]
```

## Output Format

### HTML Report
Interactive HTML report with:
- Dataset comparison visualizations
- Column-level drift scores
- Statistical test results
- Distribution comparisons

### JSON Summary
Machine-readable JSON with:
- **`meta`**: `driftlab_version`, `started_at`, `completed_at` (UTC ISO-8601)
- **`fingerprints`**: reference/current row counts, column dtypes, optional `sample_sha256` for the first N rows
- **`run_id`**, **`reference_path`**, **`current_path`**
- **Validation** (schema + quality metrics per dataset)
- **Metrics**: tabular, text, prediction drift, Evidently dataset/column drift
- **Alerts**: severity, message, metric name, value, threshold
- **`reports`**: `html`, `json`, and **`prometheus`** path when `prometheus_textfile` is enabled

Written **atomically** (temp file + replace) to avoid partial JSON on failure.

## Development

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
pytest tests/ -v

python -m driftlab.cli generate
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/demo/
driftlab validate --ref data/reference/ref.csv --cur data/current/cur.csv --config configs/demo.yaml
```

Current package version: **0.2.0** (`driftlab.__version__` / `setup.py`).

## License

MIT
