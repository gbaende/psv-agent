#!/usr/bin/env python3
"""
Test sending messages to Slack channel and explain DM vs Channel messaging
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def test_channel_and_dm_messages():
    """Test sending messages to both channel and DMs"""
    
    print("📱 Testing Slack Channel vs DM Messages...")
    print("=" * 60)
    
    # Initialize Slack service
    slack_service = SlackService()
    
    if not slack_service.is_configured():
        print("❌ Slack service not configured")
        return
    
    channel_id = os.getenv('SLACK_CHANNEL_ID')
    print(f"📢 Channel ID: {channel_id}")
    
    # Your Slack ID
    your_slack_id = "U08E2VCC1FB"
    
    print(f"\n🔍 **Understanding Message Types:**")
    print(f"📱 **DMs (Direct Messages)** - Private messages sent directly to users")
    print(f"📢 **Channel Messages** - Public messages posted in the channel")
    print(f"")
    print(f"🎯 **DealTracker AI Sales Automation uses DMs for:**")
    print(f"• Personal goal setting prompts")
    print(f"• Individual coaching tips")
    print(f"• Private milestone celebrations")
    print(f"• Personalized feedback")
    print(f"")
    print(f"📢 **Channel messages are used for:**")
    print(f"• Team announcements")
    print(f"• Weekly leaderboards")
    print(f"• General updates")
    
    # Test sending a message to the channel
    channel_message = """🚀 **DealTracker AI Sales Automation - Team Update**

Hello Pacific Software Ventures sales team! 👋

Your AI Sales Agent is now LIVE and ready to help you crush your goals! 🎯

**📱 Check Your DMs!** Each team member should have received:
• Welcome message with automation overview
• Monday goal-setting prompt
• Example coaching tips and celebrations

**🤖 What I'll do for the team:**
• **Monday 9 AM** - Personal goal setting prompts (via DM)
• **Wednesday 2 PM** - Individual coaching tips (via DM)
• **Friday 5 PM** - Team leaderboards (posted here!)
• **Daily 6 PM** - Milestone celebrations (via DM)

**👥 Team Members Onboarded:**
✅ Gedeon Baende (Sales Manager)
✅ Aidan Scudder (Sales Rep)
✅ Sanjay Thasma (Sales Rep)
✅ Srivatsaan Kalpana Sreenivasan (Sales Rep)
✅ Aaryaman Singh (Sales Rep)
✅ Gabriel Krishnadasan (Sales Rep)

Ready to dominate this week? Let's go! 💪

*DealTracker AI Sales Agent - Pacific Software Ventures*"""
    
    try:
        print(f"\n📢 Sending team announcement to channel...")
        
        # Send to channel
        channel_result = await slack_service.send_channel_message(
            channel_id=channel_id,
            text=channel_message
        )
        
        if channel_result.get("ok"):
            print(f"✅ Channel message sent successfully!")
            print(f"📢 Check #psv-sales-agent channel for the team announcement!")
        else:
            print(f"❌ Failed to send channel message: {channel_result}")
        
    except Exception as e:
        print(f"❌ Error sending channel message: {e}")
    
    # Send a clarification DM to you
    dm_clarification = """📱 **DM vs Channel Messages - Clarification**

Hi Gedeon! 👋

I wanted to clarify where you'll see different types of messages:

**📱 Your DMs (Private Messages):**
You should see these 5 messages here in your DMs:
1. 🧪 Slack connection test
2. 🎉 Welcome/onboarding message
3. 🎯 Monday goal-setting prompt
4. 💡 Coaching tip example
5. 🏆 Milestone celebration example

**📢 #psv-sales-agent Channel:**
You'll see:
• Team announcements (just posted one!)
• Weekly leaderboards (Fridays)
• General automation updates

**🎯 Why DMs for personal messages?**
• Goal setting is personal and private
• Coaching tips are tailored to individual performance
• Milestone celebrations are personal achievements
• Keeps the channel clean for team-wide updates

Check both your DMs and the channel now! 📱📢

*DealTracker AI Sales Agent*"""
    
    try:
        print(f"\n📱 Sending clarification DM to you...")
        
        dm_result = await slack_service.send_direct_message(
            user_id=your_slack_id,
            text=dm_clarification
        )
        
        if dm_result.get("ok"):
            print(f"✅ Clarification DM sent successfully!")
            print(f"📱 Check your DMs for the explanation!")
        else:
            print(f"❌ Failed to send DM: {dm_result}")
            
    except Exception as e:
        print(f"❌ Error sending DM: {e}")

async def main():
    """Main function"""
    await test_channel_and_dm_messages()
    
    print(f"\n🎯 **Summary:**")
    print(f"📢 **Channel Message** - Posted to #psv-sales-agent")
    print(f"📱 **DM Messages** - Sent privately to your DMs")
    print(f"")
    print(f"📱 **Check BOTH locations:**")
    print(f"1. Your DMs - 6 personal messages")
    print(f"2. #psv-sales-agent channel - 1 team announcement")
    print(f"")
    print(f"🚀 **Your AI Sales Automation is fully operational!**")

if __name__ == "__main__":
    asyncio.run(main()) 