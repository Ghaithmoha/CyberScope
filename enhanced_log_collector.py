"""
Enhanced Log Collector with Kafka Integration
Supports multiple log sources and formats
"""
import csv
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedLogCollector:
    def __init__(self, kafka_bootstrap_servers: str = 'localhost:9092', kafka_topic: str = 'raw_logs'):
        """
        Initialize the Enhanced Log Collector
        
        Args:
            kafka_bootstrap_servers: Kafka bootstrap servers
            kafka_topic: Kafka topic to send logs to
        """
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.producer = None
        self.use_kafka = False
        
        # Try to initialize Kafka producer
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            self.use_kafka = True
            logger.info(f"Kafka producer initialized successfully. Topic: {kafka_topic}")
        except Exception as e:
            logger.warning(f"Failed to initialize Kafka producer: {e}. Falling back to file output.")
            self.use_kafka = False

    def generate_realistic_logs(self, num_logs: int = 1000) -> List[Dict[str, Any]]:
        """
        Generate realistic log entries with various patterns and anomalies
        
        Args:
            num_logs: Number of log entries to generate
            
        Returns:
            List of log dictionaries
        """
        log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        log_sources = ['web_server', 'database', 'auth_service', 'payment_gateway', 'file_system']
        
        # Realistic log message templates
        message_templates = {
            'INFO': [
                "User {user_id} logged in successfully from IP {ip_address}",
                "File {filename} uploaded successfully by user {user_id}",
                "Database connection established for session {session_id}",
                "Payment processed successfully for order {order_id}",
                "System health check completed - all services running",
                "Cache cleared for user {user_id}",
                "Backup completed successfully at {timestamp}"
            ],
            'WARNING': [
                "High memory usage detected: {memory_usage}% on server {server_id}",
                "Slow query detected: {query_time}ms for query {query_id}",
                "Failed login attempt from IP {ip_address} for user {user_id}",
                "Disk space running low: {disk_usage}% on volume {volume_id}",
                "API rate limit approaching for client {client_id}",
                "Connection timeout for external service {service_name}"
            ],
            'ERROR': [
                "Database connection failed: {error_message}",
                "Payment processing failed for order {order_id}: {error_message}",
                "File upload failed: {filename} - {error_message}",
                "Authentication service unavailable",
                "Critical system error: {error_message}",
                "Data corruption detected in table {table_name}",
                "Service {service_name} crashed with exit code {exit_code}"
            ],
            'DEBUG': [
                "Processing request {request_id} from user {user_id}",
                "Query executed: {query} in {query_time}ms",
                "Cache miss for key {cache_key}",
                "Function {function_name} called with parameters {parameters}",
                "API call to {endpoint} returned status {status_code}"
            ]
        }
        
        logs = []
        start_time = datetime.now() - timedelta(hours=24)
        
        for i in range(num_logs):
            # Generate timestamp (mostly recent, with some older entries)
            if random.random() < 0.8:  # 80% recent logs
                timestamp = start_time + timedelta(
                    hours=random.uniform(20, 24),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
            else:  # 20% older logs
                timestamp = start_time + timedelta(
                    hours=random.uniform(0, 20),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
            
            # Select log level (INFO most common, ERROR least common)
            level_weights = {'INFO': 0.6, 'WARNING': 0.25, 'ERROR': 0.1, 'DEBUG': 0.05}
            level = random.choices(list(level_weights.keys()), weights=list(level_weights.values()))[0]
            
            # Select source
            source = random.choice(log_sources)
            
            # Generate message
            template = random.choice(message_templates[level])
            message = template.format(
                user_id=f"user_{random.randint(1000, 9999)}",
                ip_address=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                filename=f"document_{random.randint(1, 1000)}.pdf",
                session_id=f"sess_{random.randint(100000, 999999)}",
                order_id=f"order_{random.randint(10000, 99999)}",
                server_id=f"srv_{random.randint(1, 10)}",
                memory_usage=random.randint(70, 95),
                query_time=random.randint(100, 5000),
                query_id=f"q_{random.randint(1000, 9999)}",
                disk_usage=random.randint(80, 95),
                volume_id=f"vol_{random.randint(1, 5)}",
                client_id=f"client_{random.randint(1000, 9999)}",
                service_name=random.choice(['auth_service', 'payment_gateway', 'notification_service']),
                error_message=random.choice(['Connection timeout', 'Invalid credentials', 'Resource not found', 'Internal server error']),
                table_name=f"table_{random.choice(['users', 'orders', 'products', 'logs'])}",
                exit_code=random.choice([1, 2, 127, 255]),
                request_id=f"req_{random.randint(100000, 999999)}",
                query=f"SELECT * FROM {random.choice(['users', 'orders', 'products'])} WHERE id = {random.randint(1, 1000)}",
                cache_key=f"cache_{random.randint(1000, 9999)}",
                function_name=f"process_{random.choice(['payment', 'user', 'order', 'file'])}",
                parameters=f"{{id: {random.randint(1, 1000)}, type: '{random.choice(['create', 'update', 'delete'])}'}}",
                endpoint=f"/api/v1/{random.choice(['users', 'orders', 'products'])}",
                status_code=random.choice([200, 201, 400, 404, 500]),
                timestamp=timestamp.isoformat()
            )
            
            # Create log entry
            log_entry = {
                'timestamp': timestamp.isoformat(),
                'level': level,
                'source': source,
                'message': message,
                'log_id': f"log_{i+1:06d}",
                'thread_id': f"thread_{random.randint(1, 20)}",
                'process_id': random.randint(1000, 9999)
            }
            
            # Add some anomalous patterns (5% of logs)
            if random.random() < 0.05:
                log_entry = self._create_anomalous_log(log_entry, i)
            
            logs.append(log_entry)
        
        # Sort logs by timestamp
        logs.sort(key=lambda x: x['timestamp'])
        
        return logs

    def _create_anomalous_log(self, log_entry: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create anomalous log patterns for testing anomaly detection"""
        anomaly_types = [
            'unusual_timing',
            'suspicious_ip',
            'repeated_failures',
            'unusual_user_activity'
        ]
        
        anomaly_type = random.choice(anomaly_types)
        
        if anomaly_type == 'unusual_timing':
            # Logs at unusual hours (2-5 AM)
            unusual_time = datetime.now().replace(hour=random.randint(2, 5), minute=random.randint(0, 59))
            log_entry['timestamp'] = unusual_time.isoformat()
            log_entry['anomaly_type'] = 'unusual_timing'
            
        elif anomaly_type == 'suspicious_ip':
            # Suspicious IP patterns
            suspicious_ips = ['192.168.1.1', '10.0.0.1', '172.16.0.1', '127.0.0.1']
            log_entry['message'] = log_entry['message'].replace(
                log_entry['message'].split('IP ')[1].split(' ')[0] if 'IP ' in log_entry['message'] else '',
                random.choice(suspicious_ips)
            )
            log_entry['anomaly_type'] = 'suspicious_ip'
            
        elif anomaly_type == 'repeated_failures':
            # Multiple failures in short time
            log_entry['level'] = 'ERROR'
            log_entry['message'] = f"Repeated failure #{random.randint(5, 20)} for user user_suspicious"
            log_entry['anomaly_type'] = 'repeated_failures'
            
        elif anomaly_type == 'unusual_user_activity':
            # Unusual user activity patterns
            log_entry['message'] = f"User user_suspicious performed {random.randint(100, 1000)} actions in 1 minute"
            log_entry['anomaly_type'] = 'unusual_user_activity'
        
        return log_entry

    def send_to_kafka(self, logs: List[Dict[str, Any]]) -> bool:
        """
        Send logs to Kafka topic
        
        Args:
            logs: List of log dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.use_kafka or not self.producer:
            logger.warning("Kafka producer not available")
            return False
        
        try:
            for log in logs:
                # Use log_id as key for partitioning
                key = log.get('log_id', str(random.randint(1, 1000)))
                future = self.producer.send(self.kafka_topic, key=key, value=log)
                
            # Wait for all messages to be sent
            self.producer.flush()
            logger.info(f"Successfully sent {len(logs)} logs to Kafka topic '{self.kafka_topic}'")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send logs to Kafka: {e}")
            return False

    def save_to_csv(self, logs: List[Dict[str, Any]], filename: str = "enhanced_logs.csv") -> bool:
        """
        Save logs to CSV file
        
        Args:
            logs: List of log dictionaries
            filename: Output CSV filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            df = pd.DataFrame(logs)
            df.to_csv(filename, index=False)
            logger.info(f"Successfully saved {len(logs)} logs to '{filename}'")
            return True
        except Exception as e:
            logger.error(f"Failed to save logs to CSV: {e}")
            return False

    def collect_and_process(self, num_logs: int = 1000, output_file: str = "enhanced_logs.csv") -> bool:
        """
        Main method to collect and process logs
        
        Args:
            num_logs: Number of logs to generate
            output_file: Output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting log collection process - generating {num_logs} logs")
        
        # Generate logs
        logs = self.generate_realistic_logs(num_logs)
        
        # Try to send to Kafka first
        kafka_success = False
        if self.use_kafka:
            kafka_success = self.send_to_kafka(logs)
        
        # Always save to CSV as backup
        csv_success = self.save_to_csv(logs, output_file)
        
        if kafka_success:
            logger.info("✅ Logs sent to Kafka successfully")
        if csv_success:
            logger.info(f"✅ Logs saved to '{output_file}' successfully")
        
        return kafka_success or csv_success

    def close(self):
        """Close Kafka producer connection"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer connection closed")

def main():
    """Main function to run the enhanced log collector"""
    collector = EnhancedLogCollector()
    
    try:
        # Generate and collect logs
        success = collector.collect_and_process(
            num_logs=5000,  # Generate 5000 realistic logs
            output_file="enhanced_synthetic_logs.csv"
        )
        
        if success:
            print("✅ Enhanced log collection completed successfully!")
        else:
            print("❌ Log collection failed!")
            
    except KeyboardInterrupt:
        logger.info("Log collection interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error during log collection: {e}")
    finally:
        collector.close()

if __name__ == "__main__":
    main()

