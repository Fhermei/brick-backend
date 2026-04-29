from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from src.core.config import settings
from src.api.v1.router import router as v1_router

# Add logging to see the error
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - THIS MUST BE FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://brick-frontend-beige.vercel.app",
        "https://brick-frontend-git-main-femis-projects-21e38439.vercel.app",
        "https://brick-frontend-*.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)


@app.on_event("startup")
def on_startup():
    try:
        from src.db.session import Base, engine
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("Continuing without database - check DATABASE_URL")
    
    # Log Redis status
    if settings.REDIS_URL:
        logger.info(f"Redis configured")
    else:
        logger.info("Redis not configured - continuing without Redis")


@app.get("/")
def root():
    return {
        "message": "Welcome to Brick SPMES API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "environment": "production" if not settings.DEBUG else "development"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "port": os.getenv("PORT", "10000"),
        "redis_enabled": bool(settings.REDIS_URL),
        "database_configured": bool(settings.DATABASE_URL)
    }


# CRITICAL FIX: Handle OPTIONS requests for all paths
@app.api_route("/{path:path}", methods=["OPTIONS"])
async def options_handler(request: Request, path: str):
    """Handle CORS preflight requests for all paths"""
    response = Response(status_code=200)
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


# Also handle OPTIONS for the specific API v1 paths
@app.api_route("/api/v1/{path:path}", methods=["OPTIONS"])
async def options_api_handler(request: Request, path: str):
    """Handle CORS preflight requests for API v1 paths"""
    response = Response(status_code=200)
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=200)


app.include_router(v1_router, prefix="/api/v1")


# This is critical for Render - use the PORT environment variable
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)