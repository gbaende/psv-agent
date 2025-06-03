# DealTracker - Autonomous Sales Project Manager 🤖

DealTracker has been transformed into a comprehensive autonomous sales project manager powered by AI. The system features an intelligent sales agent called **SalesPM** that proactively manages your sales team through automated coaching, goal setting, progress tracking, and team engagement.

## 🚀 Key Features

### Autonomous AI Sales Agent

- **Proactive Goal Setting**: Weekly goal-setting prompts sent automatically to team members
- **Smart Progress Tracking**: Real-time monitoring of sales activities and goal achievement
- **Personalized Coaching**: AI-generated coaching tips based on individual performance
- **Automated Celebrations**: Milestone achievements are automatically recognized and celebrated
- **Team Leaderboards**: Dynamic rankings to foster healthy competition

### Intelligent Scheduling System

- **Monday Morning Goals**: Automated weekly goal-setting prompts
- **Wednesday Check-ins**: Mid-week progress nudges and coaching
- **Friday Summaries**: Comprehensive weekly performance reviews
- **Achievement Celebrations**: Instant recognition of milestones
- **Team Updates**: Regular leaderboard and team progress updates

### Modern Dashboard

- **Real-time Analytics**: Live team progress and performance metrics
- **Interactive Leaderboards**: Dynamic rankings with achievement badges
- **AI Automation Control**: Manual trigger controls for all automated tasks
- **Performance Insights**: Detailed analytics and trend visualization

### Slack Integration

- **Seamless Communication**: All interactions happen directly in Slack
- **Smart Notifications**: Context-aware messages and updates
- **Team Engagement**: Automated team-wide updates and celebrations

## 🛠️ Technology Stack

### Backend

- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Robust database with advanced sales tracking schema
- **APScheduler**: Intelligent job scheduling for autonomous operations
- **OpenAI GPT**: AI-powered content generation and analysis
- **Slack SDK**: Deep Slack workspace integration

### Frontend

- **React**: Modern, responsive user interface
- **Tailwind CSS**: Beautiful, utility-first styling
- **Lucide Icons**: Clean, professional iconography
- **Real-time Updates**: Live dashboard with automatic refresh

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- OpenAI API key
- Slack workspace with bot permissions

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd DealTracker
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run build
```

### 4. Database Setup

```bash
cd backend
# Create database and run migrations
alembic upgrade head
```

### 5. Environment Configuration

Edit `backend/.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/dealtracker

# OpenAI (for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Slack (for team integration)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_CHANNEL_ID=your-sales-channel-id

# Security
SECRET_KEY=your-secure-secret-key
```

### 6. Start the Application

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` to access the dashboard.

## 🤖 AI Agent Behaviors

### Weekly Cycle

1. **Monday 9:00 AM**: Goal-setting prompts sent to all team members
2. **Wednesday 2:00 PM**: Mid-week check-ins and coaching tips
3. **Friday 5:00 PM**: Weekly performance summaries and celebrations
4. **Daily**: Continuous monitoring for milestone achievements

### Smart Interactions

- **Goal Analysis**: AI parses natural language goals into structured data
- **Performance Coaching**: Personalized tips based on individual metrics
- **Achievement Recognition**: Automatic celebration of milestones
- **Team Dynamics**: Leaderboard updates and team motivation

## 📊 Dashboard Features

### Team Progress Tab

- Real-time team performance overview
- Individual goal tracking and progress bars
- Performance color coding and status indicators
- Quick stats and team metrics

### Leaderboard Tab

- Dynamic rankings with achievement badges
- Performance percentages and goal completion
- Competitive elements to drive engagement
- Historical performance tracking

### AI Automation Tab

- Manual trigger controls for all automated tasks
- Scheduler status and job monitoring
- Real-time automation health checks
- Emergency override capabilities

### Analytics Tab

- Comprehensive performance insights
- Trend analysis and forecasting
- Team and individual metrics
- Export capabilities for reporting

## 🔧 Configuration

### Slack Setup

1. Create a Slack app in your workspace
2. Add bot permissions: `chat:write`, `users:read`, `channels:read`
3. Install the app to your workspace
4. Copy the bot token to your `.env` file

### OpenAI Setup

1. Create an OpenAI account
2. Generate an API key
3. Add the key to your `.env` file
4. Ensure sufficient credits for AI operations

### Database Schema

The system includes comprehensive tables for:

- User management and authentication
- Sales goals and progress tracking
- AI interaction history
- Performance metrics and rankings
- Automated task scheduling

## 🚀 Deployment

### Production Deployment

1. Set up a PostgreSQL database
2. Configure environment variables
3. Deploy backend to your preferred platform (Heroku, AWS, etc.)
4. Serve frontend build files
5. Configure Slack webhook endpoints

### Environment Variables

Ensure all required environment variables are set:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `SLACK_BOT_TOKEN`: Slack bot token for integrations
- `SECRET_KEY`: Secure secret for JWT tokens

## 📈 Monitoring

### Health Checks

- `/api/health`: Application and scheduler status
- Real-time dashboard updates every 30 seconds
- Automatic error handling and fallbacks
- Comprehensive logging for troubleshooting

### Performance Metrics

- AI response times and success rates
- Slack integration health
- Database performance monitoring
- User engagement analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Check the documentation
- Review the health check endpoint
- Examine application logs
- Contact the development team

---

**DealTracker** - Transforming sales management through autonomous AI-powered project management. 🚀
