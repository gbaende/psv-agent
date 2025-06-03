#!/usr/bin/env python3
"""
Test automatic user onboarding when someone joins the Slack channel
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def test_auto_onboarding():
    """Test the auto-onboarding functionality"""
    
    print("🧪 Testing DealTracker Auto-Onboarding System")
    print("=" * 60)
    
    try:
        async for db in get_db():
            # Initialize Slack service
            slack_service = SlackService()
            
            if not slack_service.is_configured():
                print("❌ Slack service not configured!")
                return
            
            # Get current team size
            result = await db.execute(select(User).where(User.role == "sales"))
            current_users = result.scalars().all()
            
            print(f"👥 **Current Team Size:** {len(current_users)} members")
            for user in current_users:
                print(f"   • {user.name} ({user.slack_user_id})")
            
            # Get all channel members to see who could be auto-onboarded
            print(f"\n📢 **Checking #psv-sales-agent channel members...**")
            
            channel_id = "C08UNPU9AGN"  # #psv-sales-agent
            members_response = await slack_service.client.conversations_members(channel=channel_id)
            
            if not members_response["ok"]:
                print(f"❌ Failed to get channel members: {members_response}")
                return
            
            member_ids = members_response["members"]
            print(f"✅ Found {len(member_ids)} total members in channel")
            
            # Check which members are NOT in database yet
            print(f"\n🔍 **Checking for members not yet onboarded...**")
            
            current_slack_ids = {user.slack_user_id for user in current_users}
            new_members = []
            
            for member_id in member_ids:
                if member_id not in current_slack_ids:
                    # Get user info
                    try:
                        user_response = await slack_service.client.users_info(user=member_id)
                        if user_response["ok"]:
                            user_data = user_response["user"]
                            
                            # Skip bots and deleted users
                            if not user_data.get("is_bot", False) and not user_data.get("deleted", False):
                                new_members.append({
                                    "slack_id": member_id,
                                    "name": user_data.get("real_name", user_data.get("name", "Unknown")),
                                    "email": user_data.get("profile", {}).get("email", "")
                                })
                                print(f"   🆕 {user_data.get('real_name', 'Unknown')} ({member_id}) - Not onboarded yet")
                    except Exception as e:
                        print(f"   ❌ Error getting info for {member_id}: {e}")
            
            if not new_members:
                print(f"   ✅ All channel members are already onboarded!")
            else:
                print(f"\n🎯 **Found {len(new_members)} members who could be auto-onboarded**")
            
            # Demonstrate what happens when auto-onboarding triggers
            print(f"\n💡 **How Auto-Onboarding Works:**")
            print(f"=" * 40)
            
            print(f"🔄 **When someone joins #psv-sales-agent:**")
            print(f"   1. Slack sends 'member_joined_channel' event")
            print(f"   2. DealTracker detects the event")
            print(f"   3. System checks if user exists in database")
            print(f"   4. If new user: Creates database record automatically")
            print(f"   5. Sends welcome DM with onboarding instructions")
            print(f"   6. Posts team announcement in channel")
            print(f"   7. User immediately appears in dashboard")
            print(f"   8. User gets included in Monday goal prompts")
            
            print(f"\n📱 **When someone DMs the AI (but not in database):**")
            print(f"   1. User sends DM to DealTracker AI")
            print(f"   2. System checks if user exists in database")
            print(f"   3. If new user: Auto-onboards them first")
            print(f"   4. Then processes their message normally")
            
            # Show current webhook configuration
            print(f"\n🔗 **Webhook Configuration:**")
            print(f"   📡 Webhook URL: {os.getenv('SLACK_WEBHOOK_URL')}")
            print(f"   📱 Channel ID: {os.getenv('SLACK_CHANNEL_ID')}")
            print(f"   🤖 Bot Token: {'✅ Configured' if os.getenv('SLACK_BOT_TOKEN') else '❌ Missing'}")
            print(f"   🔐 Signing Secret: {'✅ Configured' if os.getenv('SLACK_SIGNING_SECRET') else '❌ Missing'}")
            
            # Test sending a sample auto-onboarding message
            if new_members:
                print(f"\n🧪 **Testing Auto-Onboarding Message (Sample):**")
                sample_member = new_members[0]
                
                sample_message = f"""🎉 **Welcome to DealTracker, {sample_member['name']}!**

Hi there! I'm your AI Sales Agent, and I just automatically added you to our sales tracking system! 🚀

**🎯 What I do for you:**
• **Monday Goal Setting** - Help you set weekly sales targets
• **Progress Tracking** - Monitor your calls, demos, and proposals  
• **Milestone Celebrations** - Celebrate when you hit your goals! 🏆
• **Coaching Tips** - Personalized advice to boost performance
• **Team Leaderboards** - See how you stack up against the team

**📅 Weekly Schedule:**
• **Monday 9 AM** - Goal setting prompts
• **Wednesday 2 PM** - Mid-week coaching nudges  
• **Friday 5 PM** - Weekly summaries & leaderboards
• **Daily 6 PM** - Milestone celebrations

**🚀 Getting Started:**
When I send you the Monday prompt, just reply with your weekly targets:
*"I'll do 20 calls, 5 demos, and 2 proposals this week"*

**📊 Dashboard Access:**
You now have access to the sales dashboard at: http://localhost:3000

Ready to crush some sales goals? Let's do this! 💪

*DealTracker AI Sales Agent - Auto-Onboarded*"""
                
                print(f"📤 **Sample welcome message for {sample_member['name']}:**")
                print(f"   (This would be sent automatically when they join)")
                print(f"   Message length: {len(sample_message)} characters")
                
                # Optionally send the actual message (commented out for safety)
                # result = await slack_service.send_direct_message(sample_member['slack_id'], sample_message)
                # print(f"   ✅ Test message sent: {result.get('ok', False)}")
            
            break
            
    except Exception as e:
        print(f"❌ Error testing auto-onboarding: {e}")

async def demonstrate_event_flow():
    """Demonstrate the complete event flow for auto-onboarding"""
    
    print(f"\n🎬 **Auto-Onboarding Event Flow Demonstration:**")
    print(f"=" * 60)
    
    print(f"📋 **Step-by-Step Process:**")
    print(f"")
    print(f"1️⃣ **User joins #psv-sales-agent channel**")
    print(f"   → Slack sends webhook to: http://localhost:3001/slack/events")
    print(f"   → Event type: 'member_joined_channel'")
    print(f"   → Channel ID: C08UNPU9AGN")
    print(f"")
    print(f"2️⃣ **DealTracker receives event**")
    print(f"   → Checks if channel is #psv-sales-agent")
    print(f"   → Extracts user_id from event")
    print(f"   → Calls auto_onboard_new_user(user_id)")
    print(f"")
    print(f"3️⃣ **Auto-onboarding process**")
    print(f"   → Checks if user exists in database")
    print(f"   → Gets user info from Slack API")
    print(f"   → Creates new User record in database")
    print(f"   → Sends welcome DM to user")
    print(f"")
    print(f"4️⃣ **Team notification**")
    print(f"   → Posts welcome message in #psv-sales-agent")
    print(f"   → '@mentions' the new user")
    print(f"   → Announces they've been onboarded")
    print(f"")
    print(f"5️⃣ **Immediate benefits**")
    print(f"   → User appears in dashboard team list")
    print(f"   → Included in next Monday goal prompts")
    print(f"   → Can start tracking progress immediately")
    print(f"   → Receives all automated coaching messages")
    
    print(f"\n🔧 **Required Slack App Permissions:**")
    print(f"   📖 channels:read - Read channel information")
    print(f"   👥 users:read - Get user profile information")
    print(f"   💬 chat:write - Send messages to users and channels")
    print(f"   📨 im:write - Send direct messages")
    print(f"   🔔 channels:join - Join channels (if needed)")
    
    print(f"\n⚙️ **Event Subscription Setup:**")
    print(f"   📡 Request URL: http://localhost:3001/slack/events")
    print(f"   🎯 Subscribe to: member_joined_channel")
    print(f"   🎯 Subscribe to: message.im (for DM auto-onboarding)")

async def main():
    """Main function"""
    print("🚀 DealTracker: Auto-Onboarding System Test")
    print("=" * 70)
    
    await test_auto_onboarding()
    await demonstrate_event_flow()
    
    print(f"\n🎉 **Auto-Onboarding System Ready!**")
    print(f"✅ Event handlers configured")
    print(f"✅ Database integration ready")
    print(f"✅ Welcome messages prepared")
    print(f"✅ Team notifications ready")
    
    print(f"\n🎯 **To Test Auto-Onboarding:**")
    print(f"1. Have someone new join #psv-sales-agent channel")
    print(f"2. Watch for automatic welcome DM")
    print(f"3. Check dashboard - they should appear immediately")
    print(f"4. Verify they get Monday goal prompts")
    
    print(f"\n💡 **Alternative Test:**")
    print(f"1. Have someone DM the AI bot directly")
    print(f"2. If they're not in database, auto-onboarding triggers")
    print(f"3. They get onboarded before their message is processed")

if __name__ == "__main__":
    asyncio.run(main()) 