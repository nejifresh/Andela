from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.api import router as api_router
from app.core.config import settings
from app.db.models import Base
from app.db.session import engine


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API-first FinOps MVP for evidence-backed cloud waste remediation recommendations.",
    version="0.1.0",
)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


app.include_router(api_router, prefix="/api")
