from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.auth_routes import router as auth_router
from app.routes.me_routes import router as me_router
from app.routes.model_routes import router as model_router
from app.routes.thread_routes import router as thread_router
from app.routes.chat_routes import router as chat_router
from app.routes.admin_routes import router as admin_router

app = FastAPI(
    title="in spirit truth-api",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_base_url, "http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(me_router, tags=["me"])
app.include_router(model_router, prefix="/models", tags=["models"])
app.include_router(thread_router, prefix="/threads", tags=["threads"])
app.include_router(chat_router, tags=["chat"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "truth-api"}
