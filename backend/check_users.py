#!/usr/bin/env python3
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, text
from app.models import User
from app.database import DATABASE_URL

async def check_users():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Check for duplicate users
        result = await conn.execute(text('SELECT id, name, COUNT(*) as count FROM users GROUP BY id, name HAVING COUNT(*) > 1'))
        duplicates = result.fetchall()
        if duplicates:
            print('Duplicate users found:')
            for dup in duplicates:
                print(f'  ID: {dup[0]}, Name: {dup[1]}, Count: {dup[2]}')
        else:
            print('No duplicate users found')
        
        # Check all users
        result = await conn.execute(text('SELECT id, name, role FROM users ORDER BY id'))
        users = result.fetchall()
        print(f'\nAll users ({len(users)}):')
        for user in users:
            print(f'  ID: {user[0]}, Name: {user[1]}, Role: {user[2]}')
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_users()) 