from fastapi import FastAPI
from app.settings.database import Base, engine
from app.core.logging import configure_logging
from app.routes.auth import router as auth_router
from app.routes.enroll import router as enroll_router
from app.routes.contexts import router as contexts_router
from app.routes.devices import router as devices_router
from app.routes.sensors import router as sensors_router
from app.routes.ingests import router as ingests_router
from app.routes.api_keys import router as api_keys_router
from app.core.exception_handlers import EXCEPTION_HANDLERS
from app.middlewares.auth import AuthMiddleware
from app.middlewares.api_key_auth import ApiKeyAuthMiddleware


def create_app() -> FastAPI:
    configure_logging()

    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="PWIMDDIOT API",
        description="IoT Device Management API",
        version="1.0.0",
    )

    for exception_class, exception_handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, exception_handler)

    app.add_middleware(AuthMiddleware)
    app.add_middleware(ApiKeyAuthMiddleware)

    app.include_router(auth_router)
    app.include_router(enroll_router)
    app.include_router(contexts_router)
    app.include_router(devices_router)
    app.include_router(sensors_router)
    app.include_router(ingests_router)
    app.include_router(api_keys_router)

    @app.get("/", tags=["health"])
    async def root():
        return {"message": "API is running"}

    return app


app = create_app()
