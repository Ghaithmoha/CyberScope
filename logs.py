"""
Logs API Routes
Handles log ingestion, search, and retrieval
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

logs_bp = Blueprint('logs', __name__)

# Mock data for demonstration (in production, this would come from database)
MOCK_LOGS = [
    {
        'id': 1,
        'timestamp': '2025-06-17T14:30:15Z',
        'level': 'INFO',
        'source': 'web_server',
        'message': 'User user_8773 logged in successfully from IP 107.6.148.100',
        'thread_id': 'thread_15',
        'process_id': 2376
    },
    {
        'id': 2,
        'timestamp': '2025-06-17T14:30:12Z',
        'level': 'DEBUG',
        'source': 'auth_service',
        'message': 'Processing request req_789456 from user user_8773',
        'thread_id': 'thread_8',
        'process_id': 1234
    },
    {
        'id': 3,
        'timestamp': '2025-06-17T14:30:08Z',
        'level': 'WARNING',
        'source': 'database',
        'message': 'Slow query detected: 2500ms for query q_4567',
        'thread_id': 'thread_3',
        'process_id': 5678
    },
    {
        'id': 4,
        'timestamp': '2025-06-17T14:30:05Z',
        'level': 'INFO',
        'source': 'file_system',
        'message': 'File document_456.pdf uploaded successfully by user user_8773',
        'thread_id': 'thread_12',
        'process_id': 9012
    },
    {
        'id': 5,
        'timestamp': '2025-06-17T14:30:02Z',
        'level': 'ERROR',
        'source': 'payment_gateway',
        'message': 'Payment processing failed for order order_67890: Invalid credentials',
        'thread_id': 'thread_5',
        'process_id': 3456
    }
]

@logs_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    Get logs with optional filtering
    Query parameters:
    - level: Filter by log level (INFO, WARNING, ERROR, DEBUG)
    - source: Filter by log source
    - search: Search in log messages
    - start_time: Start time for filtering (ISO format)
    - end_time: End time for filtering (ISO format)
    - limit: Number of logs to return (default: 100)
    - offset: Offset for pagination (default: 0)
    """
    try:
        # Get query parameters
        level = request.args.get('level')
        source = request.args.get('source')
        search = request.args.get('search', '').lower()
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Filter logs
        filtered_logs = MOCK_LOGS.copy()
        
        if level:
            filtered_logs = [log for log in filtered_logs if log['level'].lower() == level.lower()]
        
        if source:
            filtered_logs = [log for log in filtered_logs if log['source'].lower() == source.lower()]
        
        if search:
            filtered_logs = [log for log in filtered_logs if search in log['message'].lower()]
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')) <= end_dt]
        
        # Apply pagination
        total_count = len(filtered_logs)
        paginated_logs = filtered_logs[offset:offset + limit]
        
        return jsonify({
            'logs': paginated_logs,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total_count
        })
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/logs', methods=['POST'])
def ingest_logs():
    """
    Ingest new logs
    Expected JSON format:
    {
        "logs": [
            {
                "timestamp": "2025-06-17T14:30:15Z",
                "level": "INFO",
                "source": "web_server",
                "message": "Log message here"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'logs' not in data:
            return jsonify({'error': 'Invalid request format. Expected {"logs": [...]}'}), 400
        
        logs = data['logs']
        processed_logs = []
        
        for log_entry in logs:
            # Validate required fields
            required_fields = ['timestamp', 'level', 'source', 'message']
            if not all(field in log_entry for field in required_fields):
                return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
            
            # Process log entry
            processed_log = {
                'id': len(MOCK_LOGS) + len(processed_logs) + 1,
                'timestamp': log_entry['timestamp'],
                'level': log_entry['level'].upper(),
                'source': log_entry['source'],
                'message': log_entry['message'],
                'thread_id': log_entry.get('thread_id', 'unknown'),
                'process_id': log_entry.get('process_id', 0)
            }
            
            processed_logs.append(processed_log)
            MOCK_LOGS.append(processed_log)
        
        # In production, you would:
        # 1. Store logs in database
        # 2. Process logs through ML pipeline for anomaly detection
        # 3. Trigger alerts if necessary
        
        return jsonify({
            'message': f'Successfully ingested {len(processed_logs)} logs',
            'processed_logs': processed_logs
        }), 201
        
    except Exception as e:
        logger.error(f"Error ingesting logs: {e}")
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/logs/<int:log_id>', methods=['GET'])
def get_log_by_id(log_id):
    """Get a specific log by ID"""
    try:
        log = next((log for log in MOCK_LOGS if log['id'] == log_id), None)
        
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        
        return jsonify(log)
        
    except Exception as e:
        logger.error(f"Error getting log {log_id}: {e}")
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/logs/predict', methods=['POST'])
def predict_log_level():
    """
    Predict log level using ML models
    Expected JSON format:
    {
        "message": "Log message to classify",
        "source": "optional_source",
        "model": "random_forest"  # optional, defaults to random_forest
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing required field: message'}), 400
        
        message = data['message']
        source = data.get('source', 'unknown')
        model_name = data.get('model', 'random_forest')
        
        # Get ML models from app config
        ml_models = current_app.config.get('ml_models', {})
        preprocessor = current_app.config.get('preprocessor', {})
        
        classification_model_key = f'classification_{model_name}'
        
        if classification_model_key not in ml_models:
            available_models = [key.replace('classification_', '') for key in ml_models.keys() if key.startswith('classification_')]
            return jsonify({
                'error': f'Model {model_name} not found',
                'available_models': available_models
            }), 400
        
        # For demonstration, return mock prediction
        # In production, you would preprocess the message and use the actual model
        mock_predictions = {
            'predicted_level': 'INFO',
            'confidence': 0.85,
            'probabilities': {
                'INFO': 0.85,
                'WARNING': 0.10,
                'ERROR': 0.03,
                'DEBUG': 0.02
            }
        }
        
        return jsonify({
            'message': message,
            'source': source,
            'model_used': model_name,
            'prediction': mock_predictions
        })
        
    except Exception as e:
        logger.error(f"Error predicting log level: {e}")
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/logs/sources', methods=['GET'])
def get_log_sources():
    """Get list of available log sources"""
    try:
        sources = list(set(log['source'] for log in MOCK_LOGS))
        return jsonify({'sources': sorted(sources)})
        
    except Exception as e:
        logger.error(f"Error getting log sources: {e}")
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/logs/levels', methods=['GET'])
def get_log_levels():
    """Get list of available log levels"""
    try:
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        return jsonify({'levels': levels})
        
    except Exception as e:
        logger.error(f"Error getting log levels: {e}")
        return jsonify({'error': str(e)}), 500

