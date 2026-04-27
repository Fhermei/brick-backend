from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.v1.router import router as v1_router
from src.db.session import Base, engine


def create_tables():
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS properly for all endpoints including reports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://brick-frontend-beige.vercel.app",
        "https://brick-frontend-1d3rb52bw-femis-projects-21e38439.vercel.app",
    ], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Cookie",
        "Authorization",
        "Accept",
        "X-Requested-With"
    ],
    expose_headers=["Set-Cookie"],
    max_age=3600,
)


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/")
def root():
    return {
        "message": "Welcome to Brick SPMES API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


app.include_router(v1_router, prefix="/api/v1")