#!/usr/bin/env python3
"""
Script to add sample users to the database
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models import User
from sqlalchemy import select

async def add_users():
    async with AsyncSessionLocal() as session:
        # Check if users exist
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if len(users) == 0:
            print('Adding sample users...')
            sample_users = [
                User(name='John Doe', email='john@company.com', role='sales', slack_user_id='U123456'),
                User(name='Jane Smith', email='jane@company.com', role='sales', slack_user_id='U789012'),
                User(name='Mike Johnson', email='mike@company.com', role='sales', slack_user_id='U345678'),
                User(name='Admin User', email='admin@company.com', role='admin', slack_user_id='U999999')
            ]
            
            for user in sample_users:
                session.add(user)
            
            await session.commit()
            print(f'Created {len(sample_users)} sample users!')
        else:
            print(f'Found {len(users)} existing users')

if __name__ == "__main__":
    asyncio.run(add_users()) 