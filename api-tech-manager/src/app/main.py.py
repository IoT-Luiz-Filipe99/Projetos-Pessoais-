from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.db import init_db
from .routers import auth, technicians, clients, orders, files

app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static (uploads locais)
if settings.UPLOAD_BACKEND == "local":
    app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR, html=False), name="static")

# Routers
app.include_router(auth.router)
app.include_router(technicians.router)
app.include_router(clients.router)
app.include_router(orders.router)
app.include_router(files.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"name": settings.APP_NAME, "env": settings.APP_ENV, "status": "ok"}
