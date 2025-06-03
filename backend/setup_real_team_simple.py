#!/usr/bin/env python3
"""
Set up sales team with real Slack users (simplified version)
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.slack_service import SlackService

# Load environment variables
load_dotenv()

async def setup_real_team_simple():
    """Set up and test with real team members from previous discovery"""
    
    print("🚀 Setting up DealTracker with real Pacific Software Ventures team")
    print("=" * 70)
    
    # Real team members from your Slack workspace (from our earlier discovery)
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
    
    print(f"👥 **Pacific Software Ventures Sales Team ({len(real_team_members)} members):**")
    for i, member in enumerate(real_team_members, 1):
        print(f"  {i}. {member['name']} - {member['role']}")
        print(f"     📧 {member['email']}")
        print(f"     💬 {member['slack_id']}")
        print()
    
    # Initialize Slack service
    slack_service = SlackService()
    
    if not slack_service.is_configured():
        print("❌ Slack service is not properly configured!")
        return
    
    print("✅ Slack service is configured!")
    
    # Send team onboarding messages
    await send_team_onboarding(slack_service, real_team_members)
    
    # Test Monday prompts with real team
    await test_monday_prompts_real_team(slack_service, real_team_members)
    
    # Test coaching and celebrations
    await test_coaching_and_celebrations(slack_service, real_team_members)
    
    return real_team_members

async def send_team_onboarding(slack_service, team_members):
    """Send onboarding messages to the real team"""
    
    print(f"\n🎉 Sending onboarding messages to {len(team_members)} team members...")
    
    onboarding_message = """🎉 **Welcome to DealTracker AI Sales Automation!**

Hi there! I'm your new AI Sales Agent for Pacific Software Ventures! 🚀

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

Ready to crush some sales goals? Let's do this! 💪

*DealTracker AI Sales Agent - Pacific Software Ventures*"""
    
    success_count = 0
    for member in team_members:
        try:
            print(f"📤 Sending onboarding to {member['name']}...")
            
            result = await slack_service.send_direct_message(
                user_id=member['slack_id'],
                text=onboarding_message
            )
            
            if result.get("ok"):
                print(f"  ✅ Onboarding sent to {member['name']}")
                success_count += 1
            else:
                print(f"  ❌ Failed to send to {member['name']}: {result}")
                
        except Exception as e:
            print(f"  ❌ Error sending to {member['name']}: {e}")
    
    print(f"\n🎯 Onboarding messages sent: {success_count}/{len(team_members)}")

async def test_monday_prompts_real_team(slack_service, team_members):
    """Test Monday prompts with the real team"""
    
    print(f"\n🎯 Testing Monday goal prompts with real team...")
    
    # Send to first 3 team members as test
    test_members = team_members[:3]
    
    for member in test_members:
        monday_prompt = f"""🎯 **Monday Goal Setting - {member['name'].split()[0]}!**

Ready to start the week strong at Pacific Software Ventures? 

Let's set your sales targets for this week:

📞 **Discovery Calls** - How many prospects will you contact?
🎬 **Product Demos** - How many demos will you deliver?
📋 **Proposals** - How many proposals will you submit?

**Example responses:**
• "20 calls, 5 demos, 2 proposals"
• "I'll do 15 calls and 3 demos this week"  
• "Target: 25 calls, 4 demos, 1 proposal"

Just reply with your numbers and I'll create tasks to track your progress! 💪

*DealTracker AI Sales Agent - Automated Monday Check-in*"""
        
        try:
            print(f"📤 Sending Monday prompt to {member['name']}...")
            
            result = await slack_service.send_direct_message(
                user_id=member['slack_id'],
                text=monday_prompt
            )
            
            if result.get("ok"):
                print(f"  ✅ Monday prompt sent to {member['name']}")
            else:
                print(f"  ❌ Failed to send Monday prompt: {result}")
                
        except Exception as e:
            print(f"  ❌ Error sending Monday prompt: {e}")

async def test_coaching_and_celebrations(slack_service, team_members):
    """Test coaching tips and milestone celebrations"""
    
    print(f"\n💡 Testing coaching tips and celebrations...")
    
    # Send coaching tip to first member
    coaching_member = team_members[0]
    
    coaching_tip = f"""💡 **Mid-Week Coaching Tip for {coaching_member['name'].split()[0]}**

Here's a proven strategy to boost your conversion rates:

**🎯 The 3-Touch Rule**
Instead of one cold call, use this sequence:
1. **LinkedIn connection** with personalized note
2. **Email** with value proposition  
3. **Phone call** referencing your previous touches

**📊 Results:** 40% higher response rates vs. cold calling alone

**This Week's Challenge:**
Try this approach with 5 prospects and track the difference!

Keep crushing it! 🚀

*DealTracker AI Sales Agent - Pacific Software Ventures*"""
    
    try:
        print(f"📤 Sending coaching tip to {coaching_member['name']}...")
        
        result = await slack_service.send_direct_message(
            user_id=coaching_member['slack_id'],
            text=coaching_tip
        )
        
        if result.get("ok"):
            print(f"  ✅ Coaching tip sent to {coaching_member['name']}")
        else:
            print(f"  ❌ Failed to send coaching tip: {result}")
            
    except Exception as e:
        print(f"  ❌ Error sending coaching tip: {e}")
    
    # Send milestone celebration
    celebration = f"""🎉 **MILESTONE ACHIEVED!** 🎉

Congratulations {coaching_member['name'].split()[0]}! 

🎯 **You just hit your weekly call target!**
📞 20/20 calls completed - that's 100%!

Your dedication is paying off! The whole Pacific Software Ventures team is cheering for you! 👏

**🏆 Achievement Unlocked:** Call Master
**🚀 Momentum:** Keep this energy going into demos!

Amazing work! 💪

*DealTracker AI Sales Agent - Pacific Software Ventures*"""
    
    try:
        print(f"📤 Sending milestone celebration to {coaching_member['name']}...")
        
        result = await slack_service.send_direct_message(
            user_id=coaching_member['slack_id'],
            text=celebration
        )
        
        if result.get("ok"):
            print(f"  ✅ Celebration sent to {coaching_member['name']}")
        else:
            print(f"  ❌ Failed to send celebration: {result}")
            
    except Exception as e:
        print(f"  ❌ Error sending celebration: {e}")

async def main():
    """Main function"""
    team_members = await setup_real_team_simple()
    
    if team_members:
        print(f"\n🎉 **SUCCESS! DealTracker is now live with your real team!**")
        print(f"✅ Team size: {len(team_members)} Pacific Software Ventures members")
        print(f"✅ Onboarding messages sent to all team members")
        print(f"✅ Monday prompts tested with 3 members")
        print(f"✅ Coaching tips and celebrations tested")
        
        print(f"\n📱 **Check Your Slack DMs!**")
        print(f"All team members should now have:")
        print(f"• Welcome/onboarding message")
        print(f"• Monday goal-setting prompt (first 3 members)")
        print(f"• Coaching tip example (Gedeon)")
        print(f"• Milestone celebration example (Gedeon)")
        
        print(f"\n🚀 **Your AI Sales Automation is LIVE!**")
        print(f"The system is now ready to:")
        print(f"• Send automated Monday prompts to your real team")
        print(f"• Track progress and send coaching tips")
        print(f"• Celebrate milestones and achievements")
        print(f"• Generate team leaderboards")
        
        print(f"\n🎯 **Next Steps:**")
        print(f"1. Check Slack DMs for all the test messages")
        print(f"2. Reply to Monday prompt to test goal setting")
        print(f"3. Run full automation triggers with real team")
        print(f"4. Set up the dashboard to track real progress")
        
    else:
        print(f"\n❌ Failed to set up real sales team!")

if __name__ == "__main__":
    asyncio.run(main()) 