from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
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

DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 