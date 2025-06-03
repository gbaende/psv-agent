#!/usr/bin/env python3
"""
Test Slack connection and send a test message
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def test_slack_connection():
    """Test Slack connection and send a message"""
    
    print("🔍 Testing Slack Connection...")
    print("=" * 50)
    
    # Check environment variables
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    print(f"SLACK_BOT_TOKEN: {'✅ Found' if bot_token else '❌ Not Found'}")
    if bot_token:
        print(f"Token starts with: {bot_token[:10]}...")
    
    # Initialize Slack service
    slack_service = SlackService()
    print(f"Slack service configured: {'✅ Yes' if slack_service.is_configured() else '❌ No'}")
    
    if not slack_service.is_configured():
        print("❌ Cannot proceed - Slack service not configured")
        return
    
    # Test sending a message to you (Gedeon)
    your_slack_id = "U08E2VCC1FB"
    test_message = """🧪 **Slack Connection Test**

This is a test message from DealTracker to verify the Slack integration is working!

If you're seeing this message, then:
✅ Slack bot token is valid
✅ Bot has permission to send DMs
✅ Your AI Sales Automation is ready to go!

🚀 DealTracker AI Sales Agent - Connection Test"""
    
    try:
        print(f"\n📤 Sending test message to Gedeon Baende ({your_slack_id})...")
        
        result = await slack_service.send_direct_message(
            user_id=your_slack_id,
            text=test_message
        )
        
        if result.get("ok"):
            print("✅ SUCCESS! Test message sent successfully!")
            print("📱 Check your Slack DMs - you should see the test message!")
            
            # Get message details
            if "message" in result:
                msg = result["message"]
                print(f"   📝 Message ID: {msg.get('ts', 'N/A')}")
                print(f"   📅 Timestamp: {msg.get('ts', 'N/A')}")
            
            return True
        else:
            print(f"❌ FAILED to send test message: {result}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR sending test message: {e}")
        return False

async def main():
    """Main function"""
    success = await test_slack_connection()
    
    if success:
        print(f"\n🎉 **SLACK CONNECTION SUCCESSFUL!**")
        print(f"✅ Your DealTracker AI Sales Automation is ready!")
        print(f"✅ Bot can send direct messages")
        print(f"✅ All team members will receive automation messages")
        
        print(f"\n📱 **Check Your Slack DMs Now!**")
        print(f"You should see:")
        print(f"• Test connection message (just sent)")
        print(f"• Welcome/onboarding message")
        print(f"• Monday goal-setting prompt")
        print(f"• Coaching tip example")
        print(f"• Milestone celebration example")
        
    else:
        print(f"\n❌ **SLACK CONNECTION FAILED!**")
        print(f"Please check:")
        print(f"• Slack bot token is correct")
        print(f"• Bot has permission to send DMs")
        print(f"• Bot is added to your workspace")

if __name__ == "__main__":
    asyncio.run(main()) 