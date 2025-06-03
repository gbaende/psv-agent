#!/usr/bin/env python3
"""
Database initialization script for DealTracker Sales Agent
"""

import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.database import get_database_url

async def init_database():
    """Initialize the database with all tables"""
    
    # Get database URL
    database_url = get_database_url()
    
    # Create async engine
    if database_url.startswith("postgresql://"):
        # Convert to asyncpg format
        async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        async_url = database_url
    
    engine = create_async_engine(async_url, echo=True)
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise
    
    finally:
        await engine.dispose()

def init_database_sync():
    """Synchronous version for environments that don't support async"""
    
    # Get database URL
    database_url = get_database_url()
    
    # Create sync engine
    if database_url.startswith("postgresql+asyncpg://"):
        # Convert to sync format
        sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        sync_url = database_url
    
    engine = create_engine(sync_url, echo=True)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    # Try async first, fall back to sync
    try:
        asyncio.run(init_database())
    except Exception as e:
        print(f"Async initialization failed: {e}")
        print("Falling back to synchronous initialization...")
        init_database_sync() 