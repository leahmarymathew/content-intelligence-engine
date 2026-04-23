import sys
from pathlib import Path

# Add parent directory to path to import ai_engine
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.rag_routes import router as rag_router
from app.routes.health import router as health_router
from app.routes.content_routes import router as content_router
from app.routes.webhook_routes import router as webhook_router
from app.routes.analytics_routes import router as analytics_router
from app.auth.auth_routes import router as auth_router
from app.core.database import Base, engine
from app.core.config import settings
from app.models import content_model, engagement_model
from app.utils.observability import add_request_context, configure_logging

Base.metadata.create_all(bind=engine)
configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered content generation and intelligence platform",
    version="1.0.0"
)

# Enable CORS with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_tracing_middleware(request, call_next):
    return await add_request_context(request, call_next)

app.include_router(health_router)
app.include_router(content_router)
app.include_router(webhook_router)
app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(rag_router)