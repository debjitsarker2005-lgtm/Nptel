from fastapi import APIRouter, HTTPException
import json
import os
from ..services.answer_engine import run_consensus_verification

router = APIRouter(prefix="/api/answer-finder", tags=["Answer Finder"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seed_questions.json")

def load_questions():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.post("/verify/{qid}")
async def verify_question(qid: str):
    questions = load_questions()
    for q in questions:
        if q["id"] == qid:
            result = await run_consensus_verification(q)
            return result
    raise HTTPException(status_code=404, detail="Question not found")

@router.get("/audit-report")
def get_audit_report():
    questions = load_questions()
    flagged = []
    for q in questions:
        meta = q.get("answer_meta") or {}
        if meta.get("status") in ["CONFLICT", "UNSURE"]:
            flagged.append({
                "id": q["id"],
                "course": q["course"],
                "week": q["week"],
                "topic": q["topic"],
                "text": q["text"],
                "stored_key": q.get("correct") or q.get("numeric_answer", {}).get("value"),
                "status": meta.get("status"),
                "confidence": meta.get("confidence"),
                "explanation": q.get("explanation")
            })
    return {"flagged_count": len(flagged), "items": flagged}
