import json
import os
from .db import engine, Base, SessionLocal
from .models import QuestionModel, ExamAttemptModel, ExamResponseModel, LeitnerQueueModel

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_questions.json")

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        count = db.query(QuestionModel).count()
        if count == 0 and os.path.exists(DATA_PATH):
            print(f"Seeding questions from {DATA_PATH} into SQLite...")
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                questions = json.load(f)

            for q in questions:
                num_ans = q.get("numeric_answer") or {}
                q_model = QuestionModel(
                    id=q["id"],
                    course=q.get("course", "General"),
                    week=q.get("week", 1),
                    source=q.get("source"),
                    type=q.get("type", "MCQ"),
                    topic=q.get("topic", "General"),
                    difficulty=q.get("difficulty", "medium"),
                    marks=q.get("marks", 1.0),
                    negative_marks=q.get("negative_marks", 0.0),
                    text=q["text"],
                    options_json=json.dumps(q.get("options", []), ensure_ascii=False),
                    correct_json=json.dumps(q.get("correct", []), ensure_ascii=False),
                    numeric_value=num_ans.get("value"),
                    tolerance=num_ans.get("tolerance", 0.0),
                    explanation=q.get("explanation", ""),
                    image=q.get("image"),
                    answer_meta_json=json.dumps(q.get("answer_meta", {}), ensure_ascii=False)
                )
                db.add(q_model)
            db.commit()
            print(f"Successfully seeded {len(questions)} questions into SQLite database.")
        else:
            print(f"Database already contains {count} questions.")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
