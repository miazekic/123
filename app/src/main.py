from fastapi import FastAPI, Request
from app.src.routers.provider import router as provider_router
from app.src.routers.auth import router as auth_router
from app.src.routers.user import router as user_router
from app.src.routers.patient import router as patient_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()


# API routers
app.include_router(provider_router, prefix="/api/provider")
app.include_router(auth_router)
app.include_router(user_router, prefix="/api/user")
app.include_router(patient_router, prefix="/api/patient")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/static")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
