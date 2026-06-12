from fastapi import FastAPI
from app.settings.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.enroll import router as enroll_router
from app.routes.contexts import router as contexts_router
from app.routes.devices import router as devices_router
from app.core.exception_handlers import EXCEPTION_HANDLERS
from app.middlewares.auth import AuthMiddleware


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="PWIMDDIOT API",
        description="IoT Device Management API",
        version="1.0.0",
    )

    for exception_class, exception_handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, exception_handler)

    app.add_middleware(AuthMiddleware)

    app.include_router(auth_router)
    app.include_router(enroll_router)
    app.include_router(contexts_router)
    app.include_router(devices_router)

    @app.get("/", tags=["health"])
    async def root():
        return {"message": "API is running"}

    return app


app = create_app()
