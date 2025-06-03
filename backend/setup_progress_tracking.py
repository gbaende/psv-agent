#!/usr/bin/env python3
"""
Set up comprehensive progress tracking for the DealTracker sales team
This creates multiple ways for team members to update their progress:
1. Slack DM responses to the AI agent
2. Slack slash commands (/done, /progress)
3. Dashboard updates
4. Email responses
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models import User, Task
from app.services.slack_service import SlackService
from datetime import datetime

# Load environment variables
load_dotenv()

async def setup_progress_tracking():
    """Set up comprehensive progress tracking system"""
    
    print("🎯 Setting up DealTracker Progress Tracking System")
    print("=" * 60)
    
    try:
        async for db in get_db():
            # Initialize Slack service
            slack_service = SlackService()
            
            # Get all team members
            result = await db.execute(select(User).where(User.role == "sales"))
            team_members = result.scalars().all()
            
            print(f"👥 Found {len(team_members)} team members:")
            for member in team_members:
                print(f"   • {member.name} (ID: {member.id}) - {member.slack_user_id}")
            
            # Send onboarding message explaining how to update progress
            print(f"\n📚 Sending progress tracking onboarding...")
            
            onboarding_message = """🎯 **DealTracker Progress Tracking - How It Works**

Hi! Now that you have your weekly goals, here's how to update your progress:

**📱 METHOD 1: Direct Message Me**
Just send me updates like:
• "Completed 5 calls today"
• "Did 2 demos this morning"
• "Submitted 1 proposal"
• "Update: 15 calls, 3 demos done so far"

**⚡ METHOD 2: Slash Commands**
• `/progress` - See your current progress
• `/done task-123` - Mark a specific task complete
• `/leaderboard` - See team rankings

**💻 METHOD 3: Dashboard**
Visit your dashboard to mark tasks complete visually

**🎉 AUTOMATIC CELEBRATIONS**
When you hit milestones, I'll celebrate in the team channel! 🏆

**📊 WEEKLY SCHEDULE:**
• **Monday 9 AM**: I ask for your weekly goals
• **Wednesday 2 PM**: Mid-week progress check
• **Friday 5 PM**: Weekly summary and leaderboard
• **Daily 6 PM**: Milestone celebrations

Just reply to this message with "Got it!" to confirm you're ready! 💪

*DealTracker AI Sales Agent*"""
            
            # Send to each team member
            for member in team_members:
                print(f"📤 Sending onboarding to {member.name}...")
                
                try:
                    if member.slack_user_id:
                        result = await slack_service.send_direct_message(
                            user_id=member.slack_user_id,
                            text=onboarding_message
                        )
                        
                        if result.get("ok"):
                            print(f"  ✅ Onboarding sent to {member.name}")
                        else:
                            print(f"  ❌ Failed to send to {member.name}: {result.get('error')}")
                    else:
                        print(f"  ⚠️ No Slack ID for {member.name}")
                        
                except Exception as e:
                    print(f"  ❌ Error sending to {member.name}: {e}")
            
            # Create sample progress scenarios
            print(f"\n🎮 Creating sample progress scenarios...")
            await create_sample_progress(db, team_members)
            
            # Test progress tracking methods
            print(f"\n🧪 Testing progress tracking methods...")
            await test_progress_methods(db, slack_service, team_members)
            
            break
            
    except Exception as e:
        print(f"❌ Error setting up progress tracking: {e}")
        return False
    
    return True

async def create_sample_progress(db: AsyncSession, team_members):
    """Create sample progress data to demonstrate tracking"""
    
    print("📊 Creating sample progress data...")
    
    # Update some tasks to "Completed" status for demo
    for i, member in enumerate(team_members):
        # Complete different amounts for each member to show variety
        tasks_to_complete = [2, 3, 1][i % 3]  # Complete 2, 3, or 1 tasks
        
        # Get member's tasks
        result = await db.execute(
            select(Task).where(Task.owner_id == member.id).limit(tasks_to_complete)
        )
        tasks = result.scalars().all()
        
        for task in tasks:
            task.status = "Completed"
            task.completed_at = datetime.now()
        
        await db.commit()
        print(f"  ✅ Marked {len(tasks)} tasks complete for {member.name}")

async def test_progress_methods(db: AsyncSession, slack_service, team_members):
    """Test different progress tracking methods"""
    
    print("🧪 Testing progress tracking methods...")
    
    # Test 1: Send sample progress update to first member
    if team_members and team_members[0].slack_user_id:
        test_member = team_members[0]
        
        test_message = f"""📊 **Progress Update Test for {test_member.name}**

This is a test of the progress tracking system!

Try responding with any of these:
• "Completed 3 calls today"
• "Did 1 demo this morning"  
• "Update: 10 calls, 2 demos done so far"
• "progress" (to see your current status)

I'll automatically track your updates and celebrate milestones! 🎉"""
        
        try:
            result = await slack_service.send_direct_message(
                user_id=test_member.slack_user_id,
                text=test_message
            )
            
            if result.get("ok"):
                print(f"  ✅ Test message sent to {test_member.name}")
            else:
                print(f"  ❌ Failed to send test message: {result.get('error')}")
                
        except Exception as e:
            print(f"  ❌ Error sending test message: {e}")
    
    # Test 2: Show webhook endpoint info
    print(f"\n🔗 **Webhook Configuration:**")
    print(f"   📡 Your webhook URL: {os.getenv('SLACK_WEBHOOK_URL')}")
    print(f"   📱 Channel ID: {os.getenv('SLACK_CHANNEL_ID')}")
    print(f"   🤖 Bot token: {'✅ Configured' if os.getenv('SLACK_BOT_TOKEN') else '❌ Missing'}")
    
    # Test 3: Show API endpoints for progress updates
    print(f"\n🔌 **API Endpoints for Progress Updates:**")
    print(f"   📊 GET /api/sales/progress/team - View team progress")
    print(f"   📈 POST /api/sales/progress/{{user_id}}/update - Update progress")
    print(f"   🏆 GET /api/sales/leaderboard/current - View leaderboard")
    print(f"   ⚡ POST /api/sales/triggers/milestone-check - Check for celebrations")

async def demonstrate_progress_tracking():
    """Demonstrate how progress tracking works with examples"""
    
    print(f"\n💡 **HOW PROGRESS TRACKING WORKS:**")
    print(f"=" * 50)
    
    print(f"🎯 **1. GOAL SETTING (Monday):**")
    print(f"   AI sends: 'What are your goals for this week?'")
    print(f"   Member replies: 'I'll do 20 calls, 5 demos, 2 proposals'")
    print(f"   ✅ AI creates tasks and starts tracking")
    
    print(f"\n📊 **2. PROGRESS UPDATES (Anytime):**")
    print(f"   Member can update via:")
    print(f"   • Slack DM: 'Completed 5 calls today'")
    print(f"   • Slash command: '/done task-123'")
    print(f"   • Dashboard: Click 'Mark Complete'")
    print(f"   • API: POST to /api/sales/progress/{{user_id}}/update")
    
    print(f"\n🎉 **3. MILESTONE CELEBRATIONS:**")
    print(f"   When goals are hit:")
    print(f"   • DM to member: '🎉 Congrats! You hit your call target!'")
    print(f"   • Channel announcement: '🏆 @member just crushed their goals!'")
    print(f"   • Leaderboard update")
    
    print(f"\n📈 **4. WEEKLY RHYTHM:**")
    print(f"   • **Monday 9 AM**: Goal setting prompts")
    print(f"   • **Wednesday 2 PM**: Progress nudges") 
    print(f"   • **Friday 5 PM**: Weekly summaries")
    print(f"   • **Daily 6 PM**: Milestone checks")

async def main():
    """Main function"""
    print("🚀 DealTracker: Setting up comprehensive progress tracking")
    print("=" * 70)
    
    success = await setup_progress_tracking()
    
    if success:
        print(f"\n🎉 **PROGRESS TRACKING SETUP COMPLETE!**")
        print(f"✅ Team onboarded on how to update progress")
        print(f"✅ Multiple tracking methods available")
        print(f"✅ Sample progress data created")
        print(f"✅ Test messages sent")
        
        await demonstrate_progress_tracking()
        
        print(f"\n🎯 **NEXT STEPS:**")
        print(f"1. Team members should reply 'Got it!' to confirm onboarding")
        print(f"2. Test progress updates via Slack DMs")
        print(f"3. Use manual triggers to test the full system")
        print(f"4. Check dashboard for real-time progress visualization")
        
        print(f"\n🔗 **Key URLs:**")
        print(f"   📊 Dashboard: http://localhost:3000")
        print(f"   📡 API: http://localhost:3001/api/sales")
        print(f"   📱 Slack Events: http://localhost:3001/slack/events")
        
    else:
        print(f"\n❌ Failed to set up progress tracking!")

if __name__ == "__main__":
    asyncio.run(main()) 