#!/usr/bin/env python3
"""
Set up database with real Pacific Software Ventures team members
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert, text
from app.database import get_db
from app.models import User, Project, Task, Goal
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

async def setup_database_with_real_team():
    """Set up database with real team members from Slack channel"""
    
    print("🗄️ Setting up database with Pacific Software Ventures team...")
    print("=" * 60)
    
    # Real team members from your Slack workspace
    real_team_members = [
        {
            "name": "Gedeon Baende",
            "slack_id": "U08E2VCC1FB",
            "email": "gedeon@pacificsoftwareventures.com",
            "role": "Sales Manager"
        },
        {
            "name": "Aidan Scudder", 
            "slack_id": "U06T93G62E5",
            "email": "aidan@pacificsoftwareventures.com",
            "role": "Sales Rep"
        },
        {
            "name": "Sanjay Thasma",
            "slack_id": "U06TAA2A73K", 
            "email": "thasma@wisc.edu",
            "role": "Sales Rep"
        },
        {
            "name": "Srivatsaan Kalpana Sreenivasan",
            "slack_id": "U06U834B04B",
            "email": "kssrivatsaan@gmail.com",
            "role": "Sales Rep"
        },
        {
            "name": "Aaryaman Singh",
            "slack_id": "U06ULS4GQTT",
            "email": "singh283@wisc.edu",
            "role": "Sales Rep"
        },
        {
            "name": "Gabriel Krishnadasan",
            "slack_id": "U070H8SGLJC",
            "email": "gkrishnadasan@sandiego.edu",
            "role": "Sales Rep"
        }
    ]
    
    print(f"👥 **Team Size: {len(real_team_members)} members**")
    for i, member in enumerate(real_team_members, 1):
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
            
            # Create project for Pacific Software Ventures
            print(f"\n📁 Creating Pacific Software Ventures project...")
            
            project_data = {
                "id": 1,
                "name": "Pacific Software Ventures Sales",
                "description": "Sales activities for Pacific Software Ventures team",
                "owner_id": 1  # Will be Gedeon
            }
            
            await db.execute(insert(Project).values(**project_data))
            print(f"✅ Project created: {project_data['name']}")
            
            # Insert real team members
            print(f"\n👥 Adding {len(real_team_members)} team members...")
            
            for i, member in enumerate(real_team_members, 1):
                user_data = {
                    "id": i,
                    "name": member["name"],
                    "email": member["email"],
                    "slack_user_id": member["slack_id"],
                    "role": "sales"  # All are sales team members
                }
                
                await db.execute(insert(User).values(**user_data))
                print(f"  ✅ Added {member['name']} (ID: {i})")
            
            # Create some sample goals and tasks for demonstration
            print(f"\n🎯 Creating sample goals and tasks...")
            
            # Create goals for each user
            for user_id in range(1, len(real_team_members) + 1):
                # Weekly goals
                goal_data = {
                    "id": user_id,
                    "user_id": user_id,
                    "project_id": 1,
                    "goal_type": "weekly",
                    "target_calls": 20,
                    "target_demos": 5,
                    "target_proposals": 2,
                    "week_start": datetime.now().date(),
                    "week_end": (datetime.now() + timedelta(days=6)).date(),
                    "is_active": True
                }
                
                await db.execute(insert(Goal).values(**goal_data))
                
                # Create some sample tasks for the first user (Gedeon) to show progress
                if user_id == 1:
                    # Create 15 call tasks (12 completed, 3 pending)
                    for task_num in range(1, 16):
                        task_data = {
                            "id": task_num,
                            "user_id": user_id,
                            "project_id": 1,
                            "title": f"Discovery Call #{task_num}",
                            "description": f"Outreach call to prospect #{task_num}",
                            "task_type": "call",
                            "status": "completed" if task_num <= 12 else "pending",
                            "due_date": datetime.now().date(),
                            "completed_at": datetime.now() if task_num <= 12 else None
                        }
                        await db.execute(insert(Task).values(**task_data))
                    
                    # Create 2 demo tasks (1 completed, 1 pending)
                    for demo_num in range(1, 3):
                        task_data = {
                            "id": 15 + demo_num,
                            "user_id": user_id,
                            "project_id": 1,
                            "title": f"Product Demo #{demo_num}",
                            "description": f"Demo presentation for prospect #{demo_num}",
                            "task_type": "demo",
                            "status": "completed" if demo_num == 1 else "pending",
                            "due_date": datetime.now().date(),
                            "completed_at": datetime.now() if demo_num == 1 else None
                        }
                        await db.execute(insert(Task).values(**task_data))
                    
                    # Create 1 proposal task (pending)
                    task_data = {
                        "id": 18,
                        "user_id": user_id,
                        "project_id": 1,
                        "title": "Proposal #1",
                        "description": "Sales proposal for qualified prospect",
                        "task_type": "proposal",
                        "status": "pending",
                        "due_date": datetime.now().date()
                    }
                    await db.execute(insert(Task).values(**task_data))
            
            await db.commit()
            
            print(f"✅ Sample goals and tasks created")
            
            # Verify the setup
            print(f"\n🔍 Verifying database setup...")
            
            # Count users
            user_count = await db.execute(select(User).count())
            user_total = user_count.scalar()
            
            # Count tasks
            task_count = await db.execute(select(Task).count())
            task_total = task_count.scalar()
            
            # Count goals
            goal_count = await db.execute(select(Goal).count())
            goal_total = goal_count.scalar()
            
            print(f"✅ Database verification:")
            print(f"   👥 Users: {user_total}")
            print(f"   🎯 Goals: {goal_total}")
            print(f"   📋 Tasks: {task_total}")
            
            break  # Exit the async generator loop
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

async def test_api_endpoints():
    """Test the API endpoints to make sure they work"""
    
    print(f"\n🧪 Testing API endpoints...")
    
    import requests
    
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/api/sales/progress/team",
        "/api/sales/leaderboard/current",
        "/api/sales/scheduler/status"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working")
            else:
                print(f"❌ {endpoint} - Error {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Connection error: {e}")

async def main():
    """Main function"""
    print("🚀 DealTracker: Setting up database with real Pacific Software Ventures team")
    print("=" * 70)
    
    success = await setup_database_with_real_team()
    
    if success:
        print(f"\n🎉 **DATABASE SETUP SUCCESSFUL!**")
        print(f"✅ Pacific Software Ventures team (6 members) added to database")
        print(f"✅ Sample goals and tasks created")
        print(f"✅ Database ready for AI automation")
        
        print(f"\n📊 **Team Progress Summary:**")
        print(f"• **Gedeon Baende** - 12/20 calls (60%), 1/5 demos (20%), 0/2 proposals (0%)")
        print(f"• **Other team members** - Goals set, ready to track progress")
        
        print(f"\n🎯 **Next Steps:**")
        print(f"1. Frontend dashboard should now work without errors")
        print(f"2. Team size will show 6 members")
        print(f"3. Progress tracking is ready")
        print(f"4. AI automation can track real progress")
        
        # Test API endpoints
        await test_api_endpoints()
        
        print(f"\n🚀 **Your DealTracker is ready with real team data!**")
        
    else:
        print(f"\n❌ Failed to set up database!")

if __name__ == "__main__":
    asyncio.run(main()) 