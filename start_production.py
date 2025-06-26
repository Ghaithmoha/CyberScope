#!/usr/bin/env python3
"""
Production startup script for CyberScope Enterprise
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please run setup-wizard.py first")
        return False
    
    # Check if models directory exists
    Path("models").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    
    print("✅ Requirements check passed")
    return True

async def initialize_database():
    """Initialize database and create admin user if needed"""
    print("🗄️ Initializing database...")
    
    try:
        # Run database migrations
        subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], check=True)
        
        print("✅ Database initialized")
        
        # Check if admin user exists
        from backend.core.database import AsyncSessionLocal
        from backend.core.security import User
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.role == "admin")
            )
            admin_exists = result.scalar_one_or_none() is not None
        
        if not admin_exists:
            print("⚠️ No admin user found. Please run create_admin.py")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True

def start_services():
    """Start all CyberScope services"""
    print("🚀 Starting CyberScope Enterprise...")
    
    # Start the main application
    try:
        # Use gunicorn for production
        cmd = [
            "gunicorn",
            "backend.main:app",
            "--bind", "0.0.0.0:8000",
            "--workers", "4",
            "--worker-class", "uvicorn.workers.UvicornWorker",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "--log-level", "info"
        ]
        
        print("🌐 Starting API server on http://0.0.0.0:8000")
        print("📊 Prometheus metrics on http://0.0.0.0:9090")
        print("📖 API documentation at http://0.0.0.0:8000/api/docs")
        print("\n🎯 CyberScope Enterprise is starting...")
        print("Press Ctrl+C to stop")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down CyberScope Enterprise...")
    except Exception as e:
        print(f"❌ Failed to start services: {e}")

async def main():
    """Main startup function"""
    print("⚡ CyberScope Enterprise - Production Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Initialize database
    if not await initialize_database():
        sys.exit(1)
    
    # Start services
    start_services()

if __name__ == "__main__":
    asyncio.run(main())