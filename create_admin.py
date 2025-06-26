#!/usr/bin/env python3
"""
Create initial admin user for CyberScope Enterprise
"""

import asyncio
import sys
import getpass
from backend.core.database import init_database, AsyncSessionLocal
from backend.core.security import security_manager, UserRole

async def create_admin_user():
    """Create initial admin user"""
    
    print("CyberScope Enterprise - Admin User Creation")
    print("=" * 50)
    
    # Get admin details
    username = input("Admin username [admin]: ").strip() or "admin"
    email = input("Admin email: ").strip()
    
    if not email:
        print("Email is required!")
        sys.exit(1)
    
    password = getpass.getpass("Admin password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        sys.exit(1)
    
    if len(password) < 8:
        print("Password must be at least 8 characters!")
        sys.exit(1)
    
    try:
        # Initialize database
        await init_database()
        
        # Create admin user
        async with AsyncSessionLocal() as db:
            user = await security_manager.create_user(
                db=db,
                username=username,
                email=email,
                password=password,
                role=UserRole.ADMIN
            )
            
            print(f"\n✅ Admin user created successfully!")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role.value}")
            print(f"ID: {user.id}")
            
    except Exception as e:
        print(f"\n❌ Failed to create admin user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_admin_user())