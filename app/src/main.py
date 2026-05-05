from fastapi import FastAPI
from app.src.routers.provider import router as provider_router
from app.src.routers.auth import router as auth_router

app = FastAPI()

app.include_router(provider_router, prefix="/api/provider")
app.include_router(auth_router)
