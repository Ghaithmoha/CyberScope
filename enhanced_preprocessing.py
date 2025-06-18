"""
Enhanced Preprocessing Module with NLP and Advanced Feature Extraction
Supports BERT embeddings, TF-IDF, and anomaly detection preprocessing
"""
import pandas as pd
import numpy as np
import logging
import pickle
import warnings
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import torch
from transformers import AutoTokenizer, AutoModel
import re

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedLogPreprocessor:
    def __init__(self, bert_model_name: str = 'distilbert-base-uncased'):
        """
        Initialize the Enhanced Log Preprocessor
        
        Args:
            bert_model_name: Name of the BERT model to use for embeddings
        """
        self.bert_model_name = bert_model_name
        self.tokenizer = None
        self.bert_model = None
        self.label_encoders = {}
        self.tfidf_vectorizer = None
        self.scaler = StandardScaler()
        self.use_bert = False
        
        # Try to initialize BERT model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(bert_model_name)
            self.bert_model = AutoModel.from_pretrained(bert_model_name)
            self.use_bert = True
            logger.info(f"BERT model '{bert_model_name}' loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load BERT model: {e}. Using TF-IDF instead.")
            self.use_bert = False

    def clean_log_message(self, message: str) -> str:
        """
        Clean and normalize log messages
        
        Args:
            message: Raw log message
            
        Returns:
            Cleaned message
        """
        if pd.isna(message) or not isinstance(message, str):
            return ""
        
        # Convert to lowercase
        message = message.lower()
        
        # Remove timestamps, IDs, and other variable parts
        message = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', '[TIMESTAMP]', message)
        message = re.sub(r'\b\d+\.\d+\.\d+\.\d+\b', '[IP]', message)  # IP addresses
        message = re.sub(r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b', '[UUID]', message)  # UUIDs
        message = re.sub(r'\b\d+\b', '[NUM]', message)  # Numbers
        message = re.sub(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '[EMAIL]', message)  # Emails
        message = re.sub(r'\b(user_|order_|sess_|req_|log_|client_|srv_|vol_|q_|cache_)\w+', '[ID]', message)  # IDs
        
        # Remove extra whitespace
        message = re.sub(r'\s+', ' ', message).strip()
        
        return message

    def extract_temporal_features(self, timestamps: pd.Series) -> pd.DataFrame:
        """
        Extract temporal features from timestamps
        
        Args:
            timestamps: Series of timestamp strings
            
        Returns:
            DataFrame with temporal features
        """
        temporal_features = pd.DataFrame()
        
        # Convert to datetime
        dt_series = pd.to_datetime(timestamps)
        
        temporal_features['hour'] = dt_series.dt.hour
        temporal_features['day_of_week'] = dt_series.dt.dayofweek
        temporal_features['is_weekend'] = (dt_series.dt.dayofweek >= 5).astype(int)
        temporal_features['is_business_hours'] = ((dt_series.dt.hour >= 9) & (dt_series.dt.hour <= 17)).astype(int)
        temporal_features['is_night'] = ((dt_series.dt.hour >= 22) | (dt_series.dt.hour <= 6)).astype(int)
        
        return temporal_features

    def get_bert_embeddings(self, messages: List[str], max_length: int = 128) -> np.ndarray:
        """
        Get BERT embeddings for log messages
        
        Args:
            messages: List of log messages
            max_length: Maximum sequence length for BERT
            
        Returns:
            Array of BERT embeddings
        """
        if not self.use_bert:
            logger.warning("BERT model not available")
            return np.array([])
        
        embeddings = []
        batch_size = 32
        
        logger.info(f"Generating BERT embeddings for {len(messages)} messages")
        
        for i in range(0, len(messages), batch_size):
            batch_messages = messages[i:i + batch_size]
            
            # Tokenize
            inputs = self.tokenizer(
                batch_messages,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors='pt'
            )
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # Use [CLS] token embedding (first token)
                batch_embeddings = outputs.last_hidden_state[:, 0, :].numpy()
                embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)

    def get_tfidf_features(self, messages: List[str], max_features: int = 1000) -> np.ndarray:
        """
        Get TF-IDF features for log messages
        
        Args:
            messages: List of log messages
            max_features: Maximum number of TF-IDF features
            
        Returns:
            Array of TF-IDF features
        """
        if self.tfidf_vectorizer is None:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
            tfidf_features = self.tfidf_vectorizer.fit_transform(messages)
        else:
            tfidf_features = self.tfidf_vectorizer.transform(messages)
        
        return tfidf_features.toarray()

    def encode_categorical_features(self, df: pd.DataFrame, categorical_columns: List[str]) -> pd.DataFrame:
        """
        Encode categorical features using label encoding
        
        Args:
            df: Input DataFrame
            categorical_columns: List of categorical column names
            
        Returns:
            DataFrame with encoded categorical features
        """
        encoded_df = df.copy()
        
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    encoded_df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Handle unseen categories
                    unique_values = set(df[col].astype(str).unique())
                    known_values = set(self.label_encoders[col].classes_)
                    new_values = unique_values - known_values
                    
                    if new_values:
                        # Add new categories to the encoder
                        all_values = list(known_values) + list(new_values)
                        self.label_encoders[col].classes_ = np.array(all_values)
                    
                    encoded_df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        return encoded_df

    def detect_anomalous_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect and flag anomalous patterns in logs
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with anomaly flags
        """
        anomaly_df = df.copy()
        
        # Flag logs with anomaly_type column (from synthetic data)
        if 'anomaly_type' in df.columns:
            anomaly_df['is_anomaly'] = (~df['anomaly_type'].isna()).astype(int)
        else:
            anomaly_df['is_anomaly'] = 0
        
        # Additional anomaly detection based on patterns
        if 'timestamp' in df.columns:
            dt_series = pd.to_datetime(df['timestamp'])
            
            # Flag unusual timing (night hours)
            anomaly_df['unusual_timing'] = ((dt_series.dt.hour >= 22) | (dt_series.dt.hour <= 6)).astype(int)
            
            # Flag high frequency of errors
            if 'level' in df.columns:
                error_counts = df[df['level'] == 'ERROR'].groupby(dt_series.dt.floor('H')).size()
                high_error_hours = error_counts[error_counts > error_counts.quantile(0.95)].index
                anomaly_df['high_error_period'] = dt_series.dt.floor('H').isin(high_error_hours).astype(int)
        
        return anomaly_df

    def preprocess_logs(self, 
                       file_path: str, 
                       use_bert: bool = True,
                       test_size: float = 0.2,
                       save_processed: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Main preprocessing function
        
        Args:
            file_path: Path to the log CSV file
            use_bert: Whether to use BERT embeddings
            test_size: Proportion of data for testing
            save_processed: Whether to save processed data
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        logger.info(f"Starting log preprocessing from '{file_path}'")
        
        # Load data
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} log entries")
        except FileNotFoundError:
            logger.error(f"File '{file_path}' not found")
            raise
        
        # Clean messages
        if 'message' in df.columns:
            df['cleaned_message'] = df['message'].apply(self.clean_log_message)
        else:
            logger.error("No 'message' column found in the data")
            raise ValueError("Missing 'message' column")
        
        # Extract temporal features
        if 'timestamp' in df.columns:
            temporal_features = self.extract_temporal_features(df['timestamp'])
            df = pd.concat([df, temporal_features], axis=1)
        
        # Detect anomalous patterns
        df = self.detect_anomalous_patterns(df)
        
        # Encode categorical features
        categorical_columns = ['level', 'source']
        df = self.encode_categorical_features(df, categorical_columns)
        
        # Prepare features
        feature_columns = []
        
        # Add temporal features
        temporal_cols = ['hour', 'day_of_week', 'is_weekend', 'is_business_hours', 'is_night']
        feature_columns.extend([col for col in temporal_cols if col in df.columns])
        
        # Add encoded categorical features
        encoded_cols = [f'{col}_encoded' for col in categorical_columns if f'{col}_encoded' in df.columns]
        feature_columns.extend(encoded_cols)
        
        # Add anomaly flags
        anomaly_cols = ['unusual_timing', 'high_error_period']
        feature_columns.extend([col for col in anomaly_cols if col in df.columns])
        
        # Get basic features
        X_basic = df[feature_columns].values
        
        # Get text features (BERT or TF-IDF)
        if use_bert and self.use_bert:
            logger.info("Using BERT embeddings for text features")
            text_features = self.get_bert_embeddings(df['cleaned_message'].tolist())
            if text_features.size > 0:
                X_combined = np.hstack([X_basic, text_features])
            else:
                logger.warning("BERT embeddings failed, falling back to TF-IDF")
                text_features = self.get_tfidf_features(df['cleaned_message'].tolist())
                X_combined = np.hstack([X_basic, text_features])
        else:
            logger.info("Using TF-IDF features for text")
            text_features = self.get_tfidf_features(df['cleaned_message'].tolist())
            X_combined = np.hstack([X_basic, text_features])
        
        # Prepare target variable
        if 'level' in df.columns:
            y = df['level_encoded'].values
        else:
            logger.error("No target variable found")
            raise ValueError("Missing target variable")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_combined)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42, stratify=y
        )
        
        logger.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
        
        # Save processed data
        if save_processed:
            self.save_processed_data(X_train, X_test, y_train, y_test, df)
        
        return X_train, X_test, y_train, y_test

    def save_processed_data(self, X_train: np.ndarray, X_test: np.ndarray, 
                           y_train: np.ndarray, y_test: np.ndarray, df: pd.DataFrame):
        """Save processed data and preprocessing objects"""
        
        # Save data arrays
        np.save('X_train_enhanced.npy', X_train)
        np.save('X_test_enhanced.npy', X_test)
        np.save('y_train_enhanced.npy', y_train)
        np.save('y_test_enhanced.npy', y_test)
        
        # Save preprocessing objects
        with open('preprocessor_objects.pkl', 'wb') as f:
            pickle.dump({
                'label_encoders': self.label_encoders,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'scaler': self.scaler,
                'use_bert': self.use_bert,
                'bert_model_name': self.bert_model_name
            }, f)
        
        # Save processed DataFrame
        df.to_csv('logs_enhanced_processed.csv', index=False)
        
        logger.info("✅ Processed data saved successfully")

    def load_processed_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load previously processed data"""
        try:
            X_train = np.load('X_train_enhanced.npy')
            X_test = np.load('X_test_enhanced.npy')
            y_train = np.load('y_train_enhanced.npy')
            y_test = np.load('y_test_enhanced.npy')
            
            # Load preprocessing objects
            with open('preprocessor_objects.pkl', 'rb') as f:
                objects = pickle.load(f)
                self.label_encoders = objects['label_encoders']
                self.tfidf_vectorizer = objects['tfidf_vectorizer']
                self.scaler = objects['scaler']
            
            logger.info("✅ Processed data loaded successfully")
            return X_train, X_test, y_train, y_test
            
        except FileNotFoundError:
            logger.error("No processed data found. Please run preprocessing first.")
            raise

def main():
    """Main function to run enhanced preprocessing"""
    preprocessor = EnhancedLogPreprocessor()
    
    try:
        # Check if enhanced logs exist
        log_file = "enhanced_synthetic_logs.csv"
        
        # Preprocess logs
        X_train, X_test, y_train, y_test = preprocessor.preprocess_logs(
            file_path=log_file,
            use_bert=True,  # Try BERT first, fallback to TF-IDF
            test_size=0.2,
            save_processed=True
        )
        
        print("✅ Enhanced preprocessing completed successfully!")
        print(f"Training set shape: {X_train.shape}")
        print(f"Test set shape: {X_test.shape}")
        print(f"Number of classes: {len(np.unique(y_train))}")
        
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        print("❌ Enhanced preprocessing failed!")

if __name__ == "__main__":
    main()

