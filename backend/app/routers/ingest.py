from fastapi import APIRouter, UploadFile, File, BackgroundTasks
import uuid
import os
import shutil

router = APIRouter(prefix="/api/ingest", tags=["Ingest"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

JOBS = {}

def process_file_job(job_id: str, file_path: str):
    # Simulated extraction pipeline
    JOBS[job_id]["status"] = "completed"
    JOBS[job_id]["extracted_count"] = 10
    JOBS[job_id]["preview"] = [
        {"sample": "Sample extracted question from assignment"}
    ]

@router.post("/upload")
async def upload_file(bg: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    JOBS[job_id] = {
        "job_id": job_id,
        "filename": file.filename,
        "status": "processing",
        "extracted_count": 0
    }

    bg.add_task(process_file_job, job_id, save_path)
    return {"job_id": job_id, "status": "processing", "filename": file.filename}

@router.get("/status/{job_id}")
def check_job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job
