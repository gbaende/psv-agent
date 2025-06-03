# DealTracker - Full Stack Project & Goal Management System

A comprehensive project and goal management system built with FastAPI (backend) and React (frontend), featuring Kanban boards, goal tracking, Slack integration, and AI-powered NLP parsing.

## 🚀 Features

### Backend (FastAPI)

- **REST API**: Full CRUD operations for users, projects, tasks, and goals
- **Database**: PostgreSQL with async SQLAlchemy
- **Scheduler**: APScheduler for Monday/Wednesday/Friday check-ins
- **Slack Integration**: Send/receive messages via Slack Web API
- **AI/NLP**: LangChain integration for natural language parsing
- **Memory**: FAISS vector store for conversation memory
- **Authentication**: Ready for JWT/OAuth integration

### Frontend (React)

- **Dashboard**: Modern, responsive UI with Tailwind CSS
- **Kanban Board**: Drag-and-drop task management
- **Goal Charts**: Interactive progress visualization with Recharts
- **Project Management**: Create, edit, and manage projects
- **Real-time Updates**: Connected to FastAPI backend

### Deployment

- **Docker**: Containerized backend and frontend
- **Nginx**: Reverse proxy for routing
- **Docker Compose**: Orchestrated multi-service deployment

## 🛠 Tech Stack

### Backend

- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- APScheduler
- Slack SDK
- LangChain
- FAISS
- Uvicorn

### Frontend

- React 18+
- Tailwind CSS
- Axios
- Recharts
- Modern JavaScript (ES6+)

### Infrastructure

- Docker & Docker Compose
- Nginx
- PostgreSQL 13+

## 📦 Installation & Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

### Quick Start with Docker

1. **Clone the repository**

   ```bash
   git clone <your-repo>
   cd DealTracker
   ```

2. **Configure environment variables**

   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   # Edit backend/.env with your credentials:
   # - DATABASE_URL
   # - SLACK_TOKEN
   # - OPENAI_API_KEY
   ```

3. **Start all services**

   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost (via Nginx)
   - Backend API: http://localhost/api
   - Direct Frontend: http://localhost:3000
   - Direct Backend: http://localhost:8000

### Local Development

#### Frontend Development

```bash
cd frontend
npm install
npm start
# Runs on http://localhost:3000
```

#### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

## 🎯 Usage

### 1. Project Management

- Create new projects with descriptions
- Edit existing projects
- Delete projects
- View project details

### 2. Task Management (Kanban)

- Create tasks within projects
- Move tasks between columns (To Do → In Progress → Done)
- Edit task details
- Track task completion

### 3. Goal Tracking

- Set weekly goals for projects
- Track goal achievement
- View progress charts and analytics
- Mark goals as completed

### 4. Dashboard Navigation

- **Projects Tab**: Manage all projects
- **Tasks Tab**: Kanban board for selected project
- **Goals Tab**: Goal tracking and charts for selected project

## 🔧 API Endpoints

### Users

- `POST /users/` - Create user
- `GET /users/{user_id}` - Get user by ID

### Projects

- `POST /projects/?owner_id={id}` - Create project
- `GET /projects/{project_id}` - Get project by ID

### Tasks

- `POST /tasks/?project_id={id}` - Create task
- `GET /tasks/{task_id}` - Get task by ID

### Goals

- `POST /goals/?project_id={id}` - Create goal
- `GET /goals/{goal_id}` - Get goal by ID

## 🔮 Advanced Features (Planned/Expandable)

### Slack Integration

- Automated check-in messages (M/W/F)
- Goal setting reminders
- Progress notifications
- Team collaboration

### AI/NLP Features

- Natural language task creation
- Goal parsing from text
- Smart project suggestions
- Automated progress insights

### Memory & Analytics

- Conversation history with FAISS
- Advanced analytics dashboard
- Predictive goal completion
- Performance insights

## 🚀 Deployment

### Production Deployment

1. **Set up your server** (Ubuntu/CentOS)
2. **Install Docker and Docker Compose**
3. **Clone the repository**
4. **Configure production environment variables**
5. **Set up SSL with Let's Encrypt** (optional)
6. **Deploy with Docker Compose**

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

#### Backend (.env)

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/dealtracker
SLACK_TOKEN=xoxb-your-slack-bot-token
OPENAI_API_KEY=sk-your-openai-api-key
```

#### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost/api
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📝 Development Notes

### Current Status

- ✅ Backend API scaffolded with CRUD endpoints
- ✅ Frontend dashboard with all major components
- ✅ Docker containerization complete
- ✅ Nginx reverse proxy configured
- 🔄 Database integration (ready for connection)
- 🔄 Slack integration (API ready, needs tokens)
- 🔄 AI/NLP features (framework ready)

### Next Steps

1. Connect frontend to live backend API
2. Implement user authentication
3. Add real-time updates with WebSockets
4. Integrate Slack bot functionality
5. Implement AI-powered features
6. Add comprehensive testing
7. Set up CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed description

---

**Built with ❤️ using FastAPI + React + Docker**
