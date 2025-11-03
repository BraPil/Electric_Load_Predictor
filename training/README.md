# VoltEdge Model Training

This directory contains the model training pipeline for electric load prediction.

## Structure

- `train_models.py` - Main training script with 5 ML algorithms
- `config.py` - Training configuration and hyperparameters
- `models/` - Individual model implementations
- `utils.py` - Shared training utilities (metrics, evaluation, SHAP)

## Usage

### Train All Models
```bash
python training/train_models.py --input data/processed/household_power_features.parquet
```

### Train Specific Model
```bash
python training/train_models.py --model linear --input data/processed/household_power_features.parquet
```

### Available Models
- `linear` - Linear Regression (baseline)
- `rf` - Random Forest Regressor
- `xgb` - XGBoost Gradient Boosting
- `mlp` - Multi-Layer Perceptron Neural Network
- `lstm` - LSTM Recurrent Neural Network (optional)

## MLflow Integration

All experiments are tracked in MLflow with:
- **Parameters**: Model hyperparameters, feature sets
- **Metrics**: RMSE, MAE, MAPE, R²
- **Artifacts**: Trained models, SHAP plots, backtesting results

Access MLflow UI:
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```

## Output

Trained models are registered in MLflow Model Registry:
- **Staging**: Newly trained models
- **Production**: Champion model after validation
