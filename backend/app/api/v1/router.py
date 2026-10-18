from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.endpoints import auth, users, documents, analysis, admin, evaluation

api_router = APIRouter()


@api_router.get("/", tags=["API Info"])
def get_api_v1_info():
    """Returns v1 API status, version, and architecture information."""
    return {
        "status": "online",
        "api_version": "v1",
        "application": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "phase": "Phase 9 - Final Integration, Deployment, QA & Project Readiness",
        "architecture": "Three-Tier Enterprise Architecture (Presentation, Application, Data)",
        "security": "Stateless RFC 7519 JWT (HS256) + Argon2id Password Hashing + RBAC + Audit Ledger",
        "database_engine": "SQLAlchemy ORM + SQLite"
    }


# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(analysis.router, prefix="/analyses", tags=["Analysis"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["Evaluation"])
