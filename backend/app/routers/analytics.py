from fastapi import APIRouter
import json
import os
from collections import defaultdict

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seed_questions.json")

def load_questions():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.get("/summary")
def get_analytics_summary():
    questions = load_questions()
    topic_distribution = defaultdict(int)
    course_distribution = defaultdict(int)
    type_distribution = defaultdict(int)

    for q in questions:
        topic_distribution[q.get("topic", "General")] += 1
        course_distribution[q.get("course", "Unknown")] += 1
        type_distribution[q.get("type", "MCQ")] += 1

    return {
        "total_questions": len(questions),
        "courses": dict(course_distribution),
        "question_types": dict(type_distribution),
        "top_topics": sorted(
            [{"topic": k, "count": v} for k, v in topic_distribution.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]
    }
