#!/usr/bin/env python3
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import DATABASE_URL

async def check_projects():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT id, name FROM projects'))
        projects = result.fetchall()
        print(f'Projects in database ({len(projects)}):')
        for project in projects:
            print(f'  ID: {project[0]}, Name: {project[1]}')
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_projects()) 