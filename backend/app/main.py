"""
FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, Base
from app.api.routes import reimbursement, employees, categories, balances

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Benefit Reimbursement Automation API",
    description="API for automated benefit reimbursement processing",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(reimbursement.router, prefix=settings.API_V1_PREFIX, tags=["reimbursement"])
app.include_router(employees.router, prefix=settings.API_V1_PREFIX, tags=["employees"])
app.include_router(categories.router, prefix=settings.API_V1_PREFIX, tags=["categories"])
app.include_router(balances.router, prefix=settings.API_V1_PREFIX, tags=["balances"])


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


# Serve static files (React build) - only in production
if settings.ENVIRONMENT == "production":
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve React app for all non-API routes."""
            # Don't serve API routes or static files
            if full_path.startswith("api") or full_path.startswith("static"):
                return {"error": "Not found"}
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"error": "Not found"}

