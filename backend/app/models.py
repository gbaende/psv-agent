from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    slack_user_id = Column(String(50), unique=True, nullable=True)  # For Slack integration
    role = Column(String(50), default="user")  # Added role for sales team identification
    created_at = Column(DateTime, default=datetime.utcnow)
    projects = relationship('Project', back_populates='owner')
    tasks = relationship('Task', back_populates='owner')
    goals = relationship('Goal', back_populates='owner')

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship('User', back_populates='projects')
    tasks = relationship('Task', back_populates='project')
    goals = relationship('Goal', back_populates='project')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="Not Started")  # Not Started, In Progress, Completed
    priority = Column(String(20), default="Medium")  # Low, Medium, High
    task_type = Column(String(50), default="general")  # Added for sales tasks: calls, demos, proposals
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)  # Added for completion tracking
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship('User', back_populates='tasks')
    project = relationship('Project', back_populates='tasks')

class Goal(Base):
    __tablename__ = 'goals'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    week_start = Column(Date, nullable=False)
    achieved = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship('User', back_populates='goals')
    project = relationship('Project', back_populates='goals')

class WeeklyGoal(Base):
    """Enhanced weekly goals for sales tracking"""
    __tablename__ = "weekly_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    
    # Sales targets
    calls_target = Column(Integer, default=0)
    demos_target = Column(Integer, default=0)
    proposals_target = Column(Integer, default=0)
    
    # Actual achievements (updated throughout the week)
    calls_completed = Column(Integer, default=0)
    demos_completed = Column(Integer, default=0)
    proposals_completed = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class SalesConversation(Base):
    """Track sales agent conversations with team members"""
    __tablename__ = "sales_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_slack_id = Column(String(50), nullable=False)  # Slack user ID
    week_start = Column(Date, nullable=False)
    conversation_type = Column(String(50), nullable=False)  # weekly_goals, midweek_check, weekly_summary
    
    # Store conversation data as JSON
    goals_data = Column(JSON, nullable=True)  # Store parsed goals
    thread_ts = Column(String(50), nullable=True)  # Slack thread timestamp for threading
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SalesMetric(Base):
    """Track detailed sales metrics and performance"""
    __tablename__ = "sales_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    
    # Detailed activity tracking
    calls_attempted = Column(Integer, default=0)
    calls_connected = Column(Integer, default=0)
    calls_qualified = Column(Integer, default=0)
    
    demos_scheduled = Column(Integer, default=0)
    demos_completed = Column(Integer, default=0)
    demos_no_show = Column(Integer, default=0)
    
    proposals_sent = Column(Integer, default=0)
    proposals_accepted = Column(Integer, default=0)
    proposals_rejected = Column(Integer, default=0)
    
    # Revenue tracking
    pipeline_value = Column(Integer, default=0)  # Total pipeline value in cents
    closed_deals = Column(Integer, default=0)
    revenue_generated = Column(Integer, default=0)  # Revenue in cents
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class TeamLeaderboard(Base):
    """Store weekly team leaderboard snapshots"""
    __tablename__ = "team_leaderboards"
    
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Performance metrics
    overall_percentage = Column(Integer, default=0)
    calls_percentage = Column(Integer, default=0)
    demos_percentage = Column(Integer, default=0)
    proposals_percentage = Column(Integer, default=0)
    
    # Rankings
    overall_rank = Column(Integer, nullable=True)
    calls_rank = Column(Integer, nullable=True)
    demos_rank = Column(Integer, nullable=True)
    proposals_rank = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User") 