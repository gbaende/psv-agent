import asyncio
from app.database import AsyncSessionLocal
from app.models import User, Base
from sqlalchemy import select

async def test_and_setup_db():
    async with AsyncSessionLocal() as session:
        try:
            # Test if we can query users
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f'Found {len(users)} users')
            
            # If no users, create some sample sales users
            if len(users) == 0:
                print("Creating sample sales users...")
                sample_users = [
                    User(
                        name="John Doe",
                        email="john@company.com",
                        role="sales",
                        slack_user_id="U123456"
                    ),
                    User(
                        name="Jane Smith", 
                        email="jane@company.com",
                        role="sales",
                        slack_user_id="U789012"
                    ),
                    User(
                        name="Mike Johnson",
                        email="mike@company.com", 
                        role="sales",
                        slack_user_id="U345678"
                    )
                ]
                
                for user in sample_users:
                    session.add(user)
                
                await session.commit()
                print("Sample users created!")
            else:
                for user in users:
                    print(f'- {user.name} ({user.role})')
                    
        except Exception as e:
            print(f"Database error: {e}")

if __name__ == "__main__":
    asyncio.run(test_and_setup_db()) 