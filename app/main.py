from fastapi import FastAPI
from app.database import Base, engine
from app.controllers.auth_controller import router as auth_router

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Auth API",
    description="FastAPI application with JWT authentication",
    version="1.0.0",
)

# Incluir rotas
app.include_router(auth_router)


@app.get("/", tags=["health"])
async def root():
    return {"message": "FastAPI Auth API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
