#!/usr/bin/env python3
"""
Test script to check Slack integration and get workspace users
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def test_slack_connection():
    """Test Slack connection and get workspace info"""
    
    print("🔍 Testing Slack Integration...")
    print(f"Bot Token: {os.getenv('SLACK_BOT_TOKEN', 'Not found')[:20]}...")
    print(f"Channel ID: {os.getenv('SLACK_CHANNEL_ID', 'Not found')}")
    
    # Initialize Slack service
    slack_service = SlackService()
    
    if not slack_service.is_configured():
        print("❌ Slack service is not properly configured!")
        return
    
    print("✅ Slack service is configured!")
    
    try:
        # Test basic API call - get bot info
        print("\n📡 Testing API connection...")
        response = await slack_service.client.auth_test()
        if response["ok"]:
            print(f"✅ Connected as: {response['user']}")
            print(f"✅ Team: {response['team']}")
            print(f"✅ Bot ID: {response['bot_id']}")
        else:
            print(f"❌ Auth test failed: {response}")
            return
        
        # Get workspace users
        print("\n👥 Getting workspace users...")
        users_response = await slack_service.client.users_list()
        if users_response["ok"]:
            users = users_response["members"]
            print(f"✅ Found {len(users)} users in workspace:")
            
            # Filter for real users (not bots)
            real_users = []
            for user in users:
                if not user.get("is_bot", False) and not user.get("deleted", False):
                    real_users.append({
                        "id": user["id"],
                        "name": user.get("real_name", user.get("name", "Unknown")),
                        "display_name": user.get("profile", {}).get("display_name", ""),
                        "email": user.get("profile", {}).get("email", ""),
                        "is_admin": user.get("is_admin", False),
                        "is_owner": user.get("is_owner", False)
                    })
            
            print(f"\n📋 Real Users ({len(real_users)}):")
            for i, user in enumerate(real_users, 1):
                print(f"  {i}. {user['name']} ({user['id']})")
                if user['email']:
                    print(f"     Email: {user['email']}")
                if user['display_name']:
                    print(f"     Display: {user['display_name']}")
                print()
        
        # Get channel info if channel ID is provided
        channel_id = os.getenv('SLACK_CHANNEL_ID')
        if channel_id:
            print(f"\n📢 Getting channel info for {channel_id}...")
            try:
                channel_response = await slack_service.client.conversations_info(channel=channel_id)
                if channel_response["ok"]:
                    channel = channel_response["channel"]
                    print(f"✅ Channel: #{channel['name']}")
                    print(f"✅ Purpose: {channel.get('purpose', {}).get('value', 'No purpose set')}")
                    
                    # Get channel members
                    members_response = await slack_service.client.conversations_members(channel=channel_id)
                    if members_response["ok"]:
                        member_ids = members_response["members"]
                        print(f"✅ Channel has {len(member_ids)} members")
                        
                        # Match member IDs to user names
                        channel_users = []
                        for member_id in member_ids:
                            for user in real_users:
                                if user["id"] == member_id:
                                    channel_users.append(user)
                                    break
                        
                        print(f"\n👥 Channel Members:")
                        for user in channel_users:
                            print(f"  - {user['name']} ({user['id']})")
                    
                else:
                    print(f"❌ Failed to get channel info: {channel_response}")
            except Exception as e:
                print(f"❌ Error getting channel info: {e}")
        
        # Test sending a message to the channel
        if channel_id:
            print(f"\n💬 Testing message sending to channel...")
            test_message = "🤖 DealTracker Sales Agent Test - Slack integration is working!"
            
            try:
                message_response = await slack_service.send_message(channel_id, test_message)
                if message_response.get("ok"):
                    print("✅ Test message sent successfully!")
                    print(f"   Message TS: {message_response.get('ts')}")
                else:
                    print(f"❌ Failed to send message: {message_response}")
            except Exception as e:
                print(f"❌ Error sending message: {e}")
        
        return real_users
        
    except Exception as e:
        print(f"❌ Error testing Slack: {e}")
        return None

async def main():
    """Main test function"""
    users = await test_slack_connection()
    
    if users:
        print(f"\n🎯 Summary:")
        print(f"✅ Slack integration is working!")
        print(f"✅ Found {len(users)} real users in workspace")
        print(f"✅ Ready to send sales automation messages!")
        
        print(f"\n💡 Next Steps:")
        print(f"1. Update your database users with Slack IDs")
        print(f"2. Test sending direct messages to specific users")
        print(f"3. Run the Monday prompts with real Slack integration!")
    else:
        print(f"\n❌ Slack integration test failed!")

if __name__ == "__main__":
    asyncio.run(main()) 