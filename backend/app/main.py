from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (ensure models are registered before create_all)
from .config import settings
from .database import Base, engine
from .routers import chat, interactions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-First CRM — HCP Log Interaction")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "provider": "groq",
        "model": settings.model_name,
        "key_configured": bool(settings.groq_api_key),
    }
