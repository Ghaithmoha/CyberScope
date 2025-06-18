"""
Alerts API Routes
Handles alert configuration, notifications, and management
"""
import os
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

alerts_bp = Blueprint('alerts', __name__)

# Mock alerts data
MOCK_ALERTS = [
    {
        'id': 1,
        'name': 'Critical Error Threshold',
        'description': 'Alert when critical errors exceed 10 per hour',
        'type': 'threshold',
        'condition': 'error_count > 10',
        'severity': 'critical',
        'enabled': True,
        'created_at': '2025-06-15T10:00:00Z',
        'last_triggered': '2025-06-17T14:23:45Z',
        'trigger_count': 3
    },
    {
        'id': 2,
        'name': 'Anomaly Detection Alert',
        'description': 'Alert when anomaly score exceeds 0.9',
        'type': 'anomaly',
        'condition': 'anomaly_score > 0.9',
        'severity': 'high',
        'enabled': True,
        'created_at': '2025-06-15T10:00:00Z',
        'last_triggered': '2025-06-17T14:15:21Z',
        'trigger_count': 7
    },
    {
        'id': 3,
        'name': 'System Health Warning',
        'description': 'Alert when system health drops below 95%',
        'type': 'health',
        'condition': 'system_health < 95',
        'severity': 'medium',
        'enabled': True,
        'created_at': '2025-06-15T10:00:00Z',
        'last_triggered': None,
        'trigger_count': 0
    }
]

MOCK_NOTIFICATIONS = [
    {
        'id': 1,
        'alert_id': 1,
        'title': 'Critical Error Threshold Exceeded',
        'message': 'Payment gateway has generated 12 critical errors in the last hour',
        'severity': 'critical',
        'timestamp': '2025-06-17T14:23:45Z',
        'status': 'sent',
        'channels': ['email', 'webhook']
    },
    {
        'id': 2,
        'alert_id': 2,
        'title': 'High Anomaly Score Detected',
        'message': 'Database connection pool exhausted - anomaly score: 0.92',
        'severity': 'high',
        'timestamp': '2025-06-17T14:15:21Z',
        'status': 'sent',
        'channels': ['email', 'slack']
    }
]

@alerts_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get all alert configurations"""
    try:
        return jsonify({
            'alerts': MOCK_ALERTS,
            'total_count': len(MOCK_ALERTS)
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts', methods=['POST'])
def create_alert():
    """
    Create a new alert configuration
    Expected JSON format:
    {
        "name": "Alert Name",
        "description": "Alert description",
        "type": "threshold|anomaly|health",
        "condition": "condition expression",
        "severity": "low|medium|high|critical",
        "enabled": true,
        "notification_channels": ["email", "webhook", "slack"]
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['name', 'description', 'type', 'condition', 'severity']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        # Create new alert
        new_alert = {
            'id': len(MOCK_ALERTS) + 1,
            'name': data['name'],
            'description': data['description'],
            'type': data['type'],
            'condition': data['condition'],
            'severity': data['severity'],
            'enabled': data.get('enabled', True),
            'created_at': datetime.now().isoformat() + 'Z',
            'last_triggered': None,
            'trigger_count': 0,
            'notification_channels': data.get('notification_channels', ['email'])
        }
        
        MOCK_ALERTS.append(new_alert)
        
        return jsonify({
            'message': 'Alert created successfully',
            'alert': new_alert
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Get a specific alert by ID"""
    try:
        alert = next((alert for alert in MOCK_ALERTS if alert['id'] == alert_id), None)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        return jsonify(alert)
        
    except Exception as e:
        logger.error(f"Error getting alert {alert_id}: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """Update an existing alert"""
    try:
        alert = next((alert for alert in MOCK_ALERTS if alert['id'] == alert_id), None)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        data = request.get_json()
        
        # Update alert fields
        updatable_fields = ['name', 'description', 'condition', 'severity', 'enabled', 'notification_channels']
        for field in updatable_fields:
            if field in data:
                alert[field] = data[field]
        
        return jsonify({
            'message': 'Alert updated successfully',
            'alert': alert
        })
        
    except Exception as e:
        logger.error(f"Error updating alert {alert_id}: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    try:
        alert_index = next((i for i, alert in enumerate(MOCK_ALERTS) if alert['id'] == alert_id), None)
        
        if alert_index is None:
            return jsonify({'error': 'Alert not found'}), 404
        
        deleted_alert = MOCK_ALERTS.pop(alert_index)
        
        return jsonify({
            'message': 'Alert deleted successfully',
            'deleted_alert': deleted_alert
        })
        
    except Exception as e:
        logger.error(f"Error deleting alert {alert_id}: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/<int:alert_id>/toggle', methods=['POST'])
def toggle_alert(alert_id):
    """Enable or disable an alert"""
    try:
        alert = next((alert for alert in MOCK_ALERTS if alert['id'] == alert_id), None)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert['enabled'] = not alert['enabled']
        
        return jsonify({
            'message': f'Alert {"enabled" if alert["enabled"] else "disabled"} successfully',
            'alert': alert
        })
        
    except Exception as e:
        logger.error(f"Error toggling alert {alert_id}: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/test', methods=['POST'])
def test_alert():
    """
    Test alert notification
    Expected JSON format:
    {
        "alert_id": 1,
        "channels": ["email", "webhook"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'alert_id' not in data:
            return jsonify({'error': 'Missing required field: alert_id'}), 400
        
        alert_id = data['alert_id']
        channels = data.get('channels', ['email'])
        
        alert = next((alert for alert in MOCK_ALERTS if alert['id'] == alert_id), None)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Mock test notification
        test_notification = {
            'id': len(MOCK_NOTIFICATIONS) + 1,
            'alert_id': alert_id,
            'title': f'TEST: {alert["name"]}',
            'message': f'This is a test notification for alert: {alert["description"]}',
            'severity': alert['severity'],
            'timestamp': datetime.now().isoformat() + 'Z',
            'status': 'sent',
            'channels': channels
        }
        
        MOCK_NOTIFICATIONS.append(test_notification)
        
        return jsonify({
            'message': 'Test notification sent successfully',
            'notification': test_notification
        })
        
    except Exception as e:
        logger.error(f"Error testing alert: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Get notification history
    Query parameters:
    - limit: Number of notifications to return (default: 50)
    - severity: Filter by severity
    - status: Filter by status (sent, failed, pending)
    """
    try:
        limit = int(request.args.get('limit', 50))
        severity = request.args.get('severity')
        status = request.args.get('status')
        
        filtered_notifications = MOCK_NOTIFICATIONS.copy()
        
        if severity:
            filtered_notifications = [n for n in filtered_notifications if n['severity'] == severity]
        
        if status:
            filtered_notifications = [n for n in filtered_notifications if n['status'] == status]
        
        # Sort by timestamp (newest first)
        filtered_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        filtered_notifications = filtered_notifications[:limit]
        
        return jsonify({
            'notifications': filtered_notifications,
            'total_count': len(filtered_notifications)
        })
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/notifications/send', methods=['POST'])
def send_notification():
    """
    Send a custom notification
    Expected JSON format:
    {
        "title": "Notification Title",
        "message": "Notification message",
        "severity": "low|medium|high|critical",
        "channels": ["email", "webhook", "slack"],
        "recipients": ["admin@company.com"]
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['title', 'message', 'severity']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        # Create notification
        notification = {
            'id': len(MOCK_NOTIFICATIONS) + 1,
            'alert_id': None,  # Custom notification
            'title': data['title'],
            'message': data['message'],
            'severity': data['severity'],
            'timestamp': datetime.now().isoformat() + 'Z',
            'status': 'sent',
            'channels': data.get('channels', ['email']),
            'recipients': data.get('recipients', [])
        }
        
        MOCK_NOTIFICATIONS.append(notification)
        
        # In production, you would actually send the notification here
        # via email, webhook, Slack, etc.
        
        return jsonify({
            'message': 'Notification sent successfully',
            'notification': notification
        }), 201
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/alerts/evaluate', methods=['POST'])
def evaluate_alerts():
    """
    Evaluate alerts against current log data
    Expected JSON format:
    {
        "logs": [...],
        "metrics": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        logs = data.get('logs', [])
        metrics = data.get('metrics', {})
        
        triggered_alerts = []
        
        # Evaluate each enabled alert
        for alert in MOCK_ALERTS:
            if not alert['enabled']:
                continue
            
            # Mock alert evaluation logic
            should_trigger = False
            
            if alert['type'] == 'threshold':
                # Example: Check error count
                error_count = len([log for log in logs if log.get('level') == 'ERROR'])
                if 'error_count > 10' in alert['condition'] and error_count > 10:
                    should_trigger = True
            
            elif alert['type'] == 'anomaly':
                # Example: Check for high anomaly scores
                high_anomaly_logs = [log for log in logs if log.get('anomaly_score', 0) > 0.9]
                if high_anomaly_logs:
                    should_trigger = True
            
            elif alert['type'] == 'health':
                # Example: Check system health
                system_health = metrics.get('system_health', 100)
                if 'system_health < 95' in alert['condition'] and system_health < 95:
                    should_trigger = True
            
            if should_trigger:
                triggered_alerts.append({
                    'alert': alert,
                    'triggered_at': datetime.now().isoformat() + 'Z',
                    'context': {
                        'logs_analyzed': len(logs),
                        'metrics': metrics
                    }
                })
        
        return jsonify({
            'alerts_evaluated': len(MOCK_ALERTS),
            'alerts_triggered': len(triggered_alerts),
            'triggered_alerts': triggered_alerts
        })
        
    except Exception as e:
        logger.error(f"Error evaluating alerts: {e}")
        return jsonify({'error': str(e)}), 500

