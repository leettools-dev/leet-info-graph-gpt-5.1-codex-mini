"""FastAPI application factory for the Infograph service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infograph.svc.api.v1.api import ServiceAPIRouter


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Infograph Service",
        description="Research Infograph Assistant backend API",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/v1/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    api_router = ServiceAPIRouter()
    app.include_router(api_router, prefix="/api/v1")

    return app
