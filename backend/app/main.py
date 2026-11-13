from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.telemetry import setup_telemetry
from app.router import auth, org, sql_lab


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="SQL Lab API", version="1.0.0", lifespan=lifespan)
setup_telemetry("sql-lab-api", app)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])

API = "/api/v1"
app.include_router(auth.router, prefix=API)
app.include_router(org.router, prefix=API)
app.include_router(sql_lab.router, prefix=API)


@app.get("/health", tags=["ops"])
def health():
    return {"status": "ok"}
