"""
VoltEdge Model Training Pipeline

Trains multiple ML models for electric load prediction with MLflow tracking.

Models:
- Linear Regression (baseline)
- Random Forest Regressor
- XGBoost Gradient Boosting
- Multi-Layer Perceptron (MLP)
- LSTM Neural Network (optional)

Usage:
    python training/train_models.py --input data/processed/household_power_features.parquet
    python training/train_models.py --model xgb --input data/processed/household_power_features.parquet
"""

import argparse
import logging
import warnings
from pathlib import Path
from typing import Dict, Tuple, Optional
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import shap
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for Windows
import matplotlib.pyplot as plt

# MLflow imports
try:
    import mlflow
    import mlflow.sklearn
    import mlflow.xgboost
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    warnings.warn("MLflow not available. Install with: pip install mlflow")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)


class ModelTrainer:
    """
    Training pipeline for electric load prediction models.
    
    Handles data splitting, model training, evaluation, and MLflow tracking.
    """
    
    def __init__(
        self,
        experiment_name: str = "voltedge-load-prediction",
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42
    ):
        """
        Initialize model trainer.
        
        Args:
            experiment_name: MLflow experiment name
            test_size: Fraction of data for test set
            val_size: Fraction of training data for validation
            random_state: Random seed for reproducibility
        """
        self.experiment_name = experiment_name
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        
        # Initialize MLflow
        if MLFLOW_AVAILABLE:
            mlflow.set_experiment(experiment_name)
            logger.info(f"MLflow experiment set to: {experiment_name}")
        else:
            logger.warning("MLflow not available - metrics will not be tracked")
    
    def prepare_data(
        self, 
        df: pd.DataFrame, 
        target_col: str = 'total_power_kw',
        exclude_cols: list = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """
        Prepare data for training with temporal train/val/test split.
        
        Args:
            df: Input dataframe with features
            target_col: Target variable column name
            exclude_cols: Columns to exclude from features
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        logger.info("Preparing data with temporal splits...")
        
        # Default exclusions - remove target and columns that would cause data leakage
        if exclude_cols is None:
            exclude_cols = [
                'quality_flag',
                # Exclude raw power measurements that are essentially the target
                'Global_active_power',  # Nearly identical to total_power_kw
                'Global_reactive_power',  # Highly correlated
                'Voltage',  # Highly correlated  
                'Global_intensity',  # Highly correlated
                'Sub_metering_1',  # Components of total power
                'Sub_metering_2',  # Components of total power
                'Sub_metering_3'   # Components of total power
            ]
        
        # Separate features and target
        feature_cols = [col for col in df.columns 
                       if col != target_col and col not in exclude_cols]
        
        # Select only numeric columns
        X = df[feature_cols].select_dtypes(include=[np.number])
        y = df[target_col]
        
        logger.info(f"Features: {len(X.columns)} numeric columns")
        logger.info(f"Target: {target_col}")
        logger.info(f"Total records: {len(X)}")
        
        # Temporal split (no shuffling for time series)
        n = len(X)
        test_idx = int(n * (1 - self.test_size))
        train_val_idx = int(test_idx * (1 - self.val_size))
        
        X_train = X.iloc[:train_val_idx]
        X_val = X.iloc[train_val_idx:test_idx]
        X_test = X.iloc[test_idx:]
        
        y_train = y.iloc[:train_val_idx]
        y_val = y.iloc[train_val_idx:test_idx]
        y_test = y.iloc[test_idx:]
        
        logger.info(f"Train: {len(X_train)} ({len(X_train)/n*100:.1f}%)")
        logger.info(f"Val: {len(X_val)} ({len(X_val)/n*100:.1f}%)")
        logger.info(f"Test: {len(X_test)} ({len(X_test)/n*100:.1f}%)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def calculate_metrics(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate regression metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # MAPE (avoiding division by zero)
        mask = y_true != 0
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        
        return {
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'mape': mape
        }
    
    def create_shap_plot(
        self,
        model,
        X_sample: pd.DataFrame,
        model_name: str,
        output_dir: Path
    ) -> Optional[str]:
        """
        Create SHAP summary plot for model explainability.
        
        Args:
            model: Trained model
            X_sample: Sample data for SHAP
            model_name: Model name for filename
            output_dir: Output directory for plots
            
        Returns:
            Path to saved plot or None
        """
        try:
            logger.info(f"Generating SHAP explanations for {model_name}...")
            
            # Create explainer based on model type
            if isinstance(model, (xgb.XGBRegressor, RandomForestRegressor)):
                explainer = shap.TreeExplainer(model)
            else:
                explainer = shap.KernelExplainer(
                    model.predict, 
                    shap.sample(X_sample, 100)
                )
            
            # Calculate SHAP values (sample for speed)
            sample_size = min(1000, len(X_sample))
            X_shap = X_sample.sample(n=sample_size, random_state=self.random_state)
            shap_values = explainer.shap_values(X_shap)
            
            # Create summary plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(
                shap_values, 
                X_shap, 
                show=False,
                max_display=15
            )
            
            # Save plot
            output_dir.mkdir(parents=True, exist_ok=True)
            plot_path = output_dir / f"{model_name}_shap_summary.png"
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"SHAP plot saved to: {plot_path}")
            return str(plot_path)
            
        except Exception as e:
            logger.warning(f"Failed to create SHAP plot: {e}")
            return None
    
    def train_linear_regression(
        self,
        X_train: pd.DataFrame,
        X_val: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_val: pd.Series,
        y_test: pd.Series
    ) -> Dict:
        """Train Linear Regression baseline model."""
        
        model_name = "linear_regression"
        logger.info(f"\n{'='*80}")
        logger.info(f"Training: {model_name}")
        logger.info(f"{'='*80}")
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_run(run_name=model_name):
                # Train model
                model = LinearRegression()
                model.fit(X_train, y_train)
                
                # Predictions
                y_train_pred = model.predict(X_train)
                y_val_pred = model.predict(X_val)
                y_test_pred = model.predict(X_test)
                
                # Metrics
                train_metrics = self.calculate_metrics(y_train, y_train_pred)
                val_metrics = self.calculate_metrics(y_val, y_val_pred)
                test_metrics = self.calculate_metrics(y_test, y_test_pred)
                
                # Log to MLflow
                mlflow.log_params({
                    "model_type": "linear_regression",
                    "n_features": X_train.shape[1]
                })
                
                mlflow.log_metrics({
                    "train_rmse": train_metrics['rmse'],
                    "train_mae": train_metrics['mae'],
                    "train_r2": train_metrics['r2'],
                    "train_mape": train_metrics['mape'],
                    "val_rmse": val_metrics['rmse'],
                    "val_mae": val_metrics['mae'],
                    "val_r2": val_metrics['r2'],
                    "val_mape": val_metrics['mape'],
                    "test_rmse": test_metrics['rmse'],
                    "test_mae": test_metrics['mae'],
                    "test_r2": test_metrics['r2'],
                    "test_mape": test_metrics['mape']
                })
                
                # Log model
                mlflow.sklearn.log_model(model, "model")
                
                # SHAP plot
                shap_path = self.create_shap_plot(
                    model, X_test, model_name, Path("artifacts/shap")
                )
                if shap_path:
                    mlflow.log_artifact(shap_path)
                
                logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
                logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
                
                return {
                    'model': model,
                    'train_metrics': train_metrics,
                    'val_metrics': val_metrics,
                    'test_metrics': test_metrics
                }
        else:
            # Train without MLflow
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            y_val_pred = model.predict(X_val)
            y_test_pred = model.predict(X_test)
            
            val_metrics = self.calculate_metrics(y_val, y_val_pred)
            test_metrics = self.calculate_metrics(y_test, y_test_pred)
            
            logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
            logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
            
            return {
                'model': model,
                'val_metrics': val_metrics,
                'test_metrics': test_metrics
            }
    
    def train_random_forest(
        self,
        X_train: pd.DataFrame,
        X_val: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_val: pd.Series,
        y_test: pd.Series
    ) -> Dict:
        """Train Random Forest model."""
        
        model_name = "random_forest"
        logger.info(f"\n{'='*80}")
        logger.info(f"Training: {model_name}")
        logger.info(f"{'='*80}")
        
        # Hyperparameters
        params = {
            'n_estimators': 100,
            'max_depth': 15,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': self.random_state,
            'n_jobs': -1
        }
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_run(run_name=model_name):
                # Train model
                model = RandomForestRegressor(**params)
                model.fit(X_train, y_train)
                
                # Predictions
                y_train_pred = model.predict(X_train)
                y_val_pred = model.predict(X_val)
                y_test_pred = model.predict(X_test)
                
                # Metrics
                train_metrics = self.calculate_metrics(y_train, y_train_pred)
                val_metrics = self.calculate_metrics(y_val, y_val_pred)
                test_metrics = self.calculate_metrics(y_test, y_test_pred)
                
                # Log to MLflow
                mlflow.log_params(params)
                mlflow.log_params({
                    "model_type": "random_forest",
                    "n_features": X_train.shape[1]
                })
                
                mlflow.log_metrics({
                    "train_rmse": train_metrics['rmse'],
                    "train_mae": train_metrics['mae'],
                    "train_r2": train_metrics['r2'],
                    "train_mape": train_metrics['mape'],
                    "val_rmse": val_metrics['rmse'],
                    "val_mae": val_metrics['mae'],
                    "val_r2": val_metrics['r2'],
                    "val_mape": val_metrics['mape'],
                    "test_rmse": test_metrics['rmse'],
                    "test_mae": test_metrics['mae'],
                    "test_r2": test_metrics['r2'],
                    "test_mape": test_metrics['mape']
                })
                
                # Log model
                mlflow.sklearn.log_model(model, "model")
                
                # Feature importance
                feature_importance = pd.DataFrame({
                    'feature': X_train.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                importance_path = Path("artifacts/feature_importance")
                importance_path.mkdir(parents=True, exist_ok=True)
                importance_file = importance_path / f"{model_name}_importance.csv"
                feature_importance.to_csv(importance_file, index=False)
                mlflow.log_artifact(str(importance_file))
                
                # SHAP plot
                shap_path = self.create_shap_plot(
                    model, X_test, model_name, Path("artifacts/shap")
                )
                if shap_path:
                    mlflow.log_artifact(shap_path)
                
                logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
                logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
                
                return {
                    'model': model,
                    'train_metrics': train_metrics,
                    'val_metrics': val_metrics,
                    'test_metrics': test_metrics,
                    'feature_importance': feature_importance
                }
        else:
            # Train without MLflow
            model = RandomForestRegressor(**params)
            model.fit(X_train, y_train)
            
            y_val_pred = model.predict(X_val)
            y_test_pred = model.predict(X_test)
            
            val_metrics = self.calculate_metrics(y_val, y_val_pred)
            test_metrics = self.calculate_metrics(y_test, y_test_pred)
            
            logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
            logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
            
            return {
                'model': model,
                'val_metrics': val_metrics,
                'test_metrics': test_metrics
            }
    
    def train_xgboost(
        self,
        X_train: pd.DataFrame,
        X_val: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_val: pd.Series,
        y_test: pd.Series
    ) -> Dict:
        """Train XGBoost Gradient Boosting model."""
        
        model_name = "xgboost"
        logger.info(f"\n{'='*80}")
        logger.info(f"Training: {model_name}")
        logger.info(f"{'='*80}")
        
        # Hyperparameters
        params = {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': self.random_state,
            'n_jobs': -1
        }
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_run(run_name=model_name):
                # Train model
                model = xgb.XGBRegressor(**params)
                model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
                
                # Predictions
                y_train_pred = model.predict(X_train)
                y_val_pred = model.predict(X_val)
                y_test_pred = model.predict(X_test)
                
                # Metrics
                train_metrics = self.calculate_metrics(y_train, y_train_pred)
                val_metrics = self.calculate_metrics(y_val, y_val_pred)
                test_metrics = self.calculate_metrics(y_test, y_test_pred)
                
                # Log to MLflow
                mlflow.log_params(params)
                mlflow.log_params({
                    "model_type": "xgboost",
                    "n_features": X_train.shape[1]
                })
                
                mlflow.log_metrics({
                    "train_rmse": train_metrics['rmse'],
                    "train_mae": train_metrics['mae'],
                    "train_r2": train_metrics['r2'],
                    "train_mape": train_metrics['mape'],
                    "val_rmse": val_metrics['rmse'],
                    "val_mae": val_metrics['mae'],
                    "val_r2": val_metrics['r2'],
                    "val_mape": val_metrics['mape'],
                    "test_rmse": test_metrics['rmse'],
                    "test_mae": test_metrics['mae'],
                    "test_r2": test_metrics['r2'],
                    "test_mape": test_metrics['mape']
                })
                
                # Log model
                mlflow.xgboost.log_model(model, "model")
                
                # Feature importance
                feature_importance = pd.DataFrame({
                    'feature': X_train.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                importance_path = Path("artifacts/feature_importance")
                importance_path.mkdir(parents=True, exist_ok=True)
                importance_file = importance_path / f"{model_name}_importance.csv"
                feature_importance.to_csv(importance_file, index=False)
                mlflow.log_artifact(str(importance_file))
                
                # SHAP plot
                shap_path = self.create_shap_plot(
                    model, X_test, model_name, Path("artifacts/shap")
                )
                if shap_path:
                    mlflow.log_artifact(shap_path)
                
                logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
                logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
                
                return {
                    'model': model,
                    'train_metrics': train_metrics,
                    'val_metrics': val_metrics,
                    'test_metrics': test_metrics,
                    'feature_importance': feature_importance
                }
        else:
            # Train without MLflow
            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
            
            y_val_pred = model.predict(X_val)
            y_test_pred = model.predict(X_test)
            
            val_metrics = self.calculate_metrics(y_val, y_val_pred)
            test_metrics = self.calculate_metrics(y_test, y_test_pred)
            
            logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
            logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
            
            return {
                'model': model,
                'val_metrics': val_metrics,
                'test_metrics': test_metrics
            }
    
    def train_mlp(
        self,
        X_train: pd.DataFrame,
        X_val: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_val: pd.Series,
        y_test: pd.Series
    ) -> Dict:
        """Train Multi-Layer Perceptron neural network."""
        
        model_name = "mlp"
        logger.info(f"\n{'='*80}")
        logger.info(f"Training: {model_name}")
        logger.info(f"{'='*80}")
        
        # Hyperparameters
        params = {
            'hidden_layer_sizes': (100, 50, 25),
            'activation': 'relu',
            'solver': 'adam',
            'alpha': 0.0001,
            'batch_size': 64,
            'learning_rate': 'adaptive',
            'max_iter': 200,
            'random_state': self.random_state,
            'early_stopping': True,
            'validation_fraction': 0.1,
            'verbose': False
        }
        
        if MLFLOW_AVAILABLE:
            with mlflow.start_run(run_name=model_name):
                # Train model
                model = MLPRegressor(**params)
                model.fit(X_train, y_train)
                
                # Predictions
                y_train_pred = model.predict(X_train)
                y_val_pred = model.predict(X_val)
                y_test_pred = model.predict(X_test)
                
                # Metrics
                train_metrics = self.calculate_metrics(y_train, y_train_pred)
                val_metrics = self.calculate_metrics(y_val, y_val_pred)
                test_metrics = self.calculate_metrics(y_test, y_test_pred)
                
                # Log to MLflow
                mlflow.log_params(params)
                mlflow.log_params({
                    "model_type": "mlp",
                    "n_features": X_train.shape[1],
                    "n_iterations": model.n_iter_
                })
                
                mlflow.log_metrics({
                    "train_rmse": train_metrics['rmse'],
                    "train_mae": train_metrics['mae'],
                    "train_r2": train_metrics['r2'],
                    "train_mape": train_metrics['mape'],
                    "val_rmse": val_metrics['rmse'],
                    "val_mae": val_metrics['mae'],
                    "val_r2": val_metrics['r2'],
                    "val_mape": val_metrics['mape'],
                    "test_rmse": test_metrics['rmse'],
                    "test_mae": test_metrics['mae'],
                    "test_r2": test_metrics['r2'],
                    "test_mape": test_metrics['mape']
                })
                
                # Log model
                mlflow.sklearn.log_model(model, "model")
                
                logger.info(f"Training completed in {model.n_iter_} iterations")
                logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
                logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
                
                return {
                    'model': model,
                    'train_metrics': train_metrics,
                    'val_metrics': val_metrics,
                    'test_metrics': test_metrics
                }
        else:
            # Train without MLflow
            model = MLPRegressor(**params)
            model.fit(X_train, y_train)
            
            y_val_pred = model.predict(X_val)
            y_test_pred = model.predict(X_test)
            
            val_metrics = self.calculate_metrics(y_val, y_val_pred)
            test_metrics = self.calculate_metrics(y_test, y_test_pred)
            
            logger.info(f"Val RMSE: {val_metrics['rmse']:.4f}, R²: {val_metrics['r2']:.4f}")
            logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}, R²: {test_metrics['r2']:.4f}")
            
            return {
                'model': model,
                'val_metrics': val_metrics,
                'test_metrics': test_metrics
            }


def main():
    """Main training pipeline."""
    
    parser = argparse.ArgumentParser(description="Train VoltEdge load prediction models")
    parser.add_argument(
        '--input',
        type=str,
        default='data/processed/household_power_features.parquet',
        help='Path to feature parquet file'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['linear', 'rf', 'xgb', 'mlp', 'all'],
        default='all',
        help='Model to train (default: all)'
    )
    parser.add_argument(
        '--experiment',
        type=str,
        default='voltedge-load-prediction',
        help='MLflow experiment name'
    )
    
    args = parser.parse_args()
    
    # Load data
    logger.info(f"Loading data from: {args.input}")
    df = pd.read_parquet(args.input)
    logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
    
    # Initialize trainer
    trainer = ModelTrainer(experiment_name=args.experiment)
    
    # Prepare data
    X_train, X_val, X_test, y_train, y_val, y_test = trainer.prepare_data(df)
    
    # Train models
    results = {}
    
    if args.model == 'all' or args.model == 'linear':
        results['linear'] = trainer.train_linear_regression(
            X_train, X_val, X_test, y_train, y_val, y_test
        )
    
    if args.model == 'all' or args.model == 'rf':
        results['rf'] = trainer.train_random_forest(
            X_train, X_val, X_test, y_train, y_val, y_test
        )
    
    if args.model == 'all' or args.model == 'xgb':
        results['xgb'] = trainer.train_xgboost(
            X_train, X_val, X_test, y_train, y_val, y_test
        )
    
    if args.model == 'all' or args.model == 'mlp':
        results['mlp'] = trainer.train_mlp(
            X_train, X_val, X_test, y_train, y_val, y_test
        )
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("TRAINING SUMMARY")
    logger.info(f"{'='*80}")
    
    summary_df = pd.DataFrame({
        model: {
            'Val RMSE': res['val_metrics']['rmse'],
            'Val MAE': res['val_metrics']['mae'],
            'Val R²': res['val_metrics']['r2'],
            'Val MAPE': res['val_metrics']['mape'],
            'Test RMSE': res['test_metrics']['rmse'],
            'Test MAE': res['test_metrics']['mae'],
            'Test R²': res['test_metrics']['r2'],
            'Test MAPE': res['test_metrics']['mape']
        }
        for model, res in results.items()
    }).T
    
    print("\n" + summary_df.to_string())
    
    # Identify champion model (best validation RMSE)
    if results:
        champion = min(results.items(), key=lambda x: x[1]['val_metrics']['rmse'])
        logger.info(f"\nChampion Model: {champion[0].upper()}")
        logger.info(f"Val RMSE: {champion[1]['val_metrics']['rmse']:.4f}")
        logger.info(f"Test RMSE: {champion[1]['test_metrics']['rmse']:.4f}")
    
    logger.info(f"\n{'='*80}")
    logger.info("TRAINING COMPLETE")
    logger.info(f"{'='*80}")
    
    if MLFLOW_AVAILABLE:
        logger.info("\nView results in MLflow UI:")
        logger.info("  mlflow ui")
    
    return results


if __name__ == '__main__':
    main()
