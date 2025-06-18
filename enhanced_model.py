"""
Enhanced Machine Learning Model with Advanced Algorithms
Supports multiple algorithms, anomaly detection, and model evaluation
"""
import numpy as np
import pandas as pd
import logging
import pickle
import warnings
from datetime import datetime
from typing import Tuple, Dict, Any, List, Optional
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    precision_recall_fscore_support, roc_auc_score
)
import joblib

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedLogAnalysisModel:
    def __init__(self):
        """Initialize the Enhanced Log Analysis Model"""
        self.classification_models = {}
        self.anomaly_models = {}
        self.model_performance = {}
        self.label_encoders = {}
        self.is_trained = False

    def load_processed_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load preprocessed data"""
        try:
            X_train = np.load('X_train_enhanced.npy')
            X_test = np.load('X_test_enhanced.npy')
            y_train = np.load('y_train_enhanced.npy')
            y_test = np.load('y_test_enhanced.npy')
            
            # Load preprocessing objects
            with open('preprocessor_objects.pkl', 'rb') as f:
                objects = pickle.load(f)
                self.label_encoders = objects['label_encoders']
            
            logger.info("✅ Processed data loaded successfully")
            return X_train, X_test, y_train, y_test
            
        except FileNotFoundError:
            logger.error("No processed data found. Please run preprocessing first.")
            raise

    def train_classification_models(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """
        Train multiple classification models
        
        Args:
            X_train: Training features
            y_train: Training labels
            
        Returns:
            Dictionary of trained models
        """
        logger.info("Training classification models...")
        
        # Define models to train
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'logistic_regression': LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='ovr'
            ),
            'mlp_classifier': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                max_iter=500,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        }
        
        # Train each model
        for name, model in models.items():
            logger.info(f"Training {name}...")
            try:
                model.fit(X_train, y_train)
                self.classification_models[name] = model
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
                logger.info(f"{name} - CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
                
            except Exception as e:
                logger.error(f"Failed to train {name}: {e}")
        
        return self.classification_models

    def train_anomaly_detection_models(self, X_train: np.ndarray) -> Dict[str, Any]:
        """
        Train anomaly detection models
        
        Args:
            X_train: Training features (normal data only)
            
        Returns:
            Dictionary of trained anomaly models
        """
        logger.info("Training anomaly detection models...")
        
        # Define anomaly detection models
        anomaly_models = {
            'isolation_forest': IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_jobs=-1
            ),
            'one_class_svm': OneClassSVM(
                nu=0.1,  # Expected fraction of outliers
                kernel='rbf',
                gamma='scale'
            )
        }
        
        # Train each anomaly model
        for name, model in anomaly_models.items():
            logger.info(f"Training {name}...")
            try:
                model.fit(X_train)
                self.anomaly_models[name] = model
                
                # Get anomaly scores for training data
                if hasattr(model, 'decision_function'):
                    scores = model.decision_function(X_train)
                    anomaly_ratio = np.sum(scores < 0) / len(scores)
                    logger.info(f"{name} - Detected {anomaly_ratio:.2%} anomalies in training data")
                
            except Exception as e:
                logger.error(f"Failed to train {name}: {e}")
        
        return self.anomaly_models

    def evaluate_classification_models(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Dict]:
        """
        Evaluate classification models
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary of model performance metrics
        """
        logger.info("Evaluating classification models...")
        
        performance = {}
        
        for name, model in self.classification_models.items():
            logger.info(f"Evaluating {name}...")
            
            try:
                # Predictions
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
                
                # Basic metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
                
                # ROC AUC (for multiclass)
                try:
                    if y_pred_proba is not None:
                        auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
                    else:
                        auc = None
                except:
                    auc = None
                
                performance[name] = {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'auc': auc,
                    'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                    'classification_report': classification_report(y_test, y_pred, output_dict=True)
                }
                
                logger.info(f"{name} - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
                
            except Exception as e:
                logger.error(f"Failed to evaluate {name}: {e}")
                performance[name] = {'error': str(e)}
        
        self.model_performance = performance
        return performance

    def evaluate_anomaly_models(self, X_test: np.ndarray) -> Dict[str, Dict]:
        """
        Evaluate anomaly detection models
        
        Args:
            X_test: Test features
            
        Returns:
            Dictionary of anomaly detection results
        """
        logger.info("Evaluating anomaly detection models...")
        
        anomaly_results = {}
        
        for name, model in self.anomaly_models.items():
            logger.info(f"Evaluating {name}...")
            
            try:
                # Predict anomalies
                anomaly_pred = model.predict(X_test)
                anomaly_scores = model.decision_function(X_test) if hasattr(model, 'decision_function') else None
                
                # Calculate metrics
                anomaly_ratio = np.sum(anomaly_pred == -1) / len(anomaly_pred)
                
                anomaly_results[name] = {
                    'anomaly_predictions': anomaly_pred.tolist(),
                    'anomaly_scores': anomaly_scores.tolist() if anomaly_scores is not None else None,
                    'anomaly_ratio': anomaly_ratio,
                    'num_anomalies': np.sum(anomaly_pred == -1)
                }
                
                logger.info(f"{name} - Detected {anomaly_ratio:.2%} anomalies in test data")
                
            except Exception as e:
                logger.error(f"Failed to evaluate {name}: {e}")
                anomaly_results[name] = {'error': str(e)}
        
        return anomaly_results

    def hyperparameter_tuning(self, X_train: np.ndarray, y_train: np.ndarray, 
                             model_name: str = 'random_forest') -> Dict[str, Any]:
        """
        Perform hyperparameter tuning for a specific model
        
        Args:
            X_train: Training features
            y_train: Training labels
            model_name: Name of the model to tune
            
        Returns:
            Best parameters and model
        """
        logger.info(f"Performing hyperparameter tuning for {model_name}...")
        
        if model_name == 'random_forest':
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 15, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
            
        elif model_name == 'logistic_regression':
            param_grid = {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
            base_model = LogisticRegression(max_iter=1000, random_state=42)
            
        else:
            logger.warning(f"Hyperparameter tuning not implemented for {model_name}")
            return {}
        
        try:
            # Grid search with cross-validation
            grid_search = GridSearchCV(
                base_model, 
                param_grid, 
                cv=5, 
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            
            # Update the model with best parameters
            self.classification_models[f'{model_name}_tuned'] = grid_search.best_estimator_
            
            results = {
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'best_model': grid_search.best_estimator_
            }
            
            logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
            logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Hyperparameter tuning failed for {model_name}: {e}")
            return {}

    def predict_log_level(self, features: np.ndarray, model_name: str = 'random_forest') -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict log levels for new data
        
        Args:
            features: Input features
            model_name: Name of the model to use
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        if model_name not in self.classification_models:
            raise ValueError(f"Model '{model_name}' not found. Available models: {list(self.classification_models.keys())}")
        
        model = self.classification_models[model_name]
        predictions = model.predict(features)
        probabilities = model.predict_proba(features) if hasattr(model, 'predict_proba') else None
        
        return predictions, probabilities

    def detect_anomalies(self, features: np.ndarray, model_name: str = 'isolation_forest') -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies in new data
        
        Args:
            features: Input features
            model_name: Name of the anomaly model to use
            
        Returns:
            Tuple of (anomaly_predictions, anomaly_scores)
        """
        if model_name not in self.anomaly_models:
            raise ValueError(f"Anomaly model '{model_name}' not found. Available models: {list(self.anomaly_models.keys())}")
        
        model = self.anomaly_models[model_name]
        anomaly_predictions = model.predict(features)
        anomaly_scores = model.decision_function(features) if hasattr(model, 'decision_function') else None
        
        return anomaly_predictions, anomaly_scores

    def save_models(self, filepath_prefix: str = 'enhanced_models'):
        """Save all trained models"""
        try:
            # Save classification models
            for name, model in self.classification_models.items():
                joblib.dump(model, f'{filepath_prefix}_classification_{name}.pkl')
            
            # Save anomaly models
            for name, model in self.anomaly_models.items():
                joblib.dump(model, f'{filepath_prefix}_anomaly_{name}.pkl')
            
            # Save performance metrics
            with open(f'{filepath_prefix}_performance.pkl', 'wb') as f:
                pickle.dump(self.model_performance, f)
            
            logger.info("✅ All models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")

    def load_models(self, filepath_prefix: str = 'enhanced_models'):
        """Load previously trained models"""
        try:
            import glob
            
            # Load classification models
            classification_files = glob.glob(f'{filepath_prefix}_classification_*.pkl')
            for filepath in classification_files:
                name = filepath.split('_classification_')[1].replace('.pkl', '')
                self.classification_models[name] = joblib.load(filepath)
            
            # Load anomaly models
            anomaly_files = glob.glob(f'{filepath_prefix}_anomaly_*.pkl')
            for filepath in anomaly_files:
                name = filepath.split('_anomaly_')[1].replace('.pkl', '')
                self.anomaly_models[name] = joblib.load(filepath)
            
            # Load performance metrics
            try:
                with open(f'{filepath_prefix}_performance.pkl', 'rb') as f:
                    self.model_performance = pickle.load(f)
            except FileNotFoundError:
                logger.warning("Performance metrics file not found")
            
            self.is_trained = True
            logger.info("✅ All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")

    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary of all trained models"""
        summary = {
            'classification_models': list(self.classification_models.keys()),
            'anomaly_models': list(self.anomaly_models.keys()),
            'performance': self.model_performance,
            'is_trained': self.is_trained
        }
        return summary

def main():
    """Main function to train and evaluate enhanced models"""
    model_trainer = EnhancedLogAnalysisModel()
    
    try:
        # Load processed data
        X_train, X_test, y_train, y_test = model_trainer.load_processed_data()
        
        # Train classification models
        classification_models = model_trainer.train_classification_models(X_train, y_train)
        
        # Train anomaly detection models
        anomaly_models = model_trainer.train_anomaly_detection_models(X_train)
        
        # Evaluate classification models
        classification_performance = model_trainer.evaluate_classification_models(X_test, y_test)
        
        # Evaluate anomaly detection models
        anomaly_results = model_trainer.evaluate_anomaly_models(X_test)
        
        # Hyperparameter tuning for best model
        tuning_results = model_trainer.hyperparameter_tuning(X_train, y_train, 'random_forest')
        
        # Save all models
        model_trainer.save_models()
        
        # Print summary
        print("✅ Enhanced model training completed successfully!")
        print(f"\nClassification Models Trained: {len(classification_models)}")
        print(f"Anomaly Detection Models Trained: {len(anomaly_models)}")
        
        print("\n=== Classification Performance ===")
        for name, perf in classification_performance.items():
            if 'error' not in perf:
                print(f"{name}: Accuracy={perf['accuracy']:.4f}, F1={perf['f1_score']:.4f}")
        
        print("\n=== Anomaly Detection Results ===")
        for name, results in anomaly_results.items():
            if 'error' not in results:
                print(f"{name}: {results['anomaly_ratio']:.2%} anomalies detected")
        
        if tuning_results:
            print(f"\n=== Hyperparameter Tuning ===")
            print(f"Best CV Score: {tuning_results['best_score']:.4f}")
            print(f"Best Parameters: {tuning_results['best_params']}")
        
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        print("❌ Enhanced model training failed!")

if __name__ == "__main__":
    main()

