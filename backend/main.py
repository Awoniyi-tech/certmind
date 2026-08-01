import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from database.db import init_db
from routers import questions, exam, analytics, rag, dumps, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="CertMind API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000",
                   os.getenv("FRONTEND_URL", "")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(questions.router,  prefix="/api/questions", tags=["questions"])
app.include_router(exam.router,       prefix="/api/exam",      tags=["exam"])
app.include_router(analytics.router,  prefix="/api/analytics", tags=["analytics"])
app.include_router(rag.router,        prefix="/api/rag",       tags=["rag"])
app.include_router(dumps.router,      prefix="/api/dumps",     tags=["dumps"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
