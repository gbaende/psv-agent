from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date
import asyncio

from app.database import get_db
from app.services.sales_agent import SalesAgentService
from app.models import User, TeamLeaderboard


class SalesAgentScheduler:
    """Autonomous Sales Agent Scheduler for proactive sales management"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.setup_sales_jobs()
    
    def setup_sales_jobs(self):
        """Setup all sales agent automation jobs"""
        
        # Monday 9:00 AM - Send weekly goal prompts to all sales reps
        self.scheduler.add_job(
            func=self.monday_goal_prompts,
            trigger=CronTrigger(day_of_week=0, hour=9, minute=0),  # Monday 9 AM
            id='monday_goal_prompts',
            name='Send Monday Goal Prompts',
            replace_existing=True
        )
        
        # Wednesday 2:00 PM - Send mid-week coaching nudges
        self.scheduler.add_job(
            func=self.wednesday_nudges,
            trigger=CronTrigger(day_of_week=2, hour=14, minute=0),  # Wednesday 2 PM
            id='wednesday_nudges',
            name='Send Wednesday Coaching Nudges',
            replace_existing=True
        )
        
        # Friday 5:00 PM - Send weekly summaries and generate leaderboards
        self.scheduler.add_job(
            func=self.friday_summaries,
            trigger=CronTrigger(day_of_week=4, hour=17, minute=0),  # Friday 5 PM
            id='friday_summaries',
            name='Send Friday Weekly Summaries',
            replace_existing=True
        )
        
        # Tuesday 10:00 AM - Follow up with non-responders from Monday
        self.scheduler.add_job(
            func=self.tuesday_followups,
            trigger=CronTrigger(day_of_week=1, hour=10, minute=0),  # Tuesday 10 AM
            id='tuesday_followups',
            name='Follow up with non-responders',
            replace_existing=True
        )
        
        # Daily 6:00 PM - Check for milestone achievements and celebrate
        self.scheduler.add_job(
            func=self.daily_milestone_check,
            trigger=CronTrigger(hour=18, minute=0),  # Daily 6 PM
            id='daily_milestone_check',
            name='Daily Milestone Celebrations',
            replace_existing=True
        )
    
    async def monday_goal_prompts(self):
        """Send Monday morning goal-setting prompts to all sales reps"""
        print(f"🎯 [SALES AGENT] Starting Monday goal prompts at {datetime.now()}")
        
        try:
            # Get async database session
            async for db in get_db():
                sales_agent = SalesAgentService(db)
                
                # Get all sales team members
                result = await db.execute(select(User).where(User.role == "sales"))
                sales_users = result.scalars().all()
                
                success_count = 0
                for user in sales_users:
                    try:
                        # Check if user already has goals for this week
                        week_start = sales_agent.get_current_week_start()
                        existing_progress = await sales_agent.get_weekly_progress(user.id, week_start)
                        
                        if existing_progress['calls_target'] > 0:
                            # User already set goals, send confirmation instead
                            await self._send_goal_confirmation(sales_agent, user, existing_progress)
                        else:
                            # Send goal-setting prompt
                            success = await sales_agent.send_monday_goal_prompt(user.id)
                            if success:
                                success_count += 1
                                print(f"✅ Sent Monday prompt to {user.name}")
                            else:
                                print(f"❌ Failed to send Monday prompt to {user.name}")
                                
                    except Exception as e:
                        print(f"❌ Error sending prompt to {user.name}: {e}")
                
                print(f"🎯 [SALES AGENT] Monday prompts completed: {success_count}/{len(sales_users)} sent")
                break  # Exit the async generator loop
            
        except Exception as e:
            print(f"❌ [SALES AGENT] Error in Monday goal prompts: {e}")
    
    async def wednesday_nudges(self):
        """Send Wednesday mid-week coaching nudges"""
        print(f"📊 [SALES AGENT] Starting Wednesday nudges at {datetime.now()}")
        
        try:
            async for db in get_db():
                sales_agent = SalesAgentService(db)
                
                result = await db.execute(select(User).where(User.role == "sales"))
                sales_users = result.scalars().all()
                
                success_count = 0
                for user in sales_users:
                    try:
                        # Only send nudge if user has goals for this week
                        week_start = sales_agent.get_current_week_start()
                        progress = await sales_agent.get_weekly_progress(user.id, week_start)
                        
                        if progress['calls_target'] > 0 or progress['demos_target'] > 0 or progress['proposals_target'] > 0:
                            success = await sales_agent.send_midweek_nudge(user.id)
                            if success:
                                success_count += 1
                                print(f"✅ Sent Wednesday nudge to {user.name}")
                            else:
                                print(f"❌ Failed to send Wednesday nudge to {user.name}")
                        else:
                            print(f"⏩ Skipping {user.name} - no goals set for this week")
                            
                    except Exception as e:
                        print(f"❌ Error sending nudge to {user.name}: {e}")
                
                print(f"📊 [SALES AGENT] Wednesday nudges completed: {success_count}/{len(sales_users)} sent")
                break
                
        except Exception as e:
            print(f"❌ [SALES AGENT] Error in Wednesday nudges: {e}")
    
    async def friday_summaries(self):
        """Send Friday weekly summaries and update leaderboards"""
        print(f"🏁 [SALES AGENT] Starting Friday summaries at {datetime.now()}")
        
        try:
            async for db in get_db():
                sales_agent = SalesAgentService(db)
                
                result = await db.execute(select(User).where(User.role == "sales"))
                sales_users = result.scalars().all()
                week_start = sales_agent.get_current_week_start()
                
                # Generate and store leaderboard
                leaderboard = await sales_agent.get_team_leaderboard(week_start)
                await self._store_weekly_leaderboard(db, leaderboard, week_start)
                
                # Send individual summaries
                summary_count = 0
                for user in sales_users:
                    try:
                        progress = await sales_agent.get_weekly_progress(user.id, week_start)
                        
                        if progress['calls_target'] > 0 or progress['demos_target'] > 0 or progress['proposals_target'] > 0:
                            success = await sales_agent.send_weekly_summary(user.id)
                            if success:
                                summary_count += 1
                                print(f"✅ Sent Friday summary to {user.name}")
                            else:
                                print(f"❌ Failed to send Friday summary to {user.name}")
                        else:
                            print(f"⏩ Skipping {user.name} - no goals set for this week")
                            
                    except Exception as e:
                        print(f"❌ Error sending summary to {user.name}: {e}")
                
                # Send team celebration message if there are high performers
                await self._send_team_celebration(sales_agent, leaderboard)
                
                print(f"🏁 [SALES AGENT] Friday summaries completed: {summary_count}/{len(sales_users)} sent")
                break
                
        except Exception as e:
            print(f"❌ [SALES AGENT] Error in Friday summaries: {e}")
    
    async def tuesday_followups(self):
        """Follow up with sales reps who didn't respond to Monday's prompt"""
        print(f"🔔 [SALES AGENT] Starting Tuesday followups at {datetime.now()}")
        
        try:
            async for db in get_db():
                sales_agent = SalesAgentService(db)
                
                result = await db.execute(select(User).where(User.role == "sales"))
                sales_users = result.scalars().all()
                
                followup_count = 0
                for user in sales_users:
                    try:
                        week_start = sales_agent.get_current_week_start()
                        progress = await sales_agent.get_weekly_progress(user.id, week_start)
                        
                        # If no goals set, send friendly followup
                        if progress['calls_target'] == 0 and progress['demos_target'] == 0 and progress['proposals_target'] == 0:
                            await self._send_tuesday_followup(sales_agent, user)
                            followup_count += 1
                            print(f"✅ Sent Tuesday followup to {user.name}")
                            
                    except Exception as e:
                        print(f"❌ Error sending followup to {user.name}: {e}")
                
                print(f"🔔 [SALES AGENT] Tuesday followups completed: {followup_count} sent")
                break
                
        except Exception as e:
            print(f"❌ [SALES AGENT] Error in Tuesday followups: {e}")
    
    async def daily_milestone_check(self):
        """Check for daily milestones and send celebrations"""
        print(f"🎉 [SALES AGENT] Starting daily milestone check at {datetime.now()}")
        
        try:
            async for db in get_db():
                sales_agent = SalesAgentService(db)
                
                result = await db.execute(select(User).where(User.role == "sales"))
                sales_users = result.scalars().all()
                week_start = sales_agent.get_current_week_start()
                
                celebrations_sent = 0
                for user in sales_users:
                    try:
                        progress = await sales_agent.get_weekly_progress(user.id, week_start)
                        
                        # Check for milestone achievements
                        milestone_message = self._check_milestones(user, progress)
                        if milestone_message:
                            # Send celebration DM (simulated since Slack is disabled)
                            print(f"🎉 Milestone celebration for {user.name}: {milestone_message}")
                            celebrations_sent += 1
                            
                    except Exception as e:
                        print(f"❌ Error checking milestones for {user.name}: {e}")
                
                if celebrations_sent > 0:
                    print(f"🎉 [SALES AGENT] Daily milestones: {celebrations_sent} celebrations sent")
                break
                
        except Exception as e:
            print(f"❌ [SALES AGENT] Error in daily milestone check: {e}")
    
    async def _send_goal_confirmation(self, sales_agent: SalesAgentService, user: User, progress: dict):
        """Send confirmation message for users who already set goals"""
        message = f"""👋 Good morning {user.name}! 

I see you've already set your goals for this week:
📞 Calls: {progress['calls_target']}
🎬 Demos: {progress['demos_target']}
📋 Proposals: {progress['proposals_target']}

Would you like to revise them, or are you ready to crush these numbers? Reply with new numbers if you want to adjust, otherwise you're all set! 💪"""
        
        # Simulate sending message since Slack is disabled
        print(f"📧 Goal confirmation to {user.name}: {message}")
        return True
    
    async def _send_tuesday_followup(self, sales_agent: SalesAgentService, user: User):
        """Send Tuesday followup to non-responders"""
        message = f"""👋 Hey {user.name}! 

I noticed you haven't set your goals for this week yet. No worries - it happens!

When you have a moment, just reply with your numbers for:
📞 **Discovery Calls** 
🎬 **Demos/Presentations**
📋 **Proposals**

For example: "I'll do 15 calls, 4 demos, and 2 proposals this week"

The week is still young - let's make it count! 🚀"""
        
        # Simulate sending message since Slack is disabled
        print(f"📧 Tuesday followup to {user.name}: {message}")
        return True
    
    def _check_milestones(self, user: User, progress: dict) -> str:
        """Check if user hit any milestones worth celebrating"""
        celebrations = []
        
        # Check for 100% completion in any category
        if progress['calls_percentage'] == 100 and progress['calls_target'] > 0:
            celebrations.append(f"🎯 You just hit your weekly call target! {progress['calls_completed']}/{progress['calls_target']} calls complete!")
        
        if progress['demos_percentage'] == 100 and progress['demos_target'] > 0:
            celebrations.append(f"🎬 Demo target achieved! {progress['demos_completed']}/{progress['demos_target']} demos done!")
        
        if progress['proposals_percentage'] == 100 and progress['proposals_target'] > 0:
            celebrations.append(f"📋 All proposals submitted! {progress['proposals_completed']}/{progress['proposals_target']} proposals sent!")
        
        # Check for overall completion
        if progress['overall_percentage'] == 100:
            celebrations.append("🏆 WEEK COMPLETE! You've hit ALL your targets! Absolutely crushing it!")
        
        # Check for exceeding targets (>100%)
        if progress['overall_percentage'] > 100:
            celebrations.append(f"🚀 You're at {progress['overall_percentage']}% of your targets - going above and beyond!")
        
        if celebrations:
            return f"🎉 **Milestone Alert!** 🎉\n\n" + "\n".join(celebrations) + f"\n\nKeep up the amazing work, {user.name}! 💪"
        
        return None
    
    async def _store_weekly_leaderboard(self, db: AsyncSession, leaderboard: list, week_start: date):
        """Store weekly leaderboard snapshot in database"""
        try:
            # Clear existing leaderboard for this week
            await db.execute(
                select(TeamLeaderboard).where(TeamLeaderboard.week_start == week_start)
            )
            
            # Store new leaderboard
            for rank, entry in enumerate(leaderboard, 1):
                leaderboard_entry = TeamLeaderboard(
                    week_start=week_start,
                    user_id=entry['user_id'],
                    overall_percentage=entry['overall_pct'],
                    calls_percentage=entry['calls_pct'],
                    demos_percentage=entry['demos_pct'],
                    proposals_percentage=entry['proposals_pct'],
                    overall_rank=rank
                )
                db.add(leaderboard_entry)
            
            await db.commit()
            print(f"📊 Stored weekly leaderboard for {week_start}")
            
        except Exception as e:
            print(f"❌ Error storing leaderboard: {e}")
            await db.rollback()
    
    async def _send_team_celebration(self, sales_agent: SalesAgentService, leaderboard: list):
        """Send team celebration message for top performers"""
        if not leaderboard:
            return
        
        # Find top performers (>80% overall)
        top_performers = [entry for entry in leaderboard if entry['overall_pct'] >= 80]
        
        if top_performers:
            # This would send to a team channel - for now just log
            print(f"🏆 Top performers this week: {[p['name'] for p in top_performers[:3]]}")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("🤖 [SALES AGENT] Scheduler started - autonomous sales management active!")
            print("📅 Scheduled jobs:")
            print("   - Monday 9:00 AM: Goal setting prompts")
            print("   - Tuesday 10:00 AM: Follow-up with non-responders") 
            print("   - Wednesday 2:00 PM: Mid-week coaching nudges")
            print("   - Friday 5:00 PM: Weekly summaries & leaderboards")
            print("   - Daily 6:00 PM: Milestone celebrations")
        else:
            print("🤖 [SALES AGENT] Scheduler is already running")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 [SALES AGENT] Scheduler stopped")
        else:
            print("🛑 [SALES AGENT] Scheduler is not running")
    
    def get_job_status(self):
        """Get status of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if hasattr(job, 'next_run_time') and job.next_run_time else "Not scheduled",
                "trigger": str(job.trigger)
            })
        return jobs


# Global scheduler instance
sales_scheduler = SalesAgentScheduler() 