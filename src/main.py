from fastapi import FastAPI, Response
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

# CORS configuration for Render and Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://brick-frontend-beige.vercel.app",
        "https://brick-frontend-git-main-femis-projects-21e38439.vercel.app",
        "https://brick-frontend-*.vercel.app",
        "https://brick-backend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie", "Cookie"],
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


@app.get("/")
def root():
    return {
        "message": "Welcome to Brick SPMES API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "port": os.getenv("PORT", "10000")}


@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return Response(status_code=200)


app.include_router(v1_router, prefix="/api/v1")

# This is important for Render - make sure the app is properly configured
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)