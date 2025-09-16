from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, engine
from app.api.v1.health import router as health_router
from app.api.v1.interviews import router as interviews_router


def create_app() -> FastAPI:
    application = FastAPI(title=settings.PROJECT_NAME)

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    application.include_router(health_router, tags=["health"])
    application.include_router(interviews_router, prefix=settings.API_V1_STR, tags=["interviews"])

    return application


app = create_app()

# Create tables on startup for initial development convenience
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine) 