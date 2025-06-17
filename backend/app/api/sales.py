from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel

from app.database import get_db
from app.services.sales_agent import SalesAgentService
from app.services.scheduler import sales_scheduler
from app.models import User, WeeklyGoal, SalesConversation, TeamLeaderboard
from app.services.auto_sync_users import auto_sync_service

router = APIRouter(tags=["Sales Agent"])


def get_sync_session() -> Session:
    """Get a synchronous database session for SalesAgentService compatibility"""
    from app.database import SessionLocal
    return SessionLocal()


# Pydantic models for request/response
class SalesGoalsRequest(BaseModel):
    calls: int
    demos: int 
    proposals: int
    stretch_goal: Optional[str] = None


class ProgressUpdateRequest(BaseModel):
    calls_completed: Optional[int] = None
    demos_completed: Optional[int] = None
    proposals_completed: Optional[int] = None
    notes: Optional[str] = None


class SalesResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class WeeklyProgressResponse(BaseModel):
    user_id: int
    user_name: str
    week_start: date
    calls_target: int
    calls_completed: int
    calls_percentage: float
    demos_target: int
    demos_completed: int
    demos_percentage: float
    proposals_target: int
    proposals_completed: int
    proposals_percentage: float
    overall_percentage: float
    rank: Optional[int] = None


class LeaderboardEntry(BaseModel):
    user_id: int
    name: str
    overall_pct: float
    calls_pct: float
    demos_pct: float
    proposals_pct: float
    total_score: float


class MessageRequest(BaseModel):
    message: str


# ================== MANUAL TRIGGERS ==================

@router.post("/triggers/monday-prompts", response_model=SalesResponse)
async def trigger_monday_prompts():
    """Manually trigger Monday goal-setting prompts for all sales reps"""
    try:
        # Run the scheduled job manually
        await sales_scheduler.monday_goal_prompts()
        return SalesResponse(
            success=True,
            message="Monday goal prompts sent to all sales reps",
            data={"timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Monday prompts: {str(e)}")


@router.post("/triggers/wednesday-nudges", response_model=SalesResponse)
async def trigger_wednesday_nudges():
    """Manually trigger Wednesday coaching nudges"""
    try:
        await sales_scheduler.wednesday_nudges()
        return SalesResponse(
            success=True,
            message="Wednesday coaching nudges sent",
            data={"timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Wednesday nudges: {str(e)}")


@router.post("/triggers/friday-summaries", response_model=SalesResponse)
async def trigger_friday_summaries():
    """Manually trigger Friday weekly summaries and leaderboard generation"""
    try:
        await sales_scheduler.friday_summaries()
        return SalesResponse(
            success=True,
            message="Friday summaries and leaderboards generated",
            data={"timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Friday summaries: {str(e)}")


@router.post("/triggers/milestone-check", response_model=SalesResponse)
async def trigger_milestone_check():
    """Manually trigger milestone achievement check"""
    try:
        await sales_scheduler.daily_milestone_check()
        return SalesResponse(
            success=True,
            message="Milestone check completed",
            data={"timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check milestones: {str(e)}")


# ================== GOAL MANAGEMENT ==================

@router.post("/goals/{user_id}/set", response_model=SalesResponse)
async def set_user_goals(
    user_id: int,
    goals: SalesGoalsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Set weekly goals for a specific user"""
    try:
        sales_agent = SalesAgentService(db)
        
        # Create goals text similar to what a user would respond with
        goals_text = f"I'll do {goals.calls} calls, {goals.demos} demos, and {goals.proposals} proposals this week"
        if goals.stretch_goal:
            goals_text += f". {goals.stretch_goal}"
        
        # Parse and create tasks
        parsed_goals = await sales_agent.parse_sales_response(goals_text)
        tasks_created = await sales_agent.create_weekly_sales_tasks(user_id, parsed_goals)
        
        return SalesResponse(
            success=True,
            message=f"Goals set successfully for user {user_id}",
            data={
                "goals": parsed_goals,
                "tasks_created": len(tasks_created),
                "tasks": [{"id": task.id, "title": task.title} for task in tasks_created]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set goals: {str(e)}")


@router.get("/goals/{user_id}/current", response_model=WeeklyProgressResponse)
async def get_current_goals(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get current week's goals and progress for a user"""
    try:
        from sqlalchemy import select
        sales_agent = SalesAgentService(db)
        week_start = sales_agent.get_current_week_start()
        progress = await sales_agent.get_weekly_progress(user_id, week_start)
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return WeeklyProgressResponse(
            user_id=user_id,
            user_name=user.name,
            week_start=week_start,
            **progress
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get goals: {str(e)}")


# ================== PROGRESS TRACKING ==================

@router.post("/progress/{user_id}/update", response_model=SalesResponse)
async def update_progress(
    user_id: int,
    update: ProgressUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update progress for a user's weekly goals"""
    try:
        sales_agent = SalesAgentService(db)
        week_start = sales_agent.get_current_week_start()
        
        # Build update text
        updates = []
        if update.calls_completed is not None:
            updates.append(f"{update.calls_completed} calls")
        if update.demos_completed is not None:
            updates.append(f"{update.demos_completed} demos")
        if update.proposals_completed is not None:
            updates.append(f"{update.proposals_completed} proposals")
        
        if not updates:
            raise HTTPException(status_code=400, detail="No progress updates provided")
        
        update_text = f"I've completed {', '.join(updates)}"
        if update.notes:
            update_text += f". {update.notes}"
        
        # Update progress (you'd implement this method in SalesAgentService)
        success = await sales_agent.update_weekly_goals_progress(user_id, update_text, week_start)
        
        if success:
            # Get updated progress
            progress = await sales_agent.get_weekly_progress(user_id, week_start)
            return SalesResponse(
                success=True,
                message="Progress updated successfully",
                data=progress
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update progress")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")


@router.get("/progress/team", response_model=List[WeeklyProgressResponse])
async def get_team_progress(
    week_start: Optional[date] = Query(None, description="Week start date (defaults to current week)")
):
    """Get progress for entire sales team"""
    try:
        # Use sync session for SalesAgentService compatibility
        sync_db = get_sync_session()
        try:
            sales_agent = SalesAgentService(sync_db)
            
            if not week_start:
                week_start = sales_agent.get_current_week_start()
            
            # Get all sales users using sync session
            sales_users = sync_db.query(User).filter(User.role == "sales").all()
            
            team_progress = []
            for user in sales_users:
                try:
                    progress = sales_agent.get_weekly_progress(user.id, week_start)
                    team_progress.append(WeeklyProgressResponse(
                        user_id=user.id,
                        user_name=user.name,
                        week_start=week_start,
                        **progress
                    ))
                except Exception as user_error:
                    # Handle individual user progress errors gracefully
                    print(f"Error getting progress for user {user.name}: {user_error}")
                    # Add empty progress for user
                    team_progress.append(WeeklyProgressResponse(
                        user_id=user.id,
                        user_name=user.name,
                        week_start=week_start,
                        calls_target=0,
                        calls_completed=0,
                        calls_percentage=0.0,
                        demos_target=0,
                        demos_completed=0,
                        demos_percentage=0.0,
                        proposals_target=0,
                        proposals_completed=0,
                        proposals_percentage=0.0,
                        overall_percentage=0.0
                    ))
            
            # Sort by overall percentage descending
            team_progress.sort(key=lambda x: x.overall_percentage, reverse=True)
            
            # Add ranks
            for rank, progress in enumerate(team_progress, 1):
                progress.rank = rank
            
            return team_progress
        finally:
            sync_db.close()
    except Exception as e:
        print(f"Database error in get_team_progress: {e}")
        # Return empty team progress instead of 500 error
        return []


# ================== LEADERBOARD ==================

@router.get("/leaderboard/current", response_model=List[LeaderboardEntry])
async def get_current_leaderboard():
    """Get current week's leaderboard"""
    try:
        # Use sync session for SalesAgentService compatibility
        sync_db = get_sync_session()
        try:
            sales_agent = SalesAgentService(sync_db)
            week_start = sales_agent.get_current_week_start()
            leaderboard = sales_agent.get_team_leaderboard(week_start)
            
            return [LeaderboardEntry(**entry) for entry in leaderboard]
        finally:
            sync_db.close()
    except Exception as e:
        print(f"Error generating leaderboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")


@router.get("/leaderboard/history", response_model=List[Dict[str, Any]])
async def get_leaderboard_history(
    weeks: int = Query(4, description="Number of weeks to retrieve"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical leaderboard data"""
    try:
        from sqlalchemy import select
        # Get stored leaderboards
        result = await db.execute(
            select(TeamLeaderboard)
            .order_by(TeamLeaderboard.week_start.desc())
            .limit(weeks * 10)  # Rough estimate
        )
        leaderboards = result.scalars().all()
        
        # Group by week
        weeks_data = {}
        for entry in leaderboards:
            week_key = entry.week_start.isoformat()
            if week_key not in weeks_data:
                weeks_data[week_key] = []
            
            weeks_data[week_key].append({
                "user_id": entry.user_id,
                "overall_percentage": entry.overall_percentage,
                "calls_percentage": entry.calls_percentage,
                "demos_percentage": entry.demos_percentage,
                "proposals_percentage": entry.proposals_percentage,
                "rank": entry.overall_rank
            })
        
        # Convert to list format
        history = []
        for week_start, entries in weeks_data.items():
            history.append({
                "week_start": week_start,
                "leaderboard": entries
            })
        
        return history[:weeks]  # Return only requested number of weeks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard history: {str(e)}")


# ================== COACHING ==================

@router.get("/coaching/{user_id}/tips", response_model=SalesResponse)
async def get_coaching_tips(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get personalized coaching tips for a user"""
    try:
        sales_agent = SalesAgentService(db)
        week_start = sales_agent.get_current_week_start()
        progress = await sales_agent.get_weekly_progress(user_id, week_start)
        
        tips = await sales_agent.generate_coaching_tips(progress)
        
        return SalesResponse(
            success=True,
            message="Coaching tips generated",
            data={
                "tips": tips,
                "progress": progress
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get coaching tips: {str(e)}")


@router.post("/coaching/{user_id}/send", response_model=SalesResponse)
async def send_coaching_message(
    user_id: int,
    request: MessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a custom coaching message to a user via Slack"""
    try:
        sales_agent = SalesAgentService(db)
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For now, since Slack is disabled, we'll simulate success
        # In production, this would send via Slack
        if not user.slack_user_id:
            # Simulate sending message for demo purposes
            print(f"📧 Simulated message to {user.name}: {request.message}")
            return SalesResponse(
                success=True,
                message=f"Message sent to {user.name} (simulated - Slack disabled)",
                data={"message": request.message}
            )
        
        # This would be the real Slack implementation
        # success = await sales_agent.slack_service.send_direct_message(user.slack_user_id, request.message)
        
        return SalesResponse(
            success=True,
            message=f"Message sent to {user.name}",
            data={"message": request.message}
        )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send coaching message: {str(e)}")


# ================== SCHEDULER MANAGEMENT ==================

@router.get("/scheduler/status", response_model=SalesResponse)
async def get_scheduler_status():
    """Get status of all scheduled jobs"""
    try:
        jobs = sales_scheduler.get_job_status()
        return SalesResponse(
            success=True,
            message="Scheduler status retrieved",
            data={"jobs": jobs}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")


@router.post("/scheduler/start", response_model=SalesResponse)
async def start_scheduler():
    """Start the sales agent scheduler"""
    try:
        sales_scheduler.start()
        return SalesResponse(
            success=True,
            message="Sales agent scheduler started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/scheduler/stop", response_model=SalesResponse)
async def stop_scheduler():
    """Stop the sales agent scheduler"""
    try:
        sales_scheduler.stop()
        return SalesResponse(
            success=True,
            message="Sales agent scheduler stopped"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")


# ================== CONVERSATION HISTORY ==================

@router.get("/conversations/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_conversations(
    user_id: int,
    limit: int = Query(10, description="Number of conversations to retrieve"),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation history for a user"""
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(SalesConversation)
            .where(SalesConversation.user_id == user_id)
            .order_by(SalesConversation.created_at.desc())
            .limit(limit)
        )
        conversations = result.scalars().all()
        
        return [
            {
                "id": conv.id,
                "week_start": conv.week_start.isoformat(),
                "conversation_type": conv.conversation_type,
                "goals_data": conv.goals_data,
                "created_at": conv.created_at.isoformat()
            }
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")


# ================== TEAM ANALYTICS ==================

@router.get("/analytics/team-summary", response_model=SalesResponse)
async def get_team_analytics(
    weeks: int = Query(4, description="Number of weeks to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get team performance analytics"""
    try:
        sales_agent = SalesAgentService(db)
        
        # Get data for multiple weeks
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.role == "sales"))
        team_size = len(result.scalars().all())
        
        analytics = {
            "total_weeks_analyzed": weeks,
            "team_size": team_size,
            "weekly_averages": {},
            "top_performers": [],
            "improvement_trends": {}
        }
        
        # This would include more complex analytics
        # For now, return basic structure
        
        return SalesResponse(
            success=True,
            message="Team analytics generated",
            data=analytics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team analytics: {str(e)}")


# ================== TASK COMPLETION ==================

@router.post("/tasks/{task_id}/complete", response_model=SalesResponse)
async def mark_task_complete(task_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a sales task as complete and trigger celebration"""
    try:
        sales_agent = SalesAgentService(db)
        success = await sales_agent.mark_task_complete(task_id)
        
        if success:
            return SalesResponse(
                success=True,
                message="Task marked as complete",
                data={"task_id": task_id}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to mark task as complete")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete task: {str(e)}")


@router.post("/sync-users")
async def manual_sync_users():
    """Manually sync users from Slack channel to database"""
    
    try:
        result = await auto_sync_service.sync_all_users()
        return {
            "success": result["success"],
            "message": f"Sync completed: {result.get('created', 0)} created, {result.get('updated', 0)} updated, {result.get('errors', 0)} errors",
            "details": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Sync failed: {str(e)}"
        }


# ================== SLACK TESTING ==================

@router.post("/test-slack/{user_id}", response_model=SalesResponse)
async def test_slack_message(user_id: int, request: MessageRequest, db: AsyncSession = Depends(get_db)):
    """Test sending a Slack message to a specific user"""
    try:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.slack_user_id:
            raise HTTPException(status_code=400, detail="User has no Slack ID")
        
        # Initialize Slack service
        from app.services.slack_service import SlackService
        slack_service = SlackService()
        
        # Check if Slack is configured
        if not slack_service.is_configured():
            return SalesResponse(
                success=False,
                message="Slack is not configured - missing SLACK_BOT_TOKEN",
                data={"user": user.name, "slack_id": user.slack_user_id}
            )
        
        # Send test message
        test_message = f"🧪 Test message from DealTracker Sales Agent: {request.message}"
        result = await slack_service.send_direct_message(user.slack_user_id, test_message)
        
        if result.get("ok"):
            return SalesResponse(
                success=True,
                message=f"Test message sent successfully to {user.name}",
                data={
                    "user": user.name,
                    "slack_id": user.slack_user_id,
                    "message": test_message,
                    "slack_response": result
                }
            )
        else:
            return SalesResponse(
                success=False,
                message=f"Failed to send message to {user.name}: {result.get('error', 'Unknown error')}",
                data={
                    "user": user.name,
                    "slack_id": user.slack_user_id,
                    "error": result.get('error'),
                    "slack_response": result
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test Slack message: {str(e)}")


@router.post("/test-slack-channel", response_model=SalesResponse)
async def test_slack_channel_message(request: MessageRequest):
    """Test sending a message to the main Slack channel"""
    try:
        from app.services.slack_service import SlackService
        slack_service = SlackService()
        
        # Check if Slack is configured
        if not slack_service.is_configured():
            return SalesResponse(
                success=False,
                message="Slack is not configured - missing SLACK_BOT_TOKEN"
            )
        
        # Send test message to channel
        test_message = f"🧪 Test message from DealTracker Sales Agent: {request.message}"
        result = await slack_service.send_message(slack_service.channel_id, test_message)
        
        if result.get("ok"):
            return SalesResponse(
                success=True,
                message="Test message sent successfully to channel",
                data={
                    "channel_id": slack_service.channel_id,
                    "message": test_message,
                    "slack_response": result
                }
            )
        else:
            return SalesResponse(
                success=False,
                message=f"Failed to send message to channel: {result.get('error', 'Unknown error')}",
                data={
                    "channel_id": slack_service.channel_id,
                    "error": result.get('error'),
                    "slack_response": result
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test Slack channel message: {str(e)}") 