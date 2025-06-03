#!/usr/bin/env python3
"""
Update database users with real Slack IDs from workspace
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models import User

# Load environment variables
load_dotenv()

async def update_users_with_slack_ids():
    """Update existing users with real Slack IDs"""
    
    # Mapping of existing users to real Slack users
    user_mappings = [
        {
            "name": "John Doe",
            "slack_user_id": "U08E2VCC1FB",  # Gedeon Baende
            "email": "gedeon@pacificsoftwareventures.com"
        },
        {
            "name": "Jane Smith", 
            "slack_user_id": "U06T93G62E5",  # Aidan Scudder
            "email": "aidan@pacificsoftwareventures.com"
        },
        {
            "name": "Mike Johnson",
            "slack_user_id": "U06TAA2A73K",  # Sanjay Thasma
            "email": "thasma@wisc.edu"
        }
    ]
    
    print("🔄 Updating database users with real Slack IDs...")
    
    try:
        async for db in get_db():
            # Get existing users
            result = await db.execute(select(User))
            existing_users = result.scalars().all()
            
            print(f"📋 Found {len(existing_users)} existing users:")
            for user in existing_users:
                print(f"  - {user.name} (ID: {user.id}, Email: {user.email})")
            
            # Update users with Slack IDs
            for mapping in user_mappings:
                # Find user by name
                result = await db.execute(
                    select(User).where(User.name == mapping["name"])
                )
                user = result.scalar_one_or_none()
                
                if user:
                    # Update with Slack ID and email
                    await db.execute(
                        update(User)
                        .where(User.id == user.id)
                        .values(
                            slack_user_id=mapping["slack_user_id"],
                            email=mapping["email"]
                        )
                    )
                    print(f"✅ Updated {user.name} with Slack ID: {mapping['slack_user_id']}")
                else:
                    print(f"❌ User {mapping['name']} not found in database")
            
            await db.commit()
            print("✅ Database updated successfully!")
            
            # Verify updates
            print("\n📋 Updated users:")
            result = await db.execute(select(User))
            updated_users = result.scalars().all()
            
            for user in updated_users:
                print(f"  - {user.name}")
                print(f"    Email: {user.email}")
                print(f"    Slack ID: {user.slack_user_id}")
                print(f"    Role: {user.role}")
                print()
            
            break  # Exit the async generator loop
            
    except Exception as e:
        print(f"❌ Error updating users: {e}")

if __name__ == "__main__":
    asyncio.run(update_users_with_slack_ids()) 