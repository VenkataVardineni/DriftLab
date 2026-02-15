# DriftLab

Production-grade ML monitoring toolkit that generates interactive drift reports (tabular + text), tracks prediction drift, and produces automated alert rules + dashboards you can plug into any model pipeline.

## Overview

DriftLab is a comprehensive machine learning monitoring solution designed to detect data drift in production ML systems. It supports both tabular and text data, provides interactive HTML reports, and includes intelligent alerting with calibrated thresholds and persistence tracking.

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
- **Implementation**: Custom alert rules with persistence tracking using JSON-based history storage

### 6. **Config-Driven Architecture**
- **YAML configuration files** for flexible pipeline integration
- **Column type mapping** configuration
- **Text column specification** for text drift analysis
- **Alert rule configuration** (thresholds, consecutive runs)
- **History file configuration** for threshold calibration
- **Implementation**: YAML parsing using `pyyaml`

### 7. **Synthetic Data Generator**
- **Controlled drift generation** for testing and demos
- **Numerical drift**: Mean shifts and variance changes
- **Categorical drift**: Proportion shifts in category distributions
- **Text drift**: Length shifts and vocabulary changes
- **Reproducible**: Seed-based generation for consistent results
- **Implementation**: Custom generator using `numpy` and `pandas`

### 8. **Production-Ready Infrastructure**
- **Docker support**: Containerized deployment with Dockerfile
- **CI/CD integration**: GitHub Actions workflow for automated testing
- **Unit tests**: Test suite for schema validation and profiles
- **Modular architecture**: Plugin-based design with Profile and AlertRule interfaces
- **CLI interface**: Command-line tool for easy integration

## Technologies & Libraries Used

### Core Dependencies
- **pandas** (>=1.3.0): Data manipulation and analysis
- **numpy** (>=1.21.0): Numerical computations
- **evidently** (>=0.4.0): Statistical drift detection and report generation
- **pyyaml** (>=5.4.0): YAML configuration file parsing
- **sentence-transformers** (>=2.2.0): Text embedding generation for semantic drift detection
- **scikit-learn** (>=1.0.0): Machine learning utilities (used by Evidently and sentence-transformers)

### Architecture Components
- **Plugin Architecture**: Abstract base classes (`Profile`, `AlertRule`) for extensibility
- **Modular Design**: Separate modules for I/O, profiling, reporting, and alerting
- **Error Handling**: Graceful degradation when optional dependencies are unavailable
- **Type Hints**: Full type annotations for better code maintainability

## Project Structure

```
driftlab/
├── configs/              # YAML configuration files
│   └── demo.yaml        # Example configuration
├── data/                 # Datasets directory
│   ├── reference/        # Reference/baseline datasets
│   ├── current/          # Current datasets to compare
│   └── synthetic/        # Synthetic data generator
│       ├── __init__.py
│       └── generate.py  # Data generation functions
├── driftlab/             # Main package
│   ├── io/               # Data I/O and validation
│   │   ├── load.py      # CSV loading utilities
│   │   └── schema.py    # Schema validation and quality checks
│   ├── profiles/         # Drift profiling modules
│   │   ├── base.py      # Profile interface
│   │   ├── tabular.py   # Tabular drift profile
│   │   └── text.py      # Text drift profile
│   ├── reports/          # Report generation
│   │   ├── evidently_report.py  # Evidently integration
│   │   └── render.py    # JSON report rendering
│   ├── alerts/           # Alert system
│   │   ├── base.py      # AlertRule interface
│   │   ├── rules.py     # Alert rule implementations
│   │   └── thresholds.py # Threshold calibration
│   ├── cli.py           # Command-line interface
│   ├── run.py           # Main analysis runner
│   └── __main__.py      # Module entry point
├── reports/              # Generated reports (gitignored)
├── tests/                # Unit tests
│   ├── test_schema.py
│   └── test_profiles.py
├── .github/
│   └── workflows/
│       └── ci.yml        # CI/CD pipeline
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
├── setup.py             # Package setup
└── README.md            # This file
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

The command will print alerts like:
```
ALERT: drift in payload_bytes exceeded threshold
ALERT: drift in run_duration_ms exceeded threshold
```

## Usage Examples

### Basic Usage

```bash
python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/run_001/
```

### With Configuration File

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

## Configuration

Example `configs/demo.yaml`:

```yaml
# Input file paths
input:
  reference: data/reference/ref.csv
  current: data/current/cur.csv

# Column type mapping
column_types:
  payload_bytes: numerical
  run_duration_ms: numerical
  cpu_usage: numerical
  status: categorical
  region: categorical
  log_message: text

# Text columns for text drift analysis
text_columns:
  - log_message

# Alert rule settings
alerts:
  dataset_drift_threshold: 0.5
  feature_drift_threshold: 0.3
  consecutive_runs: 3

# History file for threshold calibration
history_file: .driftlab_history.json

# Output settings
output:
  directory: reports
  format: [html, json]
```

## Integration Guide

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

## Output Format

### HTML Report
Interactive HTML report with:
- Dataset comparison visualizations
- Column-level drift scores
- Statistical test results
- Distribution comparisons

### JSON Summary
Machine-readable JSON with:
- Run metadata (run_id, paths, timestamps)
- Validation results (schema validation, quality metrics)
- Drift metrics (dataset drift score, column drift scores, text drift metrics)
- Alert list (severity, message, metric name, value, threshold)
- Report paths (HTML and JSON locations)

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
