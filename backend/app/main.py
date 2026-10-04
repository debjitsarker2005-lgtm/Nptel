from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routers import questions, exam, answer_finder, analytics, ingest

app = FastAPI(
    title="SmartExam AI — NPTEL Practice & Exam Platform",
    description="Backend API for NPTEL exam simulations, answer auditing, and question management.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(questions.router)
app.include_router(exam.router)
app.include_router(answer_finder.router)
app.include_router(analytics.router)
app.include_router(ingest.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "SmartExam AI", "version": "1.0.0"}

# Mount Frontend Static Assets
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

