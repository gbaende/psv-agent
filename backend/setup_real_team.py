#!/usr/bin/env python3
"""
Set up sales team based on actual Slack channel members
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert
from app.database import get_db
from app.models import User, Project, Task, Goal
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def setup_real_sales_team():
    """Set up sales team based on actual Slack channel members"""
    
    print("🔍 Setting up sales team from Slack channel members...")
    
    # Initialize Slack service
    slack_service = SlackService()
    
    if not slack_service.is_configured():
        print("❌ Slack service is not properly configured!")
        return
    
    channel_id = os.getenv('SLACK_CHANNEL_ID')
    if not channel_id:
        print("❌ SLACK_CHANNEL_ID not found in environment!")
        return
    
    try:
        # Get channel info
        print(f"\n📢 Getting channel info for {channel_id}...")
        channel_response = await slack_service.client.conversations_info(channel=channel_id)
        
        if not channel_response["ok"]:
            print(f"❌ Failed to get channel info: {channel_response}")
            return
        
        channel = channel_response["channel"]
        channel_name = channel['name']
        print(f"✅ Channel: #{channel_name}")
        
        # Get channel members
        print(f"\n👥 Getting channel members...")
        members_response = await slack_service.client.conversations_members(channel=channel_id)
        
        if not members_response["ok"]:
            print(f"❌ Failed to get channel members: {members_response}")
            return
        
        member_ids = members_response["members"]
        print(f"✅ Found {len(member_ids)} members in #{channel_name}")
        
        # Get user details for each member
        print(f"\n📋 Getting user details...")
        channel_users = []
        
        for member_id in member_ids:
            try:
                user_response = await slack_service.client.users_info(user=member_id)
                if user_response["ok"]:
                    user = user_response["user"]
                    
                    # Skip bots and deleted users
                    if not user.get("is_bot", False) and not user.get("deleted", False):
                        user_info = {
                            "slack_id": user["id"],
                            "name": user.get("real_name", user.get("name", "Unknown")),
                            "display_name": user.get("profile", {}).get("display_name", ""),
                            "email": user.get("profile", {}).get("email", ""),
                            "is_admin": user.get("is_admin", False),
                            "is_owner": user.get("is_owner", False)
                        }
                        channel_users.append(user_info)
                        print(f"  ✅ {user_info['name']} ({user_info['slack_id']})")
                        if user_info['email']:
                            print(f"     📧 {user_info['email']}")
                        
            except Exception as e:
                print(f"  ❌ Error getting user {member_id}: {e}")
        
        print(f"\n🎯 Real team members: {len(channel_users)} users")
        
        # Set up database with real team
        await setup_database_with_real_team(channel_users, channel_name)
        
        # Test sending messages to the real team
        await test_real_team_messages(slack_service, channel_users)
        
        return channel_users
        
    except Exception as e:
        print(f"❌ Error setting up real team: {e}")
        return None

async def setup_database_with_real_team(channel_users, channel_name):
    """Set up database with real team members"""
    
    print(f"\n🗄️ Setting up database with real team...")
    
    try:
        async for db in get_db():
            # Clear existing data
            print("🧹 Clearing existing test data...")
            await db.execute(delete(Task))
            await db.execute(delete(Goal))
            await db.execute(delete(User))
            await db.execute(delete(Project))
            await db.commit()
            
            # Create a real project
            print(f"📁 Creating project for #{channel_name}...")
            project_data = {
                "name": f"Sales Team - {channel_name}",
                "description": f"Sales activities for the {channel_name} team",
                "owner_id": 1  # Will update after creating users
            }
            
            # Insert users
            print(f"👥 Adding {len(channel_users)} real users...")
            user_ids = []
            
            for i, user in enumerate(channel_users, 1):
                user_data = {
                    "id": i,
                    "name": user["name"],
                    "email": user["email"] or f"{user['name'].lower().replace(' ', '.')}@example.com",
                    "slack_user_id": user["slack_id"],
                    "role": "sales"  # All channel members are sales team
                }
                
                result = await db.execute(
                    insert(User).values(**user_data)
                )
                user_ids.append(i)
                print(f"  ✅ Added {user['name']} (ID: {i})")
            
            # Create project with first user as owner
            project_data["owner_id"] = user_ids[0]
            result = await db.execute(
                insert(Project).values(**project_data)
            )
            project_id = 1  # First project
            
            await db.commit()
            
            print(f"✅ Database setup complete!")
            print(f"   📁 Project: {project_data['name']}")
            print(f"   👥 Users: {len(user_ids)} sales team members")
            
            break  # Exit the async generator loop
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

async def test_real_team_messages(slack_service, channel_users):
    """Test sending messages to the real team"""
    
    print(f"\n💬 Testing messages to real team...")
    
    # Send a welcome message to each team member
    welcome_message = """🎉 **Welcome to DealTracker Sales Automation!**

Hi there! I'm your new AI Sales Agent, and I'm here to help you crush your sales goals! 🚀

**What I can do for you:**
📞 Help you set and track weekly call targets
🎬 Monitor demo and presentation goals  
📋 Track proposal submissions
🏆 Celebrate your achievements
💡 Provide personalized coaching tips

**Getting Started:**
Every Monday, I'll send you a goal-setting prompt. Just reply with your weekly targets like:
"I'll do 15 calls, 4 demos, and 2 proposals this week"

Let's make this week amazing! 💪

*This is an automated message from DealTracker Sales Agent*"""
    
    success_count = 0
    for user in channel_users:
        try:
            print(f"📤 Sending welcome message to {user['name']}...")
            
            result = await slack_service.send_direct_message(
                user_id=user['slack_id'],
                text=welcome_message
            )
            
            if result.get("ok"):
                print(f"  ✅ Welcome sent to {user['name']}")
                success_count += 1
            else:
                print(f"  ❌ Failed to send to {user['name']}: {result}")
                
        except Exception as e:
            print(f"  ❌ Error sending to {user['name']}: {e}")
    
    print(f"\n🎯 Welcome messages sent: {success_count}/{len(channel_users)}")
    
    # Send a test Monday prompt to the first user
    if channel_users:
        test_user = channel_users[0]
        print(f"\n🎯 Sending test Monday prompt to {test_user['name']}...")
        
        monday_prompt = f"""🎯 **Monday Goal Setting - {test_user['name'].split()[0]}!**

Ready to start the week strong? Let's set your sales targets:

📞 **Discovery Calls** - How many prospects will you contact?
🎬 **Demos/Presentations** - How many demos will you deliver?
📋 **Proposals** - How many proposals will you submit?

**Example responses:**
• "20 calls, 5 demos, 2 proposals"
• "I'll do 15 calls and 3 demos this week"
• "Target: 25 calls, 4 demos, 1 proposal"

Just reply with your numbers and I'll track your progress! 💪

*DealTracker Sales Agent - Automated Monday Check-in*"""
        
        try:
            result = await slack_service.send_direct_message(
                user_id=test_user['slack_id'],
                text=monday_prompt
            )
            
            if result.get("ok"):
                print(f"  ✅ Monday prompt sent to {test_user['name']}")
            else:
                print(f"  ❌ Failed to send Monday prompt: {result}")
                
        except Exception as e:
            print(f"  ❌ Error sending Monday prompt: {e}")

async def main():
    """Main function"""
    print("🚀 DealTracker: Setting up real sales team from Slack channel")
    print("=" * 60)
    
    team_members = await setup_real_sales_team()
    
    if team_members:
        print(f"\n🎉 **SUCCESS!** Real sales team is now set up!")
        print(f"✅ Team size: {len(team_members)} members")
        print(f"✅ Database updated with real users")
        print(f"✅ Welcome messages sent to team")
        print(f"✅ Test Monday prompt sent")
        
        print(f"\n👥 **Your Sales Team:**")
        for i, user in enumerate(team_members, 1):
            print(f"  {i}. {user['name']} ({user['slack_id']})")
            if user['email']:
                print(f"     📧 {user['email']}")
        
        print(f"\n🎯 **Next Steps:**")
        print(f"1. Check your Slack DMs for welcome messages")
        print(f"2. Reply to the Monday prompt to test goal setting")
        print(f"3. Run the full automation with your real team!")
        print(f"4. Use the dashboard to track real progress")
        
    else:
        print(f"\n❌ Failed to set up real sales team!")

if __name__ == "__main__":
    asyncio.run(main()) 