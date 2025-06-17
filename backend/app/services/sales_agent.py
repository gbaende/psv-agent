import json
import math
import random
import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.models import User, Project, Task, Goal, WeeklyGoal
from app.database import get_db
from app.services.slack_service import SlackService
from app.services.ai_service import AIService


class SalesAgentService:
    """Autonomous Sales Project Manager Agent"""
    
    def __init__(self, db: Session):
        self.db = db
        self.slack_service = SlackService()
        self.ai_service = AIService()
        self.templates_path = Path("ai_templates/sales/")
    
    def _send_slack_message_sync(self, user_slack_id: str, message: str) -> bool:
        """Helper to send Slack message synchronously"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.slack_service.send_direct_message(user_slack_id, message)
            )
            loop.close()
            return result.get("ok", False)
        except Exception as e:
            print(f"Error sending Slack message: {e}")
            return False
    
    async def _send_slack_message_async(self, user_slack_id: str, message: str) -> bool:
        """Helper to send Slack message asynchronously"""
        try:
            result = await self.slack_service.send_direct_message(user_slack_id, message)
            return result.get("ok", False)
        except Exception as e:
            print(f"Error sending Slack message: {e}")
            return False
    
    def load_template(self, template_name: str) -> str:
        """Load a sales prompt template"""
        template_path = self.templates_path / template_name
        if template_path.exists():
            return template_path.read_text()
        # Return fallback template if file doesn't exist
        return f"Hi {{name}}! This is a {template_name.replace('_', ' ').replace('.txt', '')} message from DealTracker. Please check back later for more details."
    
    def get_current_week_start(self) -> date:
        """Get the Monday of the current week"""
        today = date.today()
        return today - timedelta(days=today.weekday())
    
    def get_or_create_sales_project(self) -> Project:
        """Get or create the persistent Sales Sprint project"""
        project = self.db.query(Project).filter(Project.name == "PSV Sales Agent Team").first()
        if not project:
            project = Project(
                name="PSV Sales Agent Team",
                description="Ongoing weekly sprints for the PSV sales team",
                start_date=date.today(),
                end_date=None,
                owner_id=1  # System project
            )
            self.db.add(project)
            self.db.commit()
        return project
    
    def parse_sales_response(self, text: str) -> Dict[str, int]:
        """Parse sales rep's goal response using AI"""
        prompt = f"""
        You are SalesPM. Extract numbers for calls, demos, and proposals from the rep's response. 
        If they don't mention a category, default to 0.
        
        Rep says: "{text}"
        
        Output JSON only in this exact format:
        {{"calls_target": 0, "demos_target": 0, "proposals_target": 0}}
        """
        
        try:
            # For now, use simple parsing since AI service might not be available
            # response = self.ai_service.generate_response(prompt)
            # Extract JSON from response
            # start_idx = response.find('{')
            # end_idx = response.rfind('}') + 1
            # if start_idx != -1 and end_idx != -1:
            #     json_str = response[start_idx:end_idx]
            #     return json.loads(json_str)
            pass
        except Exception as e:
            print(f"Error parsing sales response: {e}")
        
        # Fallback: simple text parsing
        text_lower = text.lower()
        goals = {"calls_target": 0, "demos_target": 0, "proposals_target": 0}
        
        # Simple regex-like parsing
        import re
        numbers = re.findall(r'\d+', text)
        if len(numbers) >= 3:
            goals["calls_target"] = int(numbers[0])
            goals["demos_target"] = int(numbers[1]) 
            goals["proposals_target"] = int(numbers[2])
        elif len(numbers) == 1:
            # If only one number, assume it's calls
            goals["calls_target"] = int(numbers[0])
        
        return goals
    
    def create_weekly_sales_tasks(self, user_id: int, week_start: date, goals: Dict[str, int]) -> int:
        """Create micro-tasks from parsed goals"""
        project = self.get_or_create_sales_project()
        
        # Clear existing tasks for this week
        week_end = week_start + timedelta(days=7)
        existing_tasks = self.db.query(Task).filter(
            Task.owner_id == user_id,
            Task.project_id == project.id,
            Task.created_at >= week_start,
            Task.created_at < week_end
        ).all()
        
        for task in existing_tasks:
            self.db.delete(task)
        
        tasks = []
        
        # Create call tasks (batch of 4)
        if goals["calls_target"] > 0:
            tasks.extend(self._generate_call_subtasks(
                user_id, project.id, week_start, goals["calls_target"]
            ))
        
        # Create demo tasks (individual)
        if goals["demos_target"] > 0:
            tasks.extend(self._generate_demo_tasks(
                user_id, project.id, week_start, goals["demos_target"]
            ))
        
        # Create proposal tasks (individual)
        if goals["proposals_target"] > 0:
            tasks.extend(self._generate_proposal_tasks(
                user_id, project.id, week_start, goals["proposals_target"]
            ))
        
        for task in tasks:
            self.db.add(task)
        self.db.commit()
        
        return len(tasks)
    
    def _generate_call_subtasks(self, user_id: int, project_id: int, 
                               week_start: date, total_calls: int) -> List[Task]:
        """Generate call tasks in batches of 4"""
        tasks = []
        batch_size = 4
        num_batches = math.ceil(total_calls / batch_size)
        
        for i in range(num_batches):
            count = min(batch_size, total_calls - i * batch_size)
            tasks.append(Task(
                title=f"☎️ Make {count} discovery calls",
                description=f"Make {count} outbound calls to prospective leads",
                owner_id=user_id,
                project_id=project_id,
                due_date=week_start + timedelta(days=6),
                priority="High",
                status="Not Started",
                task_type="calls"
            ))
        
        return tasks
    
    def _generate_demo_tasks(self, user_id: int, project_id: int,
                            week_start: date, total_demos: int) -> List[Task]:
        """Generate individual demo tasks"""
        tasks = []
        
        for i in range(total_demos):
            tasks.append(Task(
                title=f"🎬 Deliver product demo #{i+1}",
                description="Conduct product demonstration for qualified prospect",
                owner_id=user_id,
                project_id=project_id,
                due_date=week_start + timedelta(days=6),
                priority="Medium",
                status="Not Started",
                task_type="demos"
            ))
        
        return tasks
    
    def _generate_proposal_tasks(self, user_id: int, project_id: int,
                                week_start: date, total_proposals: int) -> List[Task]:
        """Generate individual proposal tasks"""
        tasks = []
        
        for i in range(total_proposals):
            tasks.append(Task(
                title=f"📋 Submit proposal #{i+1}",
                description="Create and send detailed proposal to prospect",
                owner_id=user_id,
                project_id=project_id,
                due_date=week_start + timedelta(days=6),
                priority="High", 
                status="Not Started",
                task_type="proposals"
            ))
        
        return tasks
    
    def get_weekly_progress(self, user_id: int, week_start: date) -> Dict:
        """Get current week's progress for a user"""
        project = self.get_or_create_sales_project()
        
        # Get tasks for this week
        tasks = self.db.query(Task).filter(
            Task.owner_id == user_id,
            Task.project_id == project.id,
            Task.created_at >= week_start,
            Task.created_at < week_start + timedelta(days=7)
        ).all()
        
        progress = {
            "calls_target": 0,
            "calls_completed": 0,
            "demos_target": 0,
            "demos_completed": 0,
            "proposals_target": 0,
            "proposals_completed": 0
        }
        
        for task in tasks:
            if task.task_type == "calls":
                # Extract number from title like "☎️ Make 4 discovery calls"
                import re
                numbers = re.findall(r'\d+', task.title)
                if numbers:
                    progress["calls_target"] += int(numbers[0])
                    if task.status == "Completed":
                        progress["calls_completed"] += int(numbers[0])
            elif task.task_type == "demos":
                progress["demos_target"] += 1
                if task.status == "Completed":
                    progress["demos_completed"] += 1
            elif task.task_type == "proposals":
                progress["proposals_target"] += 1
                if task.status == "Completed":
                    progress["proposals_completed"] += 1
        
        # Calculate percentages
        progress["calls_percentage"] = (
            (progress["calls_completed"] / progress["calls_target"] * 100) 
            if progress["calls_target"] > 0 else 0
        )
        progress["demos_percentage"] = (
            (progress["demos_completed"] / progress["demos_target"] * 100) 
            if progress["demos_target"] > 0 else 0
        )
        progress["proposals_percentage"] = (
            (progress["proposals_completed"] / progress["proposals_target"] * 100) 
            if progress["proposals_target"] > 0 else 0
        )
        
        # Overall percentage (weighted average)
        total_targets = progress["calls_target"] + progress["demos_target"] + progress["proposals_target"]
        if total_targets > 0:
            progress["overall_percentage"] = (
                (progress["calls_completed"] + progress["demos_completed"] + progress["proposals_completed"]) 
                / total_targets * 100
            )
        else:
            progress["overall_percentage"] = 0
        
        return progress
    
    def generate_coaching_tips(self, progress: Dict) -> List[str]:
        """Generate personalized coaching tips based on progress"""
        try:
            # For now, generate tips based on progress data
            tips = []
            
            # Analyze calls performance
            if progress["calls_percentage"] < 50:
                tips.append("📞 Focus on increasing your daily call volume. Try blocking 2-3 hours each morning for prospecting calls.")
            elif progress["calls_percentage"] < 80:
                tips.append("📞 Good call activity! Consider improving your call quality by preparing better opening statements.")
            else:
                tips.append("📞 Excellent call performance! Keep up the momentum and focus on qualifying prospects better.")
            
            # Analyze demos performance
            if progress["demos_target"] > 0:
                if progress["demos_percentage"] < 50:
                    tips.append("🎬 Work on converting more calls to demos. Practice your discovery questions to identify pain points.")
                elif progress["demos_percentage"] < 80:
                    tips.append("🎬 Solid demo booking! Focus on demo preparation and customizing presentations to prospect needs.")
                else:
                    tips.append("🎬 Outstanding demo performance! Consider sharing your demo techniques with the team.")
            
            # Analyze proposals performance
            if progress["proposals_target"] > 0:
                if progress["proposals_percentage"] < 50:
                    tips.append("📋 Focus on qualifying prospects better during demos to increase proposal conversion rates.")
                elif progress["proposals_percentage"] < 80:
                    tips.append("📋 Good proposal activity! Work on follow-up timing and addressing objections proactively.")
                else:
                    tips.append("📋 Excellent proposal performance! Your qualification and demo skills are paying off.")
            
            # Overall performance tip
            if progress["overall_percentage"] >= 80:
                tips.append("🚀 You're performing at a high level! Consider mentoring newer team members.")
            elif progress["overall_percentage"] >= 60:
                tips.append("💪 Solid overall performance! Focus on consistency across all activities.")
            else:
                tips.append("📈 Remember that every expert was once a beginner. Focus on daily improvement and the results will follow.")
            
            return tips[:3]  # Return max 3 tips
            
        except Exception as e:
            print(f"Error generating coaching tips: {e}")
            return ["Keep pushing! Focus on your daily activities and the results will follow."]
    
    def send_monday_goal_prompt(self, user_id: int) -> bool:
        """Send Monday morning goal-setting prompt"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        week_start = self.get_current_week_start()
        week_end = week_start + timedelta(days=6)
        
        # Get previous week's performance
        prev_week = week_start - timedelta(days=7)
        prev_progress = self.get_weekly_progress(user_id, prev_week)
        
        previous_performance = f"Calls: {prev_progress['calls_completed']}/{prev_progress['calls_target']}, Demos: {prev_progress['demos_completed']}/{prev_progress['demos_target']}, Proposals: {prev_progress['proposals_completed']}/{prev_progress['proposals_target']}"
        
        # Load and format template
        template = self.load_template("weekly_goal_prompt.txt")
        message = template.format(
            name=user.name or "there",
            week_start=week_start.strftime("%b %d"),
            week_end=week_end.strftime("%b %d"),
            previous_performance=previous_performance if prev_progress['calls_target'] > 0 else "Starting fresh!"
        )
        
        # Send Slack DM
        return self._send_slack_message_sync(user.slack_user_id, message)
    
    def send_midweek_nudge(self, user_id: int) -> bool:
        """Send Wednesday mid-week coaching nudge"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        week_start = self.get_current_week_start()
        progress = self.get_weekly_progress(user_id, week_start)
        
        # Calculate days left
        today = date.today()
        week_end = week_start + timedelta(days=6)
        days_left = (week_end - today).days
        
        # Generate coaching message
        coaching_tips = self.generate_coaching_tips(progress)
        
        # Load and format template
        template = self.load_template("mid_week_nudge_prompt.txt")
        message = template.format(
            name=user.name or "there",
            week_start=week_start.strftime("%b %d"),
            calls_target=progress["calls_target"],
            calls_completed=progress["calls_completed"],
            demos_target=progress["demos_target"], 
            demos_completed=progress["demos_completed"],
            proposals_target=progress["proposals_target"],
            proposals_completed=progress["proposals_completed"],
            overall_percentage=progress["overall_percentage"],
            days_left=days_left,
            coaching_message="Looking good!" if progress["overall_percentage"] >= 60 else "Let's pick up the pace!",
            specific_tips=coaching_tips
        )
        
        return self._send_slack_message_sync(user.slack_user_id, message)
    
    def send_weekly_summary(self, user_id: int) -> bool:
        """Send Friday end-of-week summary"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        week_start = self.get_current_week_start()
        progress = self.get_weekly_progress(user_id, week_start)
        
        # Performance assessment
        if progress["overall_percentage"] >= 100:
            assessment = "🎉 Outstanding week! You exceeded expectations"
        elif progress["overall_percentage"] >= 80:
            assessment = "💪 Solid performance! You hit most of your targets"
        elif progress["overall_percentage"] >= 60:
            assessment = "👍 Good effort! A few targets missed but progress made"
        else:
            assessment = "📈 Challenging week, but that's part of the process"
        
        # Generate wins list
        wins = []
        if progress["calls_percentage"] >= 100:
            wins.append(f"✅ Exceeded call target ({progress['calls_completed']}/{progress['calls_target']})")
        if progress["demos_percentage"] >= 100:
            wins.append(f"✅ Hit demo target ({progress['demos_completed']}/{progress['demos_target']})")
        if progress["proposals_percentage"] >= 100:
            wins.append(f"✅ Crushed proposal target ({progress['proposals_completed']}/{progress['proposals_target']})")
        
        if not wins:
            wins.append("✅ Stayed active and engaged throughout the week")
        
        wins_list = "\n".join(wins)
        
        # Load and format template
        template = self.load_template("end_week_summary_prompt.txt")
        message = template.format(
            name=user.name or "there",
            week_start=week_start.strftime("%b %d"),
            calls_completed=progress["calls_completed"],
            calls_target=progress["calls_target"],
            calls_percentage=progress["calls_percentage"],
            demos_completed=progress["demos_completed"],
            demos_target=progress["demos_target"],
            demos_percentage=progress["demos_percentage"],
            proposals_completed=progress["proposals_completed"],
            proposals_target=progress["proposals_target"],
            proposals_percentage=progress["proposals_percentage"],
            overall_percentage=progress["overall_percentage"],
            performance_assessment=assessment,
            wins_list=wins_list,
            improvement_areas="Focus on consistency and follow-up timing",
            team_ranking_message="Keep pushing - you're making great progress!",
            motivational_close="Every week is a chance to level up! 🚀"
        )
        
        return self._send_slack_message_sync(user.slack_user_id, message)
    
    def mark_task_complete(self, task_id: int) -> bool:
        """Mark a specific task as complete"""
        try:
            task = self.db.query(Task).filter(Task.id == task_id).first()
            
            if task:
                task.status = "Completed"
                self.db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error marking task complete: {e}")
            return False
    
    def get_team_leaderboard(self, week_start: date = None) -> List[Dict]:
        """Generate team leaderboard for the week"""
        if not week_start:
            week_start = self.get_current_week_start()
        
        try:
            # Get all sales users
            sales_users = self.db.query(User).filter(User.role == "sales").all()
            
            leaderboard = []
            for user in sales_users:
                progress = self.get_weekly_progress(user.id, week_start)
                
                # Calculate total score (weighted)
                total_score = (
                    progress["calls_percentage"] * 0.4 +
                    progress["demos_percentage"] * 0.3 +
                    progress["proposals_percentage"] * 0.3
                )
                
                leaderboard.append({
                    "user_id": user.id,
                    "name": user.name,
                    "overall_pct": progress["overall_percentage"],
                    "calls_pct": progress["calls_percentage"],
                    "demos_pct": progress["demos_percentage"],
                    "proposals_pct": progress["proposals_percentage"],
                    "total_score": total_score
                })
            
            # Sort by total score descending
            leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
            
            return leaderboard
            
        except Exception as e:
            print(f"Error generating leaderboard: {e}")
            return []
    
    async def send_monday_goal_prompt_async(self, user_id: int) -> bool:
        """Send Monday morning goal-setting prompt (async version)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        week_start = self.get_current_week_start()
        week_end = week_start + timedelta(days=6)
        
        # Get previous week's performance
        prev_week = week_start - timedelta(days=7)
        prev_progress = self.get_weekly_progress(user_id, prev_week)
        
        previous_performance = f"Calls: {prev_progress['calls_completed']}/{prev_progress['calls_target']}, Demos: {prev_progress['demos_completed']}/{prev_progress['demos_target']}, Proposals: {prev_progress['proposals_completed']}/{prev_progress['proposals_target']}"
        
        # Load and format template
        template = self.load_template("weekly_goal_prompt.txt")
        message = template.format(
            name=user.name or "there",
            week_start=week_start.strftime("%b %d"),
            week_end=week_end.strftime("%b %d"),
            previous_performance=previous_performance if prev_progress['calls_target'] > 0 else "Starting fresh!"
        )
        
        # Send Slack DM (async)
        return await self._send_slack_message_async(user.slack_user_id, message)

    async def send_midweek_nudge_async(self, user_id: int) -> bool:
        """Send Wednesday mid-week coaching nudge (async version)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        week_start = self.get_current_week_start()
        progress = self.get_weekly_progress(user_id, week_start)
        
        # Calculate days left
        today = date.today()
        week_end = week_start + timedelta(days=6)
        days_left = (week_end - today).days
        
        # Generate coaching message
        coaching_tips = self.generate_coaching_tips(progress)
        
        # Load and format template
        template = self.load_template("mid_week_nudge_prompt.txt")
        message = template.format(
            name=user.name or "there",
            week_start=week_start.strftime("%b %d"),
            calls_target=progress["calls_target"],
            calls_completed=progress["calls_completed"],
            demos_target=progress["demos_target"], 
            demos_completed=progress["demos_completed"],
            proposals_target=progress["proposals_target"],
            proposals_completed=progress["proposals_completed"],
            overall_percentage=progress["overall_percentage"],
            days_left=days_left,
            coaching_message="Looking good!" if progress["overall_percentage"] >= 60 else "Let's pick up the pace!",
            specific_tips=coaching_tips
        )
        
        return await self._send_slack_message_async(user.slack_user_id, message)

    async def send_weekly_summary_async(self, user_id: int) -> bool:
        """Send Friday end-of-week summary (async version)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        week_start = self.get_current_week_start()
        progress = self.get_weekly_progress(user_id, week_start)
        
        # Performance assessment
        if progress["overall_percentage"] >= 100:
            assessment = "🎉 Outstanding week! You exceeded expectations"
        elif progress["overall_percentage"] >= 80:
            assessment = "💪 Solid performance! You hit most of your targets"
        elif progress["overall_percentage"] >= 60:
            assessment = "👍 Good effort! A few targets missed but progress made"
        else:
            assessment = "📈 Challenging week, but that's part of the process"
        
        # Generate wins list
        wins = []
        if progress["calls_percentage"] >= 100:
            wins.append(f"✅ Exceeded call target ({progress['calls_completed']}/{progress['calls_target']})")
        if progress["demos_percentage"] >= 100:
            wins.append(f"✅ Hit demo target ({progress['demos_completed']}/{progress['demos_target']})")
        if progress["proposals_percentage"] >= 100:
            wins.append(f"✅ Crushed proposal target ({progress['proposals_completed']}/{progress['proposals_target']})")
        
        if not wins:
            wins.append("✅ Stayed active and engaged throughout the week")
        
        wins_list = "\n".join(wins)
        
        # Load and format template
        template = self.load_template("end_week_summary_prompt.txt")
        message = template.format(
            name=user.name or "there",
            week_start=week_start.strftime("%b %d"),
            calls_completed=progress["calls_completed"],
            calls_target=progress["calls_target"],
            calls_percentage=progress["calls_percentage"],
            demos_completed=progress["demos_completed"],
            demos_target=progress["demos_target"],
            demos_percentage=progress["demos_percentage"],
            proposals_completed=progress["proposals_completed"],
            proposals_target=progress["proposals_target"],
            proposals_percentage=progress["proposals_percentage"],
            overall_percentage=progress["overall_percentage"],
            performance_assessment=assessment,
            wins_list=wins_list,
            improvement_areas="Focus on consistency and follow-up timing",
            team_ranking_message="Keep pushing - you're making great progress!",
            motivational_close="Every week is a chance to level up! 🚀"
        )
        
        return await self._send_slack_message_async(user.slack_user_id, message) 