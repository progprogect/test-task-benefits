"""
FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from app.config import settings
from app.database import engine, Base
from app.api.routes import reimbursement, employees, categories, balances

# Create database tables (only in development - use migrations in production)
# In production, tables should be created via Alembic migrations
if settings.ENVIRONMENT == "development":
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
    assets_dir = os.path.join(static_dir, "assets")
    
    if os.path.exists(static_dir):
        # Mount assets directory for JS, CSS, and other static files with proper MIME types
        if os.path.exists(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir, html=False), name="assets")
        
        # Serve index.html for all non-API, non-asset routes (SPA routing)
        # Note: This route is registered AFTER the mount, so /assets requests are handled by StaticFiles first
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve React app for all non-API routes."""
            # Don't serve API routes or asset routes
            if full_path.startswith("api") or full_path.startswith("assets"):
                return Response(content="Not found", status_code=404)
            
            # Serve index.html for SPA routing
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(
                    index_path,
                    media_type="text/html",
                    headers={"Cache-Control": "no-cache"}
                )
            return Response(content="Not found", status_code=404)

