"""
FastAPI application entry point.
"""
import os
import mimetypes
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from starlette.responses import Response as StarletteResponse

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

# IMPORTANT: Mount static files BEFORE API routes to ensure proper MIME types
# StaticFiles mount has priority over regular routes
if settings.ENVIRONMENT == "production":
    static_dir = Path(os.path.dirname(__file__)).parent / "static"
    assets_dir = static_dir / "assets"
    
    if static_dir.exists() and assets_dir.exists():
        # Custom handler for assets with explicit MIME types
        @app.get("/assets/{file_path:path}")
        async def serve_asset(file_path: str):
            """Serve static assets with proper MIME types."""
            file_full_path = assets_dir / file_path
            
            # Security: prevent directory traversal
            try:
                file_full_path.resolve().relative_to(assets_dir.resolve())
            except ValueError:
                return Response(content="Not found", status_code=404)
            
            if not file_full_path.exists() or not file_full_path.is_file():
                return Response(content="Not found", status_code=404)
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(file_full_path))
            if not mime_type:
                # Fallback for common file types
                if file_path.endswith('.css'):
                    mime_type = 'text/css'
                elif file_path.endswith('.js'):
                    mime_type = 'application/javascript'
                elif file_path.endswith('.json'):
                    mime_type = 'application/json'
                else:
                    mime_type = 'application/octet-stream'
            
            return FileResponse(
                str(file_full_path),
                media_type=mime_type,
                headers={"Cache-Control": "public, max-age=31536000"}
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


# Serve index.html for SPA routing (must be registered LAST to catch all non-API routes)
# This route will NOT intercept /assets/* requests because mount has higher priority
if settings.ENVIRONMENT == "production":
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    
    if os.path.exists(static_dir):
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve React app for all non-API routes."""
            # Additional safety check (though mount should handle /assets already)
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
