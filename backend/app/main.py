from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.dependencies import get_persona_service
from .api.routes import router
from .config import get_settings
from .database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    get_persona_service().seed_defaults()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(router, prefix=settings.api_prefix)
