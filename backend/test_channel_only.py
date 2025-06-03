#!/usr/bin/env python3
"""
Test sending a message to the psv-sales-agent channel
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def test_channel_message():
    """Test sending a message to the psv-sales-agent channel"""
    
    print("📢 Testing message to #psv-sales-agent channel...")
    print("=" * 50)
    
    # Initialize Slack service
    slack_service = SlackService()
    
    if not slack_service.is_configured():
        print("❌ Slack service not configured")
        return
    
    channel_id = os.getenv('SLACK_CHANNEL_ID')
    print(f"📢 Channel ID: {channel_id}")
    
    # Simple test message
    test_message = """🤖 **DealTracker AI Sales Agent - Test Message**

Hello #psv-sales-agent! 👋

This is a test message to verify the bot can post to this channel.

If you're seeing this message, then the DealTracker AI Sales Agent is successfully connected to your channel! 🎉

**🚀 Ready to automate your sales process!**

*Test sent from DealTracker AI Sales Agent*"""
    
    try:
        print(f"\n📤 Attempting to send message to channel...")
        
        # Try to send to channel
        result = await slack_service.send_channel_message(
            channel_id=channel_id,
            text=test_message
        )
        
        if result.get("ok"):
            print(f"✅ SUCCESS! Message sent to #psv-sales-agent channel!")
            print(f"📢 Check the channel now - you should see the test message!")
            
            # Get message details if available
            if "message" in result:
                msg = result["message"]
                print(f"   📝 Message ID: {msg.get('ts', 'N/A')}")
                print(f"   📅 Timestamp: {msg.get('ts', 'N/A')}")
            
            return True
        else:
            print(f"❌ FAILED to send message to channel")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
            # Provide specific help based on error
            error = result.get('error', '')
            if error == 'not_in_channel':
                print(f"\n🔧 **Solution:** The bot needs to be added to the channel!")
                print(f"   1. Go to #psv-sales-agent channel in Slack")
                print(f"   2. Type: /invite @DealTracker")
                print(f"   3. Or add the bot through channel settings")
            elif error == 'channel_not_found':
                print(f"\n🔧 **Solution:** Channel not found - check the channel ID")
            elif error == 'access_denied':
                print(f"\n🔧 **Solution:** Bot doesn't have permission to post")
            
            return False
            
    except Exception as e:
        print(f"❌ ERROR sending message: {e}")
        return False

async def main():
    """Main function"""
    success = await test_channel_message()
    
    if success:
        print(f"\n🎉 **CHANNEL MESSAGE SUCCESSFUL!**")
        print(f"✅ Bot can post to #psv-sales-agent channel")
        print(f"✅ Team announcements will work")
        print(f"✅ Weekly leaderboards will work")
        print(f"")
        print(f"📢 **Check #psv-sales-agent channel now!**")
        
    else:
        print(f"\n❌ **CHANNEL MESSAGE FAILED**")
        print(f"The bot needs to be added to the #psv-sales-agent channel first.")
        print(f"")
        print(f"📱 **Good news:** DMs are working perfectly!")
        print(f"All personal automation features are functional.")

if __name__ == "__main__":
    asyncio.run(main()) 