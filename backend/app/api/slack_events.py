from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from datetime import datetime, date
from typing import Dict, Any
import logging

from app.database import get_db
from app.services.sales_agent import SalesAgentService
from app.services.slack_service import SlackService
from app.services.ai_service import ai_service
from app.models import User, SalesConversation
from app.services.auto_sync_users import auto_sync_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/slack", tags=["slack"])


class SlackEventRouter:
    """Routes Slack events to appropriate sales agent handlers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.sales_agent = SalesAgentService(db)
        self.slack_service = SlackService()
    
    def is_reply_to_weekly_prompt(self, user_id: str, text: str, thread_ts: str = None) -> bool:
        """Check if this is a reply to Monday's goal-setting prompt"""
        try:
            # Look for an active conversation for this week
            week_start = self.sales_agent.get_current_week_start()
            conversation = self.db.query(SalesConversation).filter(
                SalesConversation.user_slack_id == user_id,
                SalesConversation.week_start == week_start,
                SalesConversation.conversation_type == "weekly_goals"
            ).first()
            
            return conversation is not None
        except Exception as e:
            logger.error(f"Error checking weekly prompt reply: {e}")
            return False
    
    def is_midweek_update(self, user_id: str, text: str) -> bool:
        """Check if this is a mid-week progress update"""
        update_keywords = ["progress", "update", "completed", "done", "finished", "status"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in update_keywords)
    
    def contains_query_intent(self, text: str) -> bool:
        """Check if the message is asking for information"""
        query_keywords = ["how am i", "progress", "status", "leaderboard", "standing", "summary"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in query_keywords)
    
    def parse_sales_progress_update(self, text: str) -> Dict:
        """Parse progress updates from text"""
        # Simple pattern matching for "completed X calls" etc.
        import re
        
        progress = {"calls": 0, "demos": 0, "proposals": 0}
        
        # Look for patterns like "completed 5 calls", "did 3 demos", etc.
        calls_match = re.search(r'(\d+)\s*(call|calls)', text.lower())
        demos_match = re.search(r'(\d+)\s*(demo|demos|presentation)', text.lower())
        proposals_match = re.search(r'(\d+)\s*(proposal|proposals)', text.lower())
        
        if calls_match:
            progress["calls"] = int(calls_match.group(1))
        if demos_match:
            progress["demos"] = int(demos_match.group(1))
        if proposals_match:
            progress["proposals"] = int(proposals_match.group(1))
        
        return progress
    
    def update_weekly_goals_progress(self, user_id: str, week_start: date, progress: Dict):
        """Update weekly goals with progress"""
        # This would update the actual progress in the database
        # For now, we'll just acknowledge the update
        pass
    
    def generate_individual_summary(self, user_id: str, week_start: date) -> str:
        """Generate individual progress summary"""
        try:
            # Get user from Slack ID
            user = self.db.query(User).filter(User.slack_user_id == user_id).first()
            if not user:
                return "Sorry, I couldn't find your user profile."
            
            progress = self.sales_agent.get_weekly_progress(user.id, week_start)
            
            summary = f"""📊 **Your Week Progress Summary**
            
**Current Status:**
📞 Calls: {progress['calls_completed']}/{progress['calls_target']} ({progress['calls_percentage']}%)
🎬 Demos: {progress['demos_completed']}/{progress['demos_target']} ({progress['demos_percentage']}%)
📋 Proposals: {progress['proposals_completed']}/{progress['proposals_target']} ({progress['proposals_percentage']}%)

**Overall: {progress['overall_percentage']}% complete**

{self.sales_agent.generate_coaching_tips(user.id, progress)}

Keep pushing! 💪"""
            
            return summary
        except Exception as e:
            logger.error(f"Error generating individual summary: {e}")
            return "I'm having trouble generating your summary right now. Please try again later."
    
    def project_manager_llm(self, text: str, user_id: str) -> str:
        """Use AI service for general sales-related conversations"""
        try:
            # Get user context
            user = self.db.query(User).filter(User.slack_user_id == user_id).first()
            user_name = user.name if user else "there"
            
            # Create a context-aware system message
            system_message = f"""You are SalesPM, an AI sales project manager for Pacific Software Ventures. 
            You're chatting with {user_name}, a sales representative. 
            
            Your role is to:
            - Help with sales strategy and tactics
            - Provide motivation and coaching
            - Answer questions about sales processes
            - Track and discuss progress toward goals
            - Offer practical sales advice
            
            Keep responses friendly, professional, and focused on helping them succeed in sales.
            Use emojis appropriately and keep responses concise but helpful."""
            
            try:
                # Use the AI service for a more intelligent response
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(ai_service.generate_response(text, system_message))
                loop.close()
                return response
            except Exception as e:
                logger.error(f"Error generating AI response: {e}")
                # Fallback response
                return f"Hi {user_name}! I'm your SalesPM assistant. I can help you with sales goals, progress tracking, and general sales questions. What would you like to know about?"
        except Exception as e:
            logger.error(f"Error in project_manager_llm: {e}")
            return "Hi there! I'm your SalesPM assistant. I can help you with sales goals, progress tracking, and general sales questions. What would you like to know about?"

    async def auto_onboard_new_user(self, user_id: str) -> bool:
        """Automatically onboard a new user when they join the channel"""
        try:
            # Check if user already exists in database
            existing_user = self.db.query(User).filter(User.slack_user_id == user_id).first()
            if existing_user:
                return False  # User already exists
            
            # Get user info from Slack
            user_response = await self.slack_service.client.users_info(user=user_id)
            if not user_response["ok"]:
                print(f"Failed to get user info for {user_id}")
                return False
            
            user_data = user_response["user"]
            
            # Skip bots
            if user_data.get("is_bot", False) or user_data.get("deleted", False):
                return False
            
            # Create new user in database
            new_user = User(
                name=user_data.get("real_name", user_data.get("name", "Unknown")),
                email=user_data.get("profile", {}).get("email", f"{user_data['name']}@example.com"),
                slack_user_id=user_id,
                role="sales"
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            # Send welcome message
            await self.send_welcome_message(user_id, new_user.name)
            
            print(f"✅ Auto-onboarded new user: {new_user.name} ({user_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error auto-onboarding user {user_id}: {e}")
            return False
    
    async def send_welcome_message(self, user_id: str, user_name: str):
        """Send welcome message to newly onboarded user"""
        welcome_message = f"""🎉 **Welcome to DealTracker, {user_name}!**

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
You now have access to the sales dashboard at: http://35.175.231.57

Ready to crush some sales goals? Let's do this! 💪

*DealTracker AI Sales Agent - Auto-Onboarded*"""
        
        await self.slack_service.send_direct_message(user_id, welcome_message)


@router.post("/events")
async def handle_slack_events(request: Request, db: Session = Depends(get_db)):
    """Main Slack event handler - routes all sales interactions through autonomous agent"""
    try:
        payload = await request.json()
        
        # Handle URL verification for Slack app setup
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}
        
        # Handle actual events
        if payload.get("type") == "event_callback":
            event = payload["event"]
            event_type = event.get("type")
            
            # Handle member joining channel - AUTO-SYNC NEW USERS
            if event_type == "member_joined_channel":
                user_id = event["user"]
                channel_id = event["channel"]
                
                # Only auto-sync for our sales channel
                if channel_id == "C08UNPU9AGN":  # #psv-sales-agent channel
                    logger.info(f"🆕 New member joined #psv-sales-agent: {user_id}")
                    
                    # Auto-sync the new user
                    sync_result = await auto_sync_service.sync_single_user(user_id)
                    
                    if sync_result["success"]:
                        user_info = sync_result["user"]
                        action = sync_result["action"]
                        
                        if action == "created":
                            # Send team announcement for new users
                            slack_service = SlackService()
                            team_message = f"🎉 Welcome <@{user_id}> to the PSV Sales Team! They've been automatically added to DealTracker. 🚀\n\n📊 View the team dashboard: http://35.175.231.57"
                            await slack_service.send_message(channel_id, team_message)
                            
                            logger.info(f"✅ Auto-onboarded new user: {user_info['name']}")
                            return {"status": "user_auto_onboarded", "user": user_info}
                        else:
                            logger.info(f"✅ Updated existing user: {user_info['name']}")
                            return {"status": "user_updated", "user": user_info}
                    else:
                        logger.error(f"❌ Failed to auto-sync user {user_id}: {sync_result.get('error')}")
                        return {"status": "sync_failed", "error": sync_result.get("error")}
                    
                return {"status": "member_joined_other_channel"}
            
            # Handle direct messages
            elif event_type == "message" and event.get("channel_type") == "im":
                user_id = event["user"]
                text = event.get("text", "")
                channel_id = event["channel"]
                thread_ts = event.get("thread_ts")
                
                # Skip bot messages
                if event.get("bot_id"):
                    return {"status": "ignored"}
                
                # Initialize event router
                event_router = SlackEventRouter(db)
                
                # Auto-onboard user if they don't exist (for DMs from new users)
                user = db.query(User).filter(User.slack_user_id == user_id).first()
                if not user:
                    await event_router.auto_onboard_new_user(user_id)
                
                # Route based on intent
                
                # 1. Reply to weekly goal prompt
                if event_router.is_reply_to_weekly_prompt(user_id, text, thread_ts):
                    return await handle_weekly_goal_response(event_router, user_id, text, channel_id, db)
                
                # 2. Mid-week progress update
                elif event_router.is_midweek_update(user_id, text):
                    return await handle_progress_update(event_router, user_id, text, channel_id, db)
                
                # 3. Query for status/progress
                elif event_router.contains_query_intent(text):
                    return await handle_progress_query(event_router, user_id, text, channel_id, db)
                
                # 4. Fallback to general project manager
                else:
                    return await handle_general_query(event_router, user_id, text, channel_id)
        
        return {"status": "ok"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error handling Slack event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_weekly_goal_response(event_router: SlackEventRouter, 
                                    user_id: str, text: str, channel_id: str, db: Session):
    """Handle response to Monday's goal-setting prompt"""
    try:
        # Get user from Slack ID
        user = db.query(User).filter(User.slack_user_id == user_id).first()
        if not user:
            await event_router.slack_service.send_message(channel_id, 
                "Sorry, I couldn't find your user profile. Please contact your manager.")
            return {"status": "error"}
        
        # Parse the goals from the response
        goals = event_router.sales_agent.parse_sales_response(text)
        
        # Create weekly tasks
        week_start = event_router.sales_agent.get_current_week_start()
        num_tasks = event_router.sales_agent.create_weekly_sales_tasks(user.id, week_start, goals)
        
        # Create conversation record
        conversation = SalesConversation(
            user_slack_id=user_id,
            week_start=week_start,
            conversation_type="weekly_goals",
            goals_data=json.dumps(goals),
            created_at=datetime.now()
        )
        db.add(conversation)
        db.commit()
        
        # Send confirmation
        confirmation = f"""🎯 **Goals Set for Week {week_start.strftime('%b %d')}!**

📞 **Calls:** {goals['calls_target']}
🎬 **Demos:** {goals['demos_target']} 
📋 **Proposals:** {goals['proposals_target']}

I've created {num_tasks} tasks for you this week. You can track them on the dashboard or mark them complete here using `/done [task-id]`.

Let's crush these goals! I'll check in with you Wednesday. 💪"""
        
        await event_router.slack_service.send_message(channel_id, confirmation)
        return {"status": "goals_recorded"}
        
    except Exception as e:
        await event_router.slack_service.send_message(channel_id, 
            f"Sorry, I had trouble processing your goals. Please try again or contact your manager. Error: {str(e)}")
        return {"status": "error"}


async def handle_progress_update(event_router: SlackEventRouter,
                               user_id: str, text: str, channel_id: str, db: Session):
    """Handle mid-week progress updates"""
    try:
        # Get user from Slack ID  
        user = db.query(User).filter(User.slack_user_id == user_id).first()
        if not user:
            await event_router.slack_service.send_message(channel_id,
                "Sorry, I couldn't find your user profile.")
            return {"status": "error"}
        
        # Parse progress from text
        progress_update = event_router.parse_sales_progress_update(text)
        
        # Get current progress
        week_start = event_router.sales_agent.get_current_week_start()
        current_progress = event_router.sales_agent.get_weekly_progress(user.id, week_start)
        
        # Generate coaching response
        coaching_tips = event_router.sales_agent.generate_coaching_tips(user.id, current_progress)
        
        response = f"""Thanks for the update! 📊

**Your current progress:**
📞 Calls: {current_progress['calls_completed']}/{current_progress['calls_target']} ({current_progress['calls_percentage']}%)
🎬 Demos: {current_progress['demos_completed']}/{current_progress['demos_target']} ({current_progress['demos_percentage']}%)
📋 Proposals: {current_progress['proposals_completed']}/{current_progress['proposals_target']} ({current_progress['proposals_percentage']}%)

{coaching_tips}

Keep it up! 🚀"""
        
        await event_router.slack_service.send_message(channel_id, response)
        return {"status": "progress_updated"}
        
    except Exception as e:
        await event_router.slack_service.send_message(channel_id,
            f"Sorry, I had trouble processing your update. Error: {str(e)}")
        return {"status": "error"}


async def handle_progress_query(event_router: SlackEventRouter,
                              user_id: str, text: str, channel_id: str, db: Session):
    """Handle queries about progress/status"""
    try:
        week_start = event_router.sales_agent.get_current_week_start()
        
        if "leaderboard" in text.lower():
            # Generate leaderboard
            leaderboard = event_router.sales_agent.get_team_leaderboard(week_start)
            
            leaderboard_text = "🏆 **Weekly Leaderboard** 🏆\n\n"
            for i, entry in enumerate(leaderboard[:5]):  # Top 5
                medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                leaderboard_text += f"{medal} {entry['name']}: {entry['overall_pct']}% overall\n"
            
            await event_router.slack_service.send_message(channel_id, leaderboard_text)
        else:
            # Generate individual summary
            summary = event_router.generate_individual_summary(user_id, week_start)
            await event_router.slack_service.send_message(channel_id, summary)
        
        return {"status": "query_handled"}
        
    except Exception as e:
        await event_router.slack_service.send_message(channel_id,
            f"Sorry, I couldn't retrieve your progress. Error: {str(e)}")
        return {"status": "error"}


async def handle_general_query(event_router: SlackEventRouter,
                             user_id: str, text: str, channel_id: str):
    """Handle general/fallback queries using AI"""
    try:
        # Get user context
        user = event_router.db.query(User).filter(User.slack_user_id == user_id).first()
        user_name = user.name if user else "there"
        
        # Enhanced system message for better conversation
        system_message = f"""You are SalesPM, an AI sales project manager for Pacific Software Ventures. 
        You're chatting with {user_name}, a sales representative.
        
        Your role is to:
        - Help with sales strategy, tactics, and best practices
        - Provide motivation, coaching, and encouragement
        - Answer questions about sales processes and techniques
        - Discuss progress, goals, and performance
        - Offer practical, actionable sales advice
        - Help with objection handling, prospecting, and closing techniques
        
        Keep responses:
        - Friendly and professional
        - Focused on sales success
        - Concise but comprehensive (2-3 sentences typically)
        - Include relevant emojis
        - Actionable and practical
        
        If they ask about technical features or non-sales topics, gently redirect to sales-related aspects."""
        
        # Use AI service for intelligent response
        response = await ai_service.generate_response(text, system_message)
        
        await event_router.slack_service.send_message(channel_id, response)
        return {"status": "general_handled"}
        
    except Exception as e:
        logger.error(f"Error in general query handler: {e}")
        fallback_response = f"Hi there! 👋 I'm your SalesPM assistant. I can help you with sales goals, progress tracking, coaching tips, and general sales questions. What would you like to know about?"
        await event_router.slack_service.send_message(channel_id, fallback_response)
        return {"status": "error"}


@router.post("/commands")
async def handle_slash_commands(request: Request, db: Session = Depends(get_db)):
    """Handle Slack slash commands like /done, /progress"""
    try:
        form = await request.form()
        command = form.get("command")
        text = form.get("text", "")
        user_id = form.get("user_id")
        response_url = form.get("response_url")
        
        # Get user from Slack ID
        user = db.query(User).filter(User.slack_user_id == user_id).first()
        if not user:
            return {"text": "Sorry, I couldn't find your user profile."}
        
        sales_agent = SalesAgentService(db)
        
        if command == "/done":
            # Mark task as complete
            result = sales_agent.mark_task_complete(user.id, text.strip())
            return {"text": result["message"]}
        
        elif command == "/progress":
            # Get current progress
            week_start = sales_agent.get_current_week_start()
            progress = sales_agent.get_weekly_progress(user.id, week_start)
            
            progress_text = f"""📊 **Your Sales Progress for Week {week_start.strftime('%b %d')}**

📞 **Discovery Calls:** {progress['calls_completed']}/{progress['calls_target']} ({progress['calls_percentage']}%)
🎬 **Demos:** {progress['demos_completed']}/{progress['demos_target']} ({progress['demos_percentage']}%)
📋 **Proposals:** {progress['proposals_completed']}/{progress['proposals_target']} ({progress['proposals_percentage']}%)

**Overall Progress:** {progress['overall_percentage']}%

{sales_agent.generate_coaching_tips(user.id, progress)}"""
            
            return {"text": progress_text}
        
        elif command == "/leaderboard":
            # Show team leaderboard
            week_start = sales_agent.get_current_week_start()
            leaderboard = sales_agent.get_team_leaderboard(week_start)
            
            leaderboard_text = f"🏆 **Team Leaderboard - Week {week_start.strftime('%b %d')}** 🏆\n\n"
            for i, entry in enumerate(leaderboard[:10]):
                rank_emoji = ["🥇", "🥈", "🥉"] + [f"{i+1}️⃣" for i in range(3, 10)]
                leaderboard_text += f"{rank_emoji[i] if i < len(rank_emoji) else f'{i+1}.'} {entry['name']}: {entry['overall_pct']}%\n"
            
            return {"text": leaderboard_text}
        
        else:
            return {"text": f"Unknown command: {command}"}
        
    except Exception as e:
        return {"text": f"Error processing command: {str(e)}"}


# Additional endpoint for manual agent actions (for testing/admin)
@router.post("/agent/send-monday-prompts")
async def send_monday_prompts(db: Session = Depends(get_db)):
    """Manually trigger Monday goal prompts for all sales reps"""
    try:
        sales_agent = SalesAgentService(db)
        
        # Get all sales users
        sales_users = db.query(User).filter(User.role == "sales").all()
        
        results = []
        for user in sales_users:
            success = sales_agent.send_monday_goal_prompt(user.id)
            results.append({"user_id": user.id, "name": user.name, "success": success})
        
        return {"message": f"Monday prompts sent to {len(sales_users)} sales reps", "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/send-midweek-nudges")
async def send_midweek_nudges(db: Session = Depends(get_db)):
    """Manually trigger Wednesday nudges for all sales reps"""
    try:
        sales_agent = SalesAgentService(db)
        
        sales_users = db.query(User).filter(User.role == "sales").all()
        
        results = []
        for user in sales_users:
            success = sales_agent.send_midweek_nudge(user.id)
            results.append({"user_id": user.id, "name": user.name, "success": success})
        
        return {"message": f"Midweek nudges sent to {len(sales_users)} sales reps", "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/send-weekly-summaries")
async def send_weekly_summaries(db: Session = Depends(get_db)):
    """Manually trigger Friday summaries for all sales reps"""
    try:
        sales_agent = SalesAgentService(db)
        
        sales_users = db.query(User).filter(User.role == "sales").all()
        
        results = []
        for user in sales_users:
            success = sales_agent.send_weekly_summary(user.id)
            results.append({"user_id": user.id, "name": user.name, "success": success})
        
        return {"message": f"Weekly summaries sent to {len(sales_users)} sales reps", "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 