# Enhanced Log Analysis API

## Description
A powerful log analysis system with machine learning capabilities for enterprise-level log monitoring and anomaly detection.

## Features
- Real-time log ingestion and processing
- Machine learning-based anomaly detection
- Advanced analytics and reporting
- RESTful API for integration
- Scalable architecture

## API Endpoints

### Health Check
- `GET /api/health` - Check API health status

### Models
- `GET /api/models/status` - Get ML models status

### Logs
- `GET /api/logs` - Get logs with pagination and filtering

### Analytics
- `GET /api/analytics` - Get analytics data and metrics

### Alerts
- `GET /api/alerts` - Get system alerts

## Deployment

### Local Development
```bash
python src/main.py
```

### Production (Heroku)
```bash
gunicorn src.main:app
```

## Environment Variables
- `PORT` - Server port (default: 5000)
- `FLASK_ENV` - Environment (development/production)
- `SECRET_KEY` - Flask secret key

## Requirements
- Python 3.10+
- Flask
- scikit-learn
- pandas
- numpy

## License
MIT License

