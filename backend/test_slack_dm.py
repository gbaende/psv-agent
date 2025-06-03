#!/usr/bin/env python3
"""
Test sending direct messages to real Slack users
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def test_direct_messages():
    """Test sending direct messages to real users"""
    
    # Real users from your workspace
    test_users = [
        {
            "name": "Gedeon Baende",
            "slack_id": "U08E2VCC1FB",
            "email": "gedeon@pacificsoftwareventures.com"
        },
        {
            "name": "Aidan Scudder", 
            "slack_id": "U06T93G62E5",
            "email": "aidan@pacificsoftwareventures.com"
        },
        {
            "name": "Sanjay Thasma",
            "slack_id": "U06TAA2A73K", 
            "email": "thasma@wisc.edu"
        }
    ]
    
    print("💬 Testing Direct Messages to Real Users...")
    
    # Initialize Slack service
    slack_service = SlackService()
    
    if not slack_service.is_configured():
        print("❌ Slack service is not properly configured!")
        return
    
    print("✅ Slack service is configured!")
    
    # Test sending Monday goal prompts
    for user in test_users:
        print(f"\n📤 Sending Monday goal prompt to {user['name']}...")
        
        # Create a realistic Monday prompt message
        monday_prompt = f"""🎯 **Good Monday Morning, {user['name'].split()[0]}!**

Ready to crush this week? Let's set your sales targets:

📞 **Discovery Calls** - How many new prospects will you reach out to?
🎬 **Demos/Presentations** - How many product demos will you deliver?
📋 **Proposals** - How many proposals will you submit?

**Example:** "I'll do 15 calls, 4 demos, and 2 proposals this week"

Just reply with your numbers and let's make this week count! 💪

*This is an automated message from the DealTracker Sales Agent*"""
        
        try:
            # Send the direct message
            result = await slack_service.send_direct_message(
                user_id=user['slack_id'],
                text=monday_prompt
            )
            
            if result.get("ok"):
                print(f"✅ Successfully sent Monday prompt to {user['name']}")
                print(f"   Message timestamp: {result.get('ts')}")
            else:
                print(f"❌ Failed to send message to {user['name']}: {result}")
                
        except Exception as e:
            print(f"❌ Error sending message to {user['name']}: {e}")
    
    # Test sending a coaching tip
    print(f"\n💡 Testing coaching tip message...")
    
    coaching_tip = f"""💡 **Mid-Week Coaching Tip**

Hey team! Here's a quick tip to boost your performance:

**🎯 Quality over Quantity**
Instead of making 20 rushed calls, focus on 10 well-researched, personalized conversations. 

**📊 This Week's Focus:**
- Research prospects for 2-3 minutes before calling
- Ask open-ended discovery questions
- Listen more than you talk

Keep up the great work! 🚀

*DealTracker Sales Agent*"""
    
    # Send to first user as test
    test_user = test_users[0]
    try:
        result = await slack_service.send_direct_message(
            user_id=test_user['slack_id'],
            text=coaching_tip
        )
        
        if result.get("ok"):
            print(f"✅ Successfully sent coaching tip to {test_user['name']}")
        else:
            print(f"❌ Failed to send coaching tip: {result}")
            
    except Exception as e:
        print(f"❌ Error sending coaching tip: {e}")
    
    # Test milestone celebration
    print(f"\n🎉 Testing milestone celebration...")
    
    celebration = f"""🎉 **MILESTONE ACHIEVED!** 🎉

Congratulations {test_user['name'].split()[0]}! 

🎯 **You just hit your weekly call target!**
📞 20/20 calls completed - that's 100%!

Your dedication and hard work are paying off. Keep this momentum going!

The whole team is cheering for you! 👏

*DealTracker Sales Agent*"""
    
    try:
        result = await slack_service.send_direct_message(
            user_id=test_user['slack_id'],
            text=celebration
        )
        
        if result.get("ok"):
            print(f"✅ Successfully sent celebration to {test_user['name']}")
        else:
            print(f"❌ Failed to send celebration: {result}")
            
    except Exception as e:
        print(f"❌ Error sending celebration: {e}")
    
    print(f"\n🎯 **Direct Message Test Complete!**")
    print(f"✅ Check your Slack DMs to see the messages!")
    print(f"✅ The sales automation is now ready to send real messages!")

if __name__ == "__main__":
    asyncio.run(test_direct_messages()) 