from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, check_db_connection
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager ensuring database schema exists upon startup.
    Also ensures default demonstration accounts and sample data are seeded.
    """
    # Initialize database tables
    init_db()
    try:
        from scripts.init_db import seed_database
        seed_database()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning(f"Startup database seed skipped/failed: {exc}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Set up CORS middleware for presentation tier
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https://.*\.onrender\.com$|^https://.*\.vercel\.app$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint welcoming clients and confirming application state."""
    return {
        "application": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "status": "running",
        "health_check": "/health",
        "api_v1": settings.API_V1_STR,
        "documentation": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Operational health probe reporting application and database connectivity."""
    db_connected = check_db_connection()
    return {
        "status": "healthy" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "application": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }


# Include v1 central router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
