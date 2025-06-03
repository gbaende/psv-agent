#!/usr/bin/env python3
"""
Get actual members from #psv-sales-agent channel and set up database
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert
from app.database import get_db
from app.models import User, Project, Task, Goal
from app.services.slack_service import SlackService
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

async def get_channel_members():
    """Get actual members from the #psv-sales-agent channel"""
    
    print("🔍 Fetching members from #psv-sales-agent channel...")
    
    # Initialize Slack service
    slack_service = SlackService()
    
    if not slack_service.is_configured():
        print("❌ Slack service not configured!")
        return []
    
    try:
        # Get channel info
        channel_id = "C08UNPU9AGN"  # #psv-sales-agent
        
        # Get channel members
        response = await slack_service.client.conversations_members(channel=channel_id)
        
        if not response["ok"]:
            print(f"❌ Failed to get channel members: {response.get('error', 'Unknown error')}")
            return []
        
        member_ids = response["members"]
        print(f"📋 Found {len(member_ids)} members in #psv-sales-agent")
        
        # Get user info for each member
        channel_members = []
        
        for user_id in member_ids:
            try:
                user_response = await slack_service.client.users_info(user=user_id)
                
                if user_response["ok"]:
                    user_data = user_response["user"]
                    
                    # Skip bots and deleted users
                    if user_data.get("is_bot", False) or user_data.get("deleted", False):
                        continue
                    
                    # Extract user information
                    member_info = {
                        "slack_id": user_data["id"],
                        "name": user_data.get("real_name", user_data.get("name", "Unknown")),
                        "display_name": user_data.get("profile", {}).get("display_name", ""),
                        "email": user_data.get("profile", {}).get("email", f"{user_data['name']}@example.com")
                    }
                    
                    channel_members.append(member_info)
                    print(f"  ✅ {member_info['name']} ({member_info['slack_id']})")
                
            except Exception as e:
                print(f"  ❌ Error getting info for user {user_id}: {e}")
                continue
        
        print(f"\n👥 **Channel Members Found: {len(channel_members)}**")
        for i, member in enumerate(channel_members, 1):
            print(f"  {i}. {member['name']} - {member['email']}")
        
        return channel_members
        
    except Exception as e:
        print(f"❌ Error fetching channel members: {e}")
        return []

async def setup_database_with_channel_members(channel_members):
    """Set up database with actual channel members"""
    
    if not channel_members:
        print("❌ No channel members found!")
        return False
    
    print(f"\n🗄️ Setting up database with {len(channel_members)} channel members...")
    print("=" * 60)
    
    try:
        async for db in get_db():
            print(f"\n🧹 Clearing existing data...")
            
            # Clear existing data in correct order (respecting foreign keys)
            await db.execute(delete(Task))
            await db.execute(delete(Goal))
            await db.execute(delete(User))
            await db.execute(delete(Project))
            await db.commit()
            
            print(f"✅ Existing data cleared")
            
            # Create project for PSV Sales Agent
            print(f"\n📁 Creating PSV Sales Agent project...")
            
            project_data = {
                "id": 1,
                "name": "PSV Sales Agent Team",
                "description": "Sales activities for #psv-sales-agent channel members",
                "owner_id": 1  # Will be first user
            }
            
            await db.execute(insert(Project).values(**project_data))
            print(f"✅ Project created: {project_data['name']}")
            
            # Insert channel members
            print(f"\n👥 Adding {len(channel_members)} channel members...")
            
            for i, member in enumerate(channel_members, 1):
                user_data = {
                    "id": i,
                    "name": member["name"],
                    "email": member["email"],
                    "slack_user_id": member["slack_id"],
                    "role": "sales"  # All channel members are sales team
                }
                
                await db.execute(insert(User).values(**user_data))
                print(f"  ✅ Added {member['name']} (ID: {i})")
            
            # Create sample goals for each user
            print(f"\n🎯 Creating weekly goals for each member...")
            
            for user_id in range(1, len(channel_members) + 1):
                goal_data = {
                    "id": user_id,
                    "description": f"Weekly Sales Goals - Week {datetime.now().strftime('%W')}: Complete calls, demos, and proposals",
                    "week_start": datetime.now().date(),
                    "achieved": False,
                    "owner_id": user_id,
                    "project_id": 1
                }
                
                await db.execute(insert(Goal).values(**goal_data))
            
            # Create sample tasks for the first user to show progress
            if len(channel_members) > 0:
                print(f"\n📋 Creating sample tasks for {channel_members[0]['name']}...")
                
                sample_tasks = [
                    {"title": "Discovery Call #1", "type": "call", "status": "completed"},
                    {"title": "Discovery Call #2", "type": "call", "status": "completed"},
                    {"title": "Discovery Call #3", "type": "call", "status": "pending"},
                    {"title": "Product Demo #1", "type": "demo", "status": "completed"},
                    {"title": "Product Demo #2", "type": "demo", "status": "pending"},
                    {"title": "Sales Proposal #1", "type": "proposal", "status": "pending"}
                ]
                
                for task_num, task_info in enumerate(sample_tasks, 1):
                    task_data = {
                        "id": task_num,
                        "title": task_info["title"],
                        "description": f"Sample {task_info['type']} task",
                        "status": task_info["status"],
                        "task_type": task_info["type"],
                        "due_date": datetime.now().date(),
                        "completed_at": datetime.now() if task_info["status"] == "completed" else None,
                        "owner_id": 1,  # First user
                        "project_id": 1
                    }
                    await db.execute(insert(Task).values(**task_data))
            
            await db.commit()
            
            print(f"✅ Database setup completed!")
            
            # Verify the setup
            print(f"\n🔍 Verifying database setup...")
            
            # Count users
            user_count = await db.execute(select(User))
            users = user_count.scalars().all()
            
            # Count tasks
            task_count = await db.execute(select(Task))
            tasks = task_count.scalars().all()
            
            # Count goals
            goal_count = await db.execute(select(Goal))
            goals = goal_count.scalars().all()
            
            print(f"✅ Database verification:")
            print(f"   👥 Users: {len(users)}")
            print(f"   🎯 Goals: {len(goals)}")
            print(f"   📋 Tasks: {len(tasks)}")
            
            break  # Exit the async generator loop
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

async def main():
    """Main function"""
    print("🚀 DealTracker: Setting up database with #psv-sales-agent channel members")
    print("=" * 70)
    
    # Get actual channel members
    channel_members = await get_channel_members()
    
    if not channel_members:
        print("❌ No channel members found! Cannot proceed.")
        return
    
    # Set up database with channel members
    success = await setup_database_with_channel_members(channel_members)
    
    if success:
        print(f"\n🎉 **DATABASE SETUP SUCCESSFUL!**")
        print(f"✅ #psv-sales-agent channel members ({len(channel_members)}) added to database")
        print(f"✅ Sample goals and tasks created")
        print(f"✅ Database ready for AI automation")
        
        print(f"\n📊 **Team Summary:**")
        for i, member in enumerate(channel_members, 1):
            print(f"• **{member['name']}** - Ready for sales tracking")
        
        print(f"\n🎯 **Next Steps:**")
        print(f"1. Frontend dashboard will show {len(channel_members)} team members")
        print(f"2. Progress tracking is ready for actual channel members")
        print(f"3. AI automation will target only #psv-sales-agent members")
        print(f"4. All messages will go to the correct users")
        
        print(f"\n🚀 **Your DealTracker is ready with real channel data!**")
        
    else:
        print(f"\n❌ Failed to set up database!")

if __name__ == "__main__":
    asyncio.run(main()) 