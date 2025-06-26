#!/usr/bin/env python3
"""
CyberScope Enterprise Setup Wizard
Interactive setup for corporate environments
"""

import os
import sys
import json
import subprocess
import secrets
import getpass
from pathlib import Path
from typing import Dict, Any, List

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Colors.ENDC}")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

class CyberScopeSetup:
    def __init__(self):
        self.config = {}
        self.env_vars = {}
        self.setup_dir = Path.cwd()
        
    def welcome(self):
        print_header("CyberScope Enterprise Setup Wizard")
        print(f"""
{Colors.OKCYAN}Welcome to CyberScope Enterprise Setup!{Colors.ENDC}

This wizard will help you configure CyberScope for your enterprise environment.
We'll set up:
• Database configuration
• Security settings
• AI/ML models
• Monitoring and alerting
• User management
• Docker/Kubernetes deployment

Press Enter to continue or Ctrl+C to exit...
        """)
        input()

    def check_requirements(self):
        print_header("Checking System Requirements")
        
        requirements = [
            ("Python 3.11+", self._check_python),
            ("Docker", self._check_docker),
            ("Docker Compose", self._check_docker_compose),
            ("Git", self._check_git),
            ("Node.js 18+", self._check_nodejs)
        ]
        
        all_good = True
        for name, check_func in requirements:
            if check_func():
                print_success(f"{name} - Found")
            else:
                print_error(f"{name} - Missing or outdated")
                all_good = False
        
        if not all_good:
            print_error("Please install missing requirements before continuing.")
            sys.exit(1)
        
        print_success("All requirements satisfied!")

    def configure_database(self):
        print_header("Database Configuration")
        
        print("Choose database setup:")
        print("1. Use built-in PostgreSQL (Docker)")
        print("2. Connect to existing PostgreSQL")
        print("3. Use SQLite (development only)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            self.config["database"] = {
                "type": "postgresql",
                "setup": "docker",
                "host": "database",
                "port": 5432,
                "name": "cyberscope",
                "user": input("Database username [cyberscope]: ").strip() or "cyberscope"
            }
            self.config["database"]["password"] = getpass.getpass("Database password: ")
            
        elif choice == "2":
            self.config["database"] = {
                "type": "postgresql",
                "setup": "external",
                "host": input("Database host: ").strip(),
                "port": int(input("Database port [5432]: ").strip() or "5432"),
                "name": input("Database name: ").strip(),
                "user": input("Database username: ").strip(),
                "password": getpass.getpass("Database password: ")
            }
            
        elif choice == "3":
            self.config["database"] = {
                "type": "sqlite",
                "setup": "local",
                "path": "./data/cyberscope.db"
            }
            print_warning("SQLite is not recommended for production use!")
            
        else:
            print_error("Invalid choice")
            return self.configure_database()

    def configure_security(self):
        print_header("Security Configuration")
        
        # JWT Secret
        jwt_secret = input("JWT Secret Key (leave empty to generate): ").strip()
        if not jwt_secret:
            jwt_secret = secrets.token_urlsafe(32)
            print_info(f"Generated JWT secret: {jwt_secret[:16]}...")
        
        self.config["security"] = {
            "jwt_secret": jwt_secret,
            "session_timeout_hours": int(input("Session timeout (hours) [8]: ").strip() or "8"),
            "max_failed_attempts": int(input("Max failed login attempts [5]: ").strip() or "5"),
            "password_min_length": int(input("Minimum password length [8]: ").strip() or "8")
        }
        
        # Admin user
        print("\nCreate initial admin user:")
        admin_username = input("Admin username [admin]: ").strip() or "admin"
        admin_email = input("Admin email: ").strip()
        admin_password = getpass.getpass("Admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if admin_password != confirm_password:
            print_error("Passwords don't match!")
            return self.configure_security()
        
        self.config["admin_user"] = {
            "username": admin_username,
            "email": admin_email,
            "password": admin_password
        }

    def configure_ai(self):
        print_header("AI/ML Configuration")
        
        print("AI Engine Options:")
        print("1. Local AI only (no external APIs)")
        print("2. Local AI + OpenAI integration")
        print("3. Local AI + Anthropic integration")
        print("4. All integrations")
        
        choice = input("Enter choice (1-4): ").strip()
        
        self.config["ai"] = {
            "local_enabled": True,
            "model_path": "./models",
            "learning_enabled": True
        }
        
        if choice in ["2", "4"]:
            openai_key = getpass.getpass("OpenAI API Key (optional): ")
            if openai_key:
                self.config["ai"]["openai_key"] = openai_key
        
        if choice in ["3", "4"]:
            anthropic_key = getpass.getpass("Anthropic API Key (optional): ")
            if anthropic_key:
                self.config["ai"]["anthropic_key"] = anthropic_key
        
        # AI settings
        self.config["ai"]["anomaly_threshold"] = float(input("Anomaly detection threshold [0.7]: ").strip() or "0.7")
        self.config["ai"]["retrain_interval_hours"] = int(input("Model retrain interval (hours) [24]: ").strip() or "24")

    def configure_monitoring(self):
        print_header("Monitoring Configuration")
        
        enable_monitoring = input("Enable Prometheus monitoring? (y/n) [y]: ").strip().lower()
        self.config["monitoring"] = {
            "enabled": enable_monitoring != "n",
            "prometheus_port": int(input("Prometheus port [9090]: ").strip() or "9090"),
            "grafana_port": int(input("Grafana port [3001]: ").strip() or "3001")
        }
        
        if self.config["monitoring"]["enabled"]:
            grafana_password = getpass.getpass("Grafana admin password: ")
            self.config["monitoring"]["grafana_password"] = grafana_password

    def configure_deployment(self):
        print_header("Deployment Configuration")
        
        print("Deployment options:")
        print("1. Docker Compose (single machine)")
        print("2. Kubernetes (scalable)")
        print("3. Development mode (local)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        self.config["deployment"] = {
            "type": {
                "1": "docker-compose",
                "2": "kubernetes", 
                "3": "development"
            }.get(choice, "docker-compose"),
            "domain": input("Domain name (optional): ").strip(),
            "ssl_enabled": input("Enable SSL/TLS? (y/n) [n]: ").strip().lower() == "y"
        }

    def generate_env_file(self):
        print_header("Generating Environment Configuration")
        
        # Database URL
        db_config = self.config["database"]
        if db_config["type"] == "postgresql":
            db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
        else:
            db_url = f"sqlite:///{db_config['path']}"
        
        env_content = f"""# CyberScope Enterprise Configuration
# Generated by setup wizard

# Database
DATABASE_URL={db_url}
DB_USER={db_config.get('user', '')}
DB_PASSWORD={db_config.get('password', '')}

# Security
JWT_SECRET_KEY={self.config['security']['jwt_secret']}
SESSION_TIMEOUT_HOURS={self.config['security']['session_timeout_hours']}

# AI Configuration
AI_MODEL_PATH={self.config['ai']['model_path']}
ANOMALY_THRESHOLD={self.config['ai']['anomaly_threshold']}
"""
        
        # Add API keys if provided
        if 'openai_key' in self.config['ai']:
            env_content += f"OPENAI_API_KEY={self.config['ai']['openai_key']}\n"
        
        if 'anthropic_key' in self.config['ai']:
            env_content += f"ANTHROPIC_API_KEY={self.config['ai']['anthropic_key']}\n"
        
        # Monitoring
        if self.config['monitoring']['enabled']:
            env_content += f"""
# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_PASSWORD={self.config['monitoring']['grafana_password']}
"""
        
        # Write .env file
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print_success("Environment file created: .env")

    def create_initial_user(self):
        print_header("Creating Initial Admin User")
        
        # This would integrate with the security manager
        admin_config = self.config["admin_user"]
        user_script = f"""
from backend.auth.security import get_security_manager, UserRole

security_manager = get_security_manager()
admin_user = security_manager.create_user(
    username="{admin_config['username']}",
    email="{admin_config['email']}",
    password="{admin_config['password']}",
    role=UserRole.ADMIN
)
print(f"Admin user created: {{admin_user.username}}")
"""
        
        with open('create_admin.py', 'w') as f:
            f.write(user_script)
        
        print_info("Admin user creation script saved: create_admin.py")

    def setup_deployment(self):
        print_header("Setting Up Deployment")
        
        deployment_type = self.config["deployment"]["type"]
        
        if deployment_type == "docker-compose":
            self._setup_docker_compose()
        elif deployment_type == "kubernetes":
            self._setup_kubernetes()
        else:
            self._setup_development()

    def _setup_docker_compose(self):
        print_info("Setting up Docker Compose deployment...")
        
        # Copy production docker-compose file
        try:
            subprocess.run(["cp", "docker-compose.prod.yml", "docker-compose.yml"], check=True)
            print_success("Docker Compose configuration ready")
            
            print_info("To start CyberScope, run:")
            print("  docker-compose up -d")
            
        except subprocess.CalledProcessError:
            print_error("Failed to setup Docker Compose")

    def _setup_kubernetes(self):
        print_info("Setting up Kubernetes deployment...")
        
        # Check if kubectl is available
        try:
            subprocess.run(["kubectl", "version", "--client"], check=True, capture_output=True)
            print_success("kubectl found")
            
            print_info("Kubernetes manifests are in the k8s/ directory")
            print_info("To deploy to Kubernetes:")
            print("  kubectl apply -f k8s/")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_warning("kubectl not found. Please install kubectl to deploy to Kubernetes")

    def _setup_development(self):
        print_info("Setting up development environment...")
        
        try:
            # Install Python dependencies
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print_success("Python dependencies installed")
            
            # Install frontend dependencies if Node.js is available
            if self._check_nodejs():
                subprocess.run(["npm", "install"], cwd="frontend", check=True)
                print_success("Frontend dependencies installed")
            
            print_info("To start development server:")
            print("  python -m uvicorn backend.api.enterprise_api:app --reload")
            
        except subprocess.CalledProcessError:
            print_error("Failed to setup development environment")

    def finalize_setup(self):
        print_header("Setup Complete!")
        
        print(f"""
{Colors.OKGREEN}CyberScope Enterprise has been configured successfully!{Colors.ENDC}

Configuration summary:
• Database: {self.config['database']['type']}
• Deployment: {self.config['deployment']['type']}
• AI Engine: Local + External APIs
• Monitoring: {'Enabled' if self.config['monitoring']['enabled'] else 'Disabled'}

Next steps:
1. Review the generated .env file
2. Start the services according to your deployment type
3. Access the dashboard at http://localhost (or your configured domain)
4. Login with admin credentials: {self.config['admin_user']['username']}

For support and documentation, visit:
https://github.com/your-org/cyberscope-enterprise

{Colors.WARNING}Security reminder:{Colors.ENDC}
• Change default passwords in production
• Configure SSL/TLS certificates
• Review firewall settings
• Enable audit logging
        """)

    # Helper methods for checking requirements
    def _check_python(self) -> bool:
        try:
            import sys
            return sys.version_info >= (3, 11)
        except:
            return False

    def _check_docker(self) -> bool:
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            return True
        except:
            return False

    def _check_docker_compose(self) -> bool:
        try:
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
            return True
        except:
            return False

    def _check_git(self) -> bool:
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            return True
        except:
            return False

    def _check_nodejs(self) -> bool:
        try:
            result = subprocess.run(["node", "--version"], check=True, capture_output=True, text=True)
            version = result.stdout.strip().replace('v', '')
            major_version = int(version.split('.')[0])
            return major_version >= 18
        except:
            return False

def main():
    """Main setup wizard entry point"""
    setup = CyberScopeSetup()
    
    try:
        setup.welcome()
        setup.check_requirements()
        setup.configure_database()
        setup.configure_security()
        setup.configure_ai()
        setup.configure_monitoring()
        setup.configure_deployment()
        setup.generate_env_file()
        setup.create_initial_user()
        setup.setup_deployment()
        setup.finalize_setup()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup cancelled by user.{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()