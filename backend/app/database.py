from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get database URL from environment variables"""
    # Use SQLite for local development if no DATABASE_URL is provided
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        # Use SQLite for local development
        return 'sqlite+aiosqlite:///./dealtracker.db'
    return db_url

def get_sync_database_url():
    """Get synchronous database URL"""
    db_url = get_database_url()
    # Convert async URL to sync URL
    if 'sqlite+aiosqlite' in db_url:
        return db_url.replace('sqlite+aiosqlite', 'sqlite')
    elif 'postgresql+asyncpg' in db_url:
        return db_url.replace('postgresql+asyncpg', 'postgresql+psycopg2')
    else:
        return db_url

DATABASE_URL = get_database_url()
SYNC_DATABASE_URL = get_sync_database_url()

# Async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Sync engine and session for SalesAgentService compatibility
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=sync_engine, class_=Session, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 