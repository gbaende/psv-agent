from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from app.database import engine
from app.models import Base
from app.api import auth, projects, tasks, sales
from app.services.scheduler import sales_scheduler

# Add get_database_url function to database.py
def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:password@db:5432/dealtracker')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting DealTracker Sales Agent...")
    
    # Start the sales scheduler
    try:
        sales_scheduler.start()
        print("✅ Sales scheduler started successfully")
    except Exception as e:
        print(f"⚠️ Failed to start sales scheduler: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down DealTracker Sales Agent...")
    try:
        sales_scheduler.stop()
        print("✅ Sales scheduler stopped successfully")
    except Exception as e:
        print(f"⚠️ Error stopping sales scheduler: {e}")

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
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])

@app.get("/api/health")
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