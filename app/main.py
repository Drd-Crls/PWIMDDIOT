from fastapi import FastAPI
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.enroll import router as enroll_router
from app.core.exception_handlers import EXCEPTION_HANDLERS

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Auth API",
    description="FastAPI application with JWT authentication",
    version="1.0.0",
)

for exception_class, exception_handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exception_class, exception_handler)

app.include_router(auth_router)
app.include_router(enroll_router)

@app.get("/", tags=["health"])
async def root():
    return {"message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
