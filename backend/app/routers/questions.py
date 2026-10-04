from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
import os
from ..schemas import QuestionSchema

router = APIRouter(prefix="/api/questions", tags=["Questions"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seed_questions.json")

def load_all_questions() -> List[dict]:
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.get("", response_model=List[dict])
def get_questions(
    course: Optional[str] = None,
    week: Optional[int] = None,
    topic: Optional[str] = None,
    q_type: Optional[str] = None
):
    questions = load_all_questions()
    filtered = []
    for q in questions:
        if course and course != "ALL" and q.get("course") != course:
            continue
        if week and q.get("week") != week:
            continue
        if topic and topic != "ALL" and q.get("topic") != topic:
            continue
        if q_type and q_type != "ALL" and q.get("type") != q_type:
            continue
        filtered.append(q)
    return filtered

@router.get("/{qid}")
def get_question_by_id(qid: str):
    questions = load_all_questions()
    for q in questions:
        if q.get("id") == qid:
            return q
    raise HTTPException(status_code=404, detail="Question not found")

@router.post("/{qid}/variant")
def get_variant_by_id(qid: str):
    from ..services.variant_generator import generate_question_variant
    questions = load_all_questions()
    for q in questions:
        if q.get("id") == qid:
            return generate_question_variant(q)
    raise HTTPException(status_code=404, detail="Question not found")

