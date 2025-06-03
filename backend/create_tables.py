#!/usr/bin/env python3
"""
Create database tables for DealTracker
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.database import DATABASE_URL

async def create_tables():
    """Create all database tables"""
    
    print("🗄️ Creating database tables...")
    print(f"Database URL: {DATABASE_URL}")
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables()) 