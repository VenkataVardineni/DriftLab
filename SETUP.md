# DriftLab Setup Instructions

This guide will help you set up DriftLab on your system for development and production use.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large datasets)
- **Disk Space**: ~500MB for installation and dependencies

### Required Software
- Python 3.8+ with pip
- Git (for cloning the repository)
- Docker (optional, for containerized deployment)

## Installation Methods

### Method 1: Standard Installation (Recommended)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/VenkataVardineni/DriftLab.git
cd DriftLab
```

#### Step 2: Create Virtual Environment (Recommended)

**Using venv:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Using conda:**
```bash
conda create -n driftlab python=3.9
conda activate driftlab
```

#### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Install DriftLab package in development mode
pip install -e .
```

#### Step 4: Verify Installation

```bash
# Check if installation was successful
python -c "import driftlab; print('DriftLab installed successfully!')"

# Check CLI availability
python -m driftlab.cli --help
```

### Method 2: Docker Installation

#### Step 1: Build Docker Image

```bash
docker build -t driftlab .
```

#### Step 2: Verify Docker Image

```bash
docker images | grep driftlab
```

#### Step 3: Run Container

```bash
# Mount data and reports directories
docker run -v $(pwd)/data:/app/data -v $(pwd)/reports:/app/reports driftlab \
  python -m driftlab.run --ref data/reference/ref.csv --cur data/current/cur.csv --out reports/run_001/
```

### Method 3: Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/VenkataVardineni/DriftLab.git
cd DriftLab

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Install additional development tools (if needed)
pip install pytest pytest-cov black flake8
```

## Post-Installation Setup

### Step 1: Create Directory Structure

```bash
# Create necessary directories
mkdir -p data/reference data/current data/synthetic
mkdir -p reports configs
```

### Step 2: Generate Demo Data (Optional)

```bash
# Generate sample datasets for testing
python -m driftlab.cli generate --output-dir data --n-samples 1000
```

This will create:
- `data/reference/ref.csv` - Reference dataset
- `data/current/cur.csv` - Current dataset with drift

### Step 3: Test Installation

```bash
# Run a test analysis
python -m driftlab.run \
  --ref data/reference/ref.csv \
  --cur data/current/cur.csv \
  --out reports/test_run/

# Verify output files were created
ls -lh reports/test_run/
```

Expected output:
- `drift_report.html` - HTML report
- `drift_summary.json` - JSON summary

## Configuration Setup

### Create Configuration File

Create a configuration file for your use case:

```bash
cp configs/demo.yaml configs/my_config.yaml
```

Edit `configs/my_config.yaml` with your settings:

```yaml
# Input file paths
input:
  reference: data/reference/ref.csv
  current: data/current/cur.csv

# Column type mapping
column_types:
  your_numerical_col: numerical
  your_categorical_col: categorical
  your_text_col: text

# Text columns for text drift analysis
text_columns:
  - your_text_col

# Alert settings
alerts:
  dataset_drift_threshold: 0.5
  feature_drift_threshold: 0.3
  consecutive_runs: 3

# History file for threshold calibration
history_file: .driftlab_history.json
```

## Environment Setup

### Environment Variables (Optional)

You can set environment variables for configuration:

```bash
# Set default config path
export DRIFTLAB_CONFIG=configs/production.yaml

# Set default history file location
export DRIFTLAB_HISTORY_FILE=.driftlab_history.json
```

### Path Configuration

Add to your shell profile (`.bashrc`, `.zshrc`, etc.) if needed:

```bash
# Add DriftLab to PATH (if installed globally)
export PATH=$PATH:/path/to/driftlab/bin
```

## Verification Checklist

After installation, verify the following:

- [ ] Python version is 3.8 or higher: `python --version`
- [ ] All dependencies installed: `pip list | grep -E "pandas|numpy|evidently|pyyaml"`
- [ ] DriftLab package importable: `python -c "import driftlab"`
- [ ] CLI command works: `python -m driftlab.cli --help`
- [ ] Demo data generation works: `python -m driftlab.cli generate --help`
- [ ] Test run completes successfully: Check `reports/test_run/` directory

## Quick Start Test

Run this complete test to verify everything works:

```bash
# 1. Generate demo data
python -m driftlab.cli generate --output-dir data --n-samples 500

# 2. Run analysis
python -m driftlab.run \
  --ref data/reference/ref.csv \
  --cur data/current/cur.csv \
  --out reports/quick_test/

# 3. Verify outputs
ls -lh reports/quick_test/
cat reports/quick_test/drift_summary.json | head -20
```

## Production Deployment

### For Production Use

1. **Install in production environment:**
   ```bash
   pip install -r requirements.txt
   pip install .
   ```

2. **Set up configuration:**
   - Create production config file
   - Set appropriate thresholds
   - Configure history file location

3. **Set up monitoring:**
   - Configure cron jobs or scheduled tasks
   - Set up CI/CD integration
   - Configure alerting notifications

### Docker Production Deployment

```bash
# Build production image
docker build -t driftlab:latest .

# Run with production config
docker run -v /path/to/data:/app/data \
           -v /path/to/reports:/app/reports \
           -v /path/to/configs:/app/configs \
           driftlab:latest \
           python -m driftlab.run --config configs/production.yaml
```

## Uninstallation

To remove DriftLab:

```bash
# Uninstall package
pip uninstall driftlab

# Remove virtual environment (if used)
rm -rf venv

# Remove Docker image (if used)
docker rmi driftlab
```

## Next Steps

After successful installation:

1. **Read the README**: Review features and usage examples
2. **Try the demo**: Run the quick start test above
3. **Configure for your data**: Update config file with your column types
4. **Integrate into pipeline**: Follow integration guide in README
5. **Set up monitoring**: Configure alerts and scheduled runs

## Getting Help

- **Documentation**: See README.md for detailed usage
- **Issues**: Report problems on GitHub Issues
- **Examples**: Check `configs/demo.yaml` for configuration examples

## System-Specific Notes

### macOS
- Use Homebrew to install Python if needed: `brew install python3`
- May need to install Xcode Command Line Tools: `xcode-select --install`

### Linux
- Install Python development headers: `sudo apt-get install python3-dev` (Ubuntu/Debian)
- Or: `sudo yum install python3-devel` (RHEL/CentOS)

### Windows
- Use Python from python.org or Microsoft Store
- Consider using WSL (Windows Subsystem for Linux) for better compatibility
- Use PowerShell or Git Bash for command-line operations

