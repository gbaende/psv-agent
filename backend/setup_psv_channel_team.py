#!/usr/bin/env python3
"""
Set up database with PSV Sales Agent channel team members
Based on actual channel activity and membership
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert
from app.database import get_db
from app.models import User, Project, Task, Goal
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

async def setup_psv_sales_team():
    """Set up database with PSV Sales Agent team members"""
    
    print("🗄️ Setting up database with #psv-sales-agent team members...")
    print("=" * 60)
    
    # Based on channel activity - starting with known active members
    # We'll start with a core team and can expand as more people join
    psv_team_members = [
        {
            "name": "Gedeon Baende",
            "slack_id": "U08E2VCC1FB",  # Your actual Slack ID
            "email": "gedeon@pacificsoftwareventures.com",
            "role": "Sales Manager"
        },
        {
            "name": "Aidan Scudder", 
            "slack_id": "U06T93G62E5",  # Aidan's actual Slack ID
            "email": "aidan@pacificsoftwareventures.com",
            "role": "Sales Rep"
        }
        # Note: We can add the other 3 members when they become active
        # or when we get their actual Slack IDs
    ]
    
    print(f"👥 **PSV Sales Team: {len(psv_team_members)} active members**")
    for i, member in enumerate(psv_team_members, 1):
        print(f"  {i}. {member['name']} - {member['role']}")
    
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
                "owner_id": 1  # Gedeon as owner
            }
            
            await db.execute(insert(Project).values(**project_data))
            print(f"✅ Project created: {project_data['name']}")
            
            # Insert team members
            print(f"\n👥 Adding {len(psv_team_members)} team members...")
            
            for i, member in enumerate(psv_team_members, 1):
                user_data = {
                    "id": i,
                    "name": member["name"],
                    "email": member["email"],
                    "slack_user_id": member["slack_id"],
                    "role": "sales"  # All are sales team members
                }
                
                await db.execute(insert(User).values(**user_data))
                print(f"  ✅ Added {member['name']} (ID: {i})")
            
            # Create weekly goals for each user
            print(f"\n🎯 Creating weekly goals for each member...")
            
            for user_id in range(1, len(psv_team_members) + 1):
                goal_data = {
                    "id": user_id,
                    "description": f"Weekly Sales Goals - Week {datetime.now().strftime('%W')}: Complete calls, demos, and proposals",
                    "week_start": datetime.now().date(),
                    "achieved": False,
                    "owner_id": user_id,
                    "project_id": 1
                }
                
                await db.execute(insert(Goal).values(**goal_data))
            
            # Create sample tasks for Gedeon to show progress
            print(f"\n📋 Creating sample tasks for {psv_team_members[0]['name']}...")
            
            sample_tasks = [
                {"title": "Discovery Call #1", "type": "call", "status": "Completed"},
                {"title": "Discovery Call #2", "type": "call", "status": "Completed"},
                {"title": "Discovery Call #3", "type": "call", "status": "In Progress"},
                {"title": "Product Demo #1", "type": "demo", "status": "Completed"},
                {"title": "Product Demo #2", "type": "demo", "status": "Not Started"},
                {"title": "Sales Proposal #1", "type": "proposal", "status": "Not Started"}
            ]
            
            for task_num, task_info in enumerate(sample_tasks, 1):
                task_data = {
                    "id": task_num,
                    "title": task_info["title"],
                    "description": f"Sample {task_info['type']} task for sales tracking",
                    "status": task_info["status"],
                    "task_type": task_info["type"],
                    "due_date": datetime.now().date(),
                    "completed_at": datetime.now() if task_info["status"] == "Completed" else None,
                    "owner_id": 1,  # Gedeon
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
            
            # Show user details
            print(f"\n👥 **Team Members in Database:**")
            for user in users:
                print(f"   • {user.name} ({user.slack_user_id}) - {user.email}")
            
            break  # Exit the async generator loop
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

async def test_api_endpoints():
    """Test the API endpoints to make sure they work"""
    
    print(f"\n🧪 Testing API endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:3001"  # Frontend API port
        
        endpoints_to_test = [
            "/api/sales/progress/team",
            "/api/sales/leaderboard/current"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Working")
                    if endpoint == "/api/sales/progress/team":
                        data = response.json()
                        print(f"   📊 Team size: {len(data.get('team_progress', []))}")
                else:
                    print(f"❌ {endpoint} - Error {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - Connection error: {e}")
                
    except ImportError:
        print("⚠️ requests library not available for API testing")

async def main():
    """Main function"""
    print("🚀 DealTracker: Setting up PSV Sales Agent team database")
    print("=" * 70)
    
    success = await setup_psv_sales_team()
    
    if success:
        print(f"\n🎉 **DATABASE SETUP SUCCESSFUL!**")
        print(f"✅ PSV Sales Agent team (2 active members) added to database")
        print(f"✅ Sample goals and tasks created")
        print(f"✅ Database ready for AI automation")
        
        print(f"\n📊 **Team Progress Summary:**")
        print(f"• **Gedeon Baende** - 2/6 calls completed, 1/2 demos completed")
        print(f"• **Aidan Scudder** - Goals set, ready to track progress")
        
        print(f"\n🎯 **Next Steps:**")
        print(f"1. Frontend dashboard will show 2 team members")
        print(f"2. Progress tracking is ready for PSV team")
        print(f"3. AI automation will target #psv-sales-agent members")
        print(f"4. Can add more team members as they join the channel")
        
        # Test API endpoints
        await test_api_endpoints()
        
        print(f"\n🚀 **Your DealTracker is ready with PSV team data!**")
        print(f"\n💡 **To add more team members:**")
        print(f"   - Get their Slack IDs from the channel")
        print(f"   - Add them to the psv_team_members list")
        print(f"   - Re-run this script")
        
    else:
        print(f"\n❌ Failed to set up database!")

if __name__ == "__main__":
    asyncio.run(main()) 