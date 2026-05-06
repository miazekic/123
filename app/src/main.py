from fastapi import FastAPI
from app.src.routers.provider import router as provider_router
from app.src.routers.auth import router as auth_router
from app.src.routers.user import router as user_router
from app.src.routers.patient import router as patient_router

app = FastAPI()

app.include_router(provider_router, prefix="/api/provider")
app.include_router(auth_router)
app.include_router(user_router, prefix="/api/user")
app.include_router(patient_router, prefix="/api/patient")
