from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from app.database import engine
from app.models import Base
from app.api import auth, projects, tasks, sales
from app.api.slack_events import router as slack_events_router
from app.services.scheduler import sales_scheduler
from app.services.auto_sync_users import auto_sync_service

# Add get_database_url function to database.py
def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:password@db:5432/dealtracker')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting DealTracker Sales Agent...")
    
    # Create database tables
    print("🗄️ Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Database table creation error: {e}")
    
    # Start the sales scheduler
    sales_scheduler.start()
    print("✅ Sales scheduler started")
    
    # Auto-sync users from Slack channel
    print("🔄 Auto-syncing users from Slack channel...")
    try:
        sync_result = await auto_sync_service.sync_all_users()
        if sync_result["success"]:
            print(f"✅ Auto-sync completed: {sync_result['created']} created, {sync_result['updated']} updated")
        else:
            print(f"⚠️ Auto-sync failed: {sync_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Auto-sync error: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down DealTracker Sales Agent...")
    sales_scheduler.stop()
    print("✅ Sales scheduler stopped")

app = FastAPI(
    title="DealTracker Sales Agent",
    description="An autonomous AI-powered sales project manager",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(slack_events_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check scheduler status
        scheduler_status = "running" if sales_scheduler.scheduler.running else "stopped"
        job_count = len(sales_scheduler.get_job_status())
        
        return {
            "status": "healthy",
            "message": "DealTracker Sales Agent is running",
            "scheduler": {
                "status": scheduler_status,
                "jobs": job_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}"
        }

# Serve React app if build directory exists
frontend_build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "build")

if os.path.exists(frontend_build_path):
    # Serve static files
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build_path, "static")), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for client-side routing"""
        if full_path.startswith("api/"):
            # Let API routes handle themselves
            return {"error": "API endpoint not found"}
        
        # Serve index.html for all other routes (client-side routing)
        return FileResponse(os.path.join(frontend_build_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 