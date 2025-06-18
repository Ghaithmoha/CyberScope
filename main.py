import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pickle

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'enhanced_log_analysis_secret_key_2025'

# Enable CORS for all routes
CORS(app, origins='*')

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.dirname(__file__), "database", "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Load ML models and preprocessors (simplified for deployment)
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app.config['MODEL_PATH'] = MODEL_PATH

def load_ml_models():
    """Load trained ML models and preprocessors"""
    try:
        models = {}
        
        # Try to load preprocessor objects
        preprocessor_path = os.path.join(MODEL_PATH, 'preprocessor_objects.pkl')
        if os.path.exists(preprocessor_path):
            try:
                with open(preprocessor_path, 'rb') as f:
                    app.config['preprocessor'] = pickle.load(f)
                logger.info("Preprocessor loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load preprocessor: {e}")
        
        # Try to load models with joblib
        try:
            import joblib
            import glob
            
            # Load classification models
            classification_files = glob.glob(os.path.join(MODEL_PATH, 'enhanced_models_classification_*.pkl'))
            for filepath in classification_files:
                name = os.path.basename(filepath).split('_classification_')[1].replace('.pkl', '')
                try:
                    models[f'classification_{name}'] = joblib.load(filepath)
                    logger.info(f"Loaded classification model: {name}")
                except Exception as e:
                    logger.warning(f"Failed to load classification model {name}: {e}")
            
            # Load anomaly detection models
            anomaly_files = glob.glob(os.path.join(MODEL_PATH, 'enhanced_models_anomaly_*.pkl'))
            for filepath in anomaly_files:
                name = os.path.basename(filepath).split('_anomaly_')[1].replace('.pkl', '')
                try:
                    models[f'anomaly_{name}'] = joblib.load(filepath)
                    logger.info(f"Loaded anomaly model: {name}")
                except Exception as e:
                    logger.warning(f"Failed to load anomaly model {name}: {e}")
                    
        except ImportError:
            logger.warning("joblib not available, skipping model loading")
        except Exception as e:
            logger.warning(f"Error loading models: {e}")
        
        app.config['ml_models'] = models
        logger.info(f"Loaded {len(models)} ML models successfully")
        
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")
        app.config['ml_models'] = {}

with app.app_context():
    db.create_all()
    load_ml_models()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': len(app.config.get('ml_models', {})),
        'version': '1.0.0'
    })

@app.route('/api/models/status', methods=['GET'])
def models_status():
    """Get status of loaded ML models"""
    models = app.config.get('ml_models', {})
    return jsonify({
        'models_count': len(models),
        'models': list(models.keys()),
        'preprocessor_loaded': 'preprocessor' in app.config
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get logs with pagination and filtering"""
    try:
        # Simulate log data for demo
        logs = []
        for i in range(100):
            logs.append({
                'id': i + 1,
                'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                'level': ['INFO', 'WARNING', 'ERROR', 'DEBUG'][i % 4],
                'source': f'service-{(i % 5) + 1}',
                'message': f'Sample log message {i + 1}',
                'anomaly_score': round((i % 10) / 10, 2)
            })
        
        return jsonify({
            'logs': logs[:20],  # Return first 20 logs
            'total': len(logs),
            'page': 1,
            'per_page': 20
        })
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': 'Failed to get logs'}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        return jsonify({
            'total_logs': 1234567,
            'errors_today': 23,
            'anomalies_detected': 156,
            'system_health': 'good',
            'trends': {
                'logs_per_hour': [100, 120, 95, 110, 130, 105, 115],
                'error_rate': [2.1, 1.8, 2.5, 1.9, 2.3, 1.7, 2.0]
            }
        })
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': 'Failed to get analytics'}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts"""
    try:
        alerts = [
            {
                'id': 1,
                'title': 'High Error Rate Detected',
                'severity': 'high',
                'timestamp': datetime.now().isoformat(),
                'status': 'active'
            },
            {
                'id': 2,
                'title': 'Anomaly in Service-3',
                'severity': 'medium',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'status': 'resolved'
            }
        ]
        
        return jsonify({'alerts': alerts})
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': 'Failed to get alerts'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

