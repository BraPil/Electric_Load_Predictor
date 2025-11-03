# VoltEdge Setup Instructions (Windows with Conda)

## Prerequisites Checklist

Before starting, install these tools:

- [ ] **Miniconda** - https://docs.conda.io/en/latest/miniconda.html
- [ ] **Docker Desktop** - https://www.docker.com/products/docker-desktop/
- [ ] **Git** - https://git-scm.com/download/win (likely already installed)

## Step-by-Step Setup

### 1. Install Miniconda (if not installed)

```powershell
# Download from: https://docs.conda.io/en/latest/miniconda.html
# Choose: Miniconda3 Windows 64-bit

# After installation, close ALL PowerShell windows and open a NEW one

# Verify installation
conda --version
# Should show: conda 23.x.x or higher
```

### 2. Create Conda Environment

```powershell
# Navigate to project directory
cd "C:\Users\BDPILEGG\OneDrive - Southern Company\Desktop\Electric_Load_Predictor"

# Create environment (installs Python 3.11 + all dependencies)
# This takes 5-10 minutes
conda env create -f environment.yml

# Activate environment
conda activate voltedge

# Verify Python version
python --version
# Should show: Python 3.11.x
```

### 3. Test Ingestion Pipeline (No Docker Required)

```powershell
# Make sure voltedge environment is activated
conda activate voltedge

# Run quick test (processes 10,000 rows)
python scripts/test_ingestion.py --limit 10000

# Expected output:
# ✓ Download UCI Dataset: PASS
# ✓ ETL Pipeline: PASS
# ✓ Data Validation: PASS
# ✓ Output Files Check: PASS
# ✅ All tests PASSED!
```

### 4. Install Docker Desktop (if not installed)

```powershell
# Download from: https://www.docker.com/products/docker-desktop/

# After installation:
# 1. Restart computer
# 2. Launch Docker Desktop
# 3. Wait for whale icon 🐋 in system tray

# Verify installation (in NEW PowerShell window)
docker --version
# Should show: Docker version 24.x.x

docker compose version
# Should show: Docker Compose version v2.x.x
```

### 5. Start Docker Services

```powershell
# Make sure Docker Desktop is running (whale icon in tray)

# Start all services (Postgres, MLflow, MinIO, Redis)
docker compose -f docker/docker-compose.yml up -d

# Check services are running
docker compose -f docker/docker-compose.yml ps

# Expected output:
# NAME                STATUS
# voltedge-postgres   running (healthy)
# voltedge-mlflow     running (healthy)
# voltedge-minio      running (healthy)
# voltedge-redis      running (healthy)
```

### 6. Create MLflow Bucket in MinIO

```powershell
# Open MinIO web interface
# Browser: http://localhost:9000

# Login credentials:
# Username: minioadmin
# Password: minioadmin

# Click "Create Bucket"
# Bucket name: mlflow
# Click "Create"
```

### 7. Run Full Ingestion Test (With Database)

```powershell
# Activate environment
conda activate voltedge

# Run full test (processes all ~2M records → 35K hourly)
python scripts/test_ingestion.py

# This will:
# ✓ Download dataset (~20MB)
# ✓ Process 2M+ records
# ✓ Load to PostgreSQL database
# ✓ Save to Parquet file
# ✓ Validate data quality
# ✓ Generate test report

# Takes 2-3 minutes
```

## Quick Reference Commands

### Conda Environment

```powershell
# Activate environment (do this every session!)
conda activate voltedge

# Deactivate
conda deactivate

# Update environment after changing environment.yml
conda env update -f environment.yml --prune

# Remove and recreate environment
conda env remove -n voltedge
conda env create -f environment.yml
```

### Docker Services

```powershell
# Start services
docker compose -f docker/docker-compose.yml up -d

# Stop services
docker compose -f docker/docker-compose.yml down

# View logs (live)
docker compose -f docker/docker-compose.yml logs -f

# Check service status
docker compose -f docker/docker-compose.yml ps

# Restart a service
docker compose -f docker/docker-compose.yml restart postgres
```

### Ingestion Pipeline

```powershell
# Activate environment first!
conda activate voltedge

# Quick test (10k rows, ~30 seconds)
python scripts/test_ingestion.py --limit 10000

# Full test (2M rows, ~3 minutes)
python scripts/test_ingestion.py

# Just download dataset
python ingestion/fetch_uci.py

# Just run ETL
python ingestion/etl.py --input data/raw/household_power.zip

# ETL without database (files only)
python ingestion/etl.py --input data/raw/household_power.zip --skip-db
```

## Service URLs

Once Docker is running:

| Service | URL | Credentials |
|---------|-----|-------------|
| MinIO Console | http://localhost:9000 | minioadmin / minioadmin |
| MLflow UI | http://localhost:5000 | (none) |
| PostgreSQL | localhost:5432 | voltedge / voltedge |
| Redis | localhost:6379 | (none) |

## Troubleshooting

### "conda: command not found"
**Solution**: Close all PowerShell windows and open new one. Restart computer if needed.

### "Environment creation failed"
**Solution**: 
```powershell
conda clean --all
conda env create -f environment.yml
```

### "Docker container unhealthy"
**Solution**:
```powershell
# Check logs
docker compose -f docker/docker-compose.yml logs <service-name>

# Restart service
docker compose -f docker/docker-compose.yml restart <service-name>

# Nuclear option: remove all and start fresh
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up -d
```

### "Cannot connect to database"
**Solution**:
```powershell
# Make sure Docker is running
docker compose -f docker/docker-compose.yml ps

# Check Postgres specifically
docker compose -f docker/docker-compose.yml logs postgres

# Test database connection
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql+psycopg2://voltedge:voltedge@localhost:5432/voltedge'); print('✓ Connected!' if engine.connect() else '✗ Failed')"
```

## Next Steps

After successful setup:

1. ✅ **Explore the data**
   ```powershell
   # Load processed data
   python -c "import pandas as pd; df = pd.read_parquet('data/processed/household_power_hourly.parquet'); print(df.head())"
   ```

2. ✅ **Move to Phase 3** - Feature Engineering
   - Create lag features
   - Calculate rolling statistics
   - Extract seasonal patterns

3. ✅ **Move to Phase 5** - Build Prediction API
   - FastAPI service
   - Prediction endpoints
   - Model serving

## Help & Documentation

- **Conda Setup**: See `CONDA_SETUP_GUIDE.md`
- **Docker Setup**: See `DOCKER_SETUP_GUIDE.md`
- **Ingestion Pipeline**: See `ingestion/README.md`
- **Learning Guide**: See `LEARNING_SUMMARY.md`

---

**Need help?** Check the troubleshooting sections in the guides above or review the logs in `ingestion_test.log`.
