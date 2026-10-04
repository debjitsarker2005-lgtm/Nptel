from fastapi import APIRouter, HTTPException
import uuid
import random
import os
import json
from ..schemas import ExamConfigSchema, ExamSubmitSchema
from ..services.grader import grade_question

router = APIRouter(prefix="/api/exam", tags=["Exam"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seed_questions.json")

def load_questions():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# In-memory session tracking
ACTIVE_SESSIONS = {}

@router.post("/start")
def start_exam(config: ExamConfigSchema):
    all_q = load_questions()
    pool = []
    for q in all_q:
        if config.course and config.course != "ALL" and q.get("course") != config.course:
            continue
        if config.week and config.week != "ALL" and str(q.get("week")) != str(config.week):
            continue
        pool.append(q)

    if not pool:
        raise HTTPException(status_code=400, detail="No questions matched the criteria.")

    if config.shuffle:
        random.shuffle(pool)

    if config.count and config.count < len(pool):
        pool = pool[:config.count]

    session_id = str(uuid.uuid4())
    # Omit correct answers for secure exam delivery
    exam_questions = []
    for q in pool:
        q_copy = dict(q)
        if config.mode == "EXAM":
            q_copy.pop("correct", None)
            q_copy.pop("numeric_answer", None)
            q_copy.pop("explanation", None)
        exam_questions.append(q_copy)

    ACTIVE_SESSIONS[session_id] = {
        "questions": pool,
        "config": config.dict()
    }

    return {
        "attempt_id": session_id,
        "total_questions": len(exam_questions),
        "duration_minutes": len(exam_questions) * 1.5,
        "questions": exam_questions
    }

@router.post("/{attempt_id}/submit")
def submit_exam(attempt_id: str, submission: ExamSubmitSchema):
    session = ACTIVE_SESSIONS.get(attempt_id)
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found or expired.")

    questions = session["questions"]
    q_map = {q["id"]: q for q in questions}

    total_score = 0.0
    max_score = 0.0
    correct_count = 0
    wrong_count = 0
    results = []

    sub_map = {r.qid: r.selected for r in submission.responses}

    for q in questions:
        qid = q["id"]
        marks = q.get("marks", 1.0)
        max_score += marks
        user_choice = sub_map.get(qid)

        eval_res = grade_question(q, user_choice)
        total_score += eval_res["marks_awarded"]

        if eval_res["is_correct"]:
            correct_count += 1
        elif user_choice is not None:
            wrong_count += 1

        results.append({
            "qid": qid,
            "user_choice": user_choice,
            "correct_answer": q.get("correct") or q.get("numeric_answer", {}).get("value"),
            "is_correct": eval_res["is_correct"],
            "marks_awarded": eval_res["marks_awarded"],
            "explanation": q.get("explanation")
        })

    accuracy = round((correct_count / max(1, correct_count + wrong_count)) * 100, 1)

    return {
        "attempt_id": attempt_id,
        "total_score": max(0.0, round(total_score, 2)),
        "max_score": max_score,
        "accuracy_percentage": accuracy,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "unattempted_count": len(questions) - (correct_count + wrong_count),
        "breakdown": results
    }
