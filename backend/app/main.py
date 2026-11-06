from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router

app = FastAPI(title=settings.app_name, version="1.0.0", description="Resume intelligence, explainable career matching and skill development API")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])
app.include_router(router)
@app.get("/health")
def health(): return {"status": "ok", "service": "skillbridge-api"}
