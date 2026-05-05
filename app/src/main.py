from fastapi import FastAPI
from app.src.routers.provider import router as provider_router

app = FastAPI()

app.include_router(provider_router, prefix="/api/provider")
