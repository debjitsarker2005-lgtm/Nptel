# 🎓 SmartExam — AI-Powered Practice Exam System

An NPTEL-style exam / practice platform (MCQ, MSQ, Numerical) built from your ML + OOSD assignments.
**Upload any PDF/DOCX → the system extracts questions → finds & verifies answers from the web + AI → turns them into a live exam.**

---

## 1. Goals

| # | Goal |
|---|------|
| 1 | Reproduce the NPTEL "Week N : Assignment N" exam look & feel (timer, question palette, marks, submit). |
| 2 | Pre-load questions from your existing assignments (ML Assignments 2–8, OOSD quiz HTML). |
| 3 | **Answer Finder:** for every question, search the browser (web), collect sources, and compute a consensus answer with explanation. |
| 4 | **PDF Ingestion:** upload any PDF/DOCX → auto-parse into new questions → added to the question bank. |
| 5 | Analytics: weak topics, time per question, score history. |

> 💡 **Recommended use:** Practice / self-study mode. The Answer Finder acts as an *explainer + answer verifier* (shows reasoning and sources) so you learn, and can also validate answer keys that may contain mistakes (see Section 11).

---

## 2. Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | **React + Vite + Tailwind** | Fast, easy exam UI |
| Backend | **FastAPI (Python)** | Best PDF/ML libraries |
| DB | **SQLite** (start) → PostgreSQL | Simple |
| PDF/DOCX parsing | `pdfplumber`, `PyMuPDF`, `python-docx`, `pytesseract` (OCR for scanned/image PDFs) | Your PDFs contain images |
| Web search | **Tavily / SerpAPI / Brave Search API** | Programmatic "browser" |
| AI | **Claude API** (`claude-sonnet-5-5`) | Question extraction, answer reasoning, explanations |
| Math rendering | **KaTeX** | Formulas like `TP/(TP+FN)` |
| Auth (optional) | JWT | Multi-user |

---

## 3. System Architecture

```
┌──────────────┐     ┌────────────────────────── FastAPI ───────────────────────────┐
│  React UI    │◄───►│  /exam   /questions   /ingest   /answer-finder   /analytics   │
│ (Exam, Admin)│     └───────┬───────────┬──────────────┬──────────────┬─────────────┘
└──────────────┘             │           │              │              │
                         ┌───▼───┐  ┌────▼─────┐  ┌─────▼──────┐  ┌────▼──────────┐
                         │  DB   │  │ Question │  │ PDF Parser │  │ Answer Finder │
                         │SQLite │  │  Bank    │  │ + OCR + LLM│  │ Web + LLM     │
                         └───────┘  └──────────┘  └────────────┘  └───────────────┘
```

### Answer Finder pipeline
```
Question → Query Builder (LLM) → Web Search (top 8) → Fetch & clean pages
        → LLM reads snippets + solves independently → Consensus voting
        → Final answer + confidence + explanation + source links
```

### PDF Ingestion pipeline
```
Upload PDF/DOCX → Text extract (OCR fallback) → Page images (for diagrams/tables)
 → LLM structured extraction (JSON) → Validation → Dedupe → Topic tagging
 → Answer Finder (auto) → Admin review → Added to question bank
```

---

## 4. Folder Structure

```
smartexam/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── exam.py
│   │   │   ├── questions.py
│   │   │   ├── ingest.py
│   │   │   ├── answer_finder.py
│   │   │   └── analytics.py
│   │   └── services/
│   │       ├── pdf_parser.py
│   │       ├── question_extractor.py
│   │       ├── web_search.py
│   │       ├── answer_engine.py
│   │       ├── grader.py
│   │       └── topic_tagger.py
│   ├── data/
│   │   ├── seed_questions.json      # from your assignments
│   │   └── uploads/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/ (Home, ExamPage, Result, Upload, Admin, Analytics)
│   │   ├── components/ (QuestionCard, Palette, Timer, MathText, SourceList)
│   │   └── api.js
│   └── package.json
├── scripts/seed_from_assignments.py
└── README.md
```

---

## 5. Data Model

### Question JSON schema
```json
{
  "id": "ml-a8-q4",
  "source": "Assignment_8_ML.pdf",
  "course": "ML",
  "week": 8,
  "type": "MCQ | MSQ | NUMERIC | TRUE_FALSE",
  "topic": "Naive Bayes",
  "difficulty": "easy | medium | hard",
  "marks": 1,
  "negative_marks": 0,
  "text": "Y is Boolean, X1 is categorical (3 values), X2 is Gaussian. Number of parameters?",
  "options": [{"key":"A","text":"..."}],
  "correct": ["A"],
  "numeric_answer": { "value": 9, "tolerance": 0 },
  "explanation": "1 prior + 2x2 categorical + 2x2 Gaussian = 9",
  "image": "data/uploads/q4.png",
  "answer_meta": {
    "key_source": "assignment_pdf",
    "web_verified": true,
    "confidence": 0.92,
    "sources": ["https://..."]
  }
}
```

### SQL tables
```sql
users(id, name, email, password_hash)
courses(id, name)
questions(id, course_id, week, type, topic, difficulty, marks, negative_marks,
          text, options_json, correct_json, numeric_value, tolerance, explanation,
          image_path, source_file, created_at)
answer_checks(id, question_id, final_answer, confidence, status, explanation, sources_json, checked_at)
exams(id, title, course_id, duration_min, config_json)
attempts(id, user_id, exam_id, started_at, submitted_at, score, max_score)
responses(id, attempt_id, question_id, selected_json, time_spent_sec, is_correct, marks_awarded)
uploads(id, filename, status, num_questions, created_at)
```

---

## 6. Core Features

### 6.1 Exam Engine
- Exam modes: **Full Week Assignment**, **Topic Practice**, **Random Mix**, **Mock Test**, **Wrong-Answers Retry**
- Timer + auto-submit, question palette (answered / marked / not visited), mark for review
- MCQ (single), MSQ (multiple), Numeric (with tolerance), True/False
- Partial marking for MSQ + negative marking (configurable)
- Shuffle questions/options
- Result page: score, per-question review, correct answer, explanation, sources

### 6.2 🔍 Answer Finder (browser-based)
- Button **"Find answer"** on each question, plus a **bulk** job for the whole bank
- Steps: build search queries → search web → read top pages → LLM solves independently → compare with stored key
- Output: `final answer`, `confidence`, `explanation`, `source links`, **status**:
  - ✅ `MATCH` – web/AI agrees with answer key
  - ⚠️ `CONFLICT` – disagrees (flag for your review — answer keys do contain mistakes!)
  - ❓ `UNSURE` – low confidence
- Calculation questions (e.g. Recall = 6/9) are verified with a **Python sandbox** instead of web search

### 6.3 📄 PDF/DOCX Ingestion
- Drag & drop any assignment PDF/DOCX/HTML
- OCR fallback for screenshot-style PDFs (like your Week 2 screenshots)
- LLM extracts: question text, options, type, selected/correct answer if present, marks
- Extracts tables/diagrams as images attached to the question
- Preview screen → edit → approve → inserted in bank
- Duplicate detection via embedding similarity

### 6.4 Advanced Add-ons
| Feature | Description |
|---------|-------------|
| 🧠 Auto topic tagging | Naive Bayes, Boosting, Decision Trees, Neural Nets, CV, Regression, etc. |
| 🎯 Adaptive difficulty | Next question depends on your recent accuracy |
| 🔁 Spaced repetition | Wrong questions return after 1 / 3 / 7 days |
| 🧮 Variant generator | LLM creates new numeric variants (change numbers, recompute with Python) |
| 💬 "Explain like I'm new" | Step-by-step tutor chat per question |
| 📊 Analytics dashboard | Topic heatmap, time/question, accuracy trend |
| 🏆 Leaderboard (optional) | Multi-user |
| 📤 Export | Results to PDF/CSV, question bank to JSON/HTML (same format as your OOSD quiz) |
| 🌙 Dark mode, mobile-friendly | |
| 📴 Offline mode (PWA) | Practice without internet |
| 🧾 Answer-key audit report | Lists all questions where key ≠ web/AI answer |

---

## 7. API Endpoints

```
POST /api/ingest/upload              # upload PDF/DOCX, returns job_id
GET  /api/ingest/{job_id}            # status + extracted questions preview
POST /api/ingest/{job_id}/approve    # save to question bank

GET  /api/questions?course=&week=&topic=
POST /api/questions                  # manual add
PUT  /api/questions/{id}

POST /api/answer-finder/{qid}        # run web + AI check on one question
POST /api/answer-finder/bulk         # all / filtered questions (background job)
GET  /api/answer-finder/report       # conflicts & low-confidence list

POST /api/exam/start                 # config -> attempt_id + questions (no answers)
POST /api/exam/{attempt}/answer      # save response
POST /api/exam/{attempt}/submit      # grade
GET  /api/exam/{attempt}/result

GET  /api/analytics/summary
```

---

## 8. Key Code

### 8.1 `requirements.txt`
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
python-multipart
pdfplumber
pymupdf
python-docx
pytesseract
pillow
httpx
anthropic
python-dotenv
numpy
```

### 8.2 `.env`
```
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DATABASE_URL=sqlite:///./smartexam.db
```

### 8.3 `services/pdf_parser.py`
```python
import fitz, pdfplumber, pytesseract
from PIL import Image
import io, docx

def extract_pdf(path: str) -> dict:
    pages = []
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        if len(text) < 40:                      # scanned / screenshot page -> OCR
            text = pytesseract.image_to_string(Image.open(io.BytesIO(img_bytes)))
        pages.append({"page": i + 1, "text": text, "image": img_bytes})
    return {"pages": pages}

def extract_docx(path: str) -> dict:
    d = docx.Document(path)
    text = "\n".join(p.text for p in d.paragraphs)
    return {"pages": [{"page": 1, "text": text, "image": None}]}
```

### 8.4 `services/question_extractor.py`
```python
import json, anthropic, base64
client = anthropic.Anthropic()

SYSTEM = """You extract exam questions from assignment pages.
Return ONLY a JSON array. Each item:
{text, type (MCQ|MSQ|NUMERIC|TRUE_FALSE), options:[{key,text}], correct:[keys] or null,
 numeric_answer:number|null, explanation:string|null, topic:string, marks:number}
Preserve math in LaTeX. If an answer/solution is shown in the page, include it in 'correct'."""

def extract_questions(page_text: str, page_image: bytes | None):
    content = []
    if page_image:
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": "image/png",
            "data": base64.b64encode(page_image).decode()}})
    content.append({"type": "text", "text": page_text})
    msg = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=4000,
        system=SYSTEM, messages=[{"role": "user", "content": content}])
    raw = msg.content[0].text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
```

### 8.5 `services/web_search.py`
```python
import httpx, os

async def search(query: str, k: int = 8):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post("https://api.tavily.com/search", json={
            "api_key": os.getenv("TAVILY_API_KEY"),
            "query": query, "max_results": k, "include_raw_content": False})
    return [{"title": x["title"], "url": x["url"], "snippet": x["content"]}
            for x in r.json().get("results", [])]
```

### 8.6 `services/answer_engine.py`
```python
import json, anthropic
from .web_search import search
client = anthropic.Anthropic()

async def find_answer(q: dict) -> dict:
    # 1) build queries
    qs = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=300,
        messages=[{"role": "user", "content":
          f"Write 2 short web search queries to verify the answer to:\n{q['text']}\nReturn JSON list only."}])
    queries = json.loads(qs.content[0].text.replace("```json","").replace("```","").strip())

    # 2) search
    results = []
    for qu in queries:
        results += await search(qu)

    ctx = "\n".join(f"[{i}] {r['title']} - {r['snippet']} ({r['url']})"
                    for i, r in enumerate(results[:10]))

    # 3) solve with evidence
    prompt = f"""Question: {q['text']}
Options: {q.get('options')}
Web evidence:\n{ctx}

Solve it yourself step by step, use evidence only as support.
Return JSON: {{"answer": [...keys] or number, "confidence": 0-1,
"explanation": "...", "used_sources": [indexes]}}"""
    out = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=1200,
        messages=[{"role": "user", "content": prompt}])
    data = json.loads(out.content[0].text.replace("```json","").replace("```","").strip())

    # 4) compare with stored key
    key = q.get("correct")
    status = "UNSURE" if data["confidence"] < 0.6 else \
             ("MATCH" if key and sorted(key) == sorted(data["answer"]) else "CONFLICT")
    data["status"] = status
    data["sources"] = [results[i]["url"] for i in data.get("used_sources", []) if i < len(results)]
    return data
```

### 8.7 `services/grader.py`
```python
def grade(q, selected, neg=0.0):
    if q["type"] == "MCQ":
        return q["marks"] if selected == q["correct"] else -neg
    if q["type"] == "MSQ":
        right, chosen = set(q["correct"]), set(selected)
        if chosen - right:           # any wrong option -> zero / negative
            return -neg
        return q["marks"] * len(chosen) / len(right)       # partial marking
    if q["type"] == "NUMERIC":
        tol = q.get("tolerance", 0)
        return q["marks"] if abs(float(selected) - q["numeric_answer"]) <= tol else 0
    if q["type"] == "TRUE_FALSE":
        return q["marks"] if selected == q["correct"] else -neg
```

### 8.8 `routers/ingest.py`
```python
from fastapi import APIRouter, UploadFile, BackgroundTasks
import shutil, uuid
from ..services.pdf_parser import extract_pdf, extract_docx
from ..services.question_extractor import extract_questions

router = APIRouter(prefix="/api/ingest")
JOBS = {}

def process(job_id, path):
    data = extract_pdf(path) if path.endswith(".pdf") else extract_docx(path)
    all_q = []
    for p in data["pages"]:
        all_q += extract_questions(p["text"], p["image"])
    JOBS[job_id] = {"status": "done", "questions": all_q}

@router.post("/upload")
async def upload(file: UploadFile, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    path = f"data/uploads/{job_id}_{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    JOBS[job_id] = {"status": "processing"}
    bg.add_task(process, job_id, path)
    return {"job_id": job_id}

@router.get("/{job_id}")
def status(job_id: str):
    return JOBS.get(job_id, {"status": "not_found"})
```

### 8.9 Frontend — Exam page skeleton (`ExamPage.jsx`)
```jsx
import { useState, useEffect } from "react";
import { api } from "../api";

export default function ExamPage({ attemptId, questions }) {
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [marked, setMarked] = useState(new Set());
  const [left, setLeft] = useState(questions.length * 90);

  useEffect(() => {
    const t = setInterval(() => setLeft(s => (s > 0 ? s - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, []);
  useEffect(() => { if (left === 0) submit(); }, [left]);

  const q = questions[idx];
  const select = (key) => {
    setAnswers(a => {
      if (q.type === "MSQ") {
        const cur = new Set(a[q.id] || []);
        cur.has(key) ? cur.delete(key) : cur.add(key);
        return { ...a, [q.id]: [...cur] };
      }
      return { ...a, [q.id]: [key] };
    });
    api.post(`/exam/${attemptId}/answer`, { qid: q.id, selected: answers[q.id] });
  };
  const submit = () => api.post(`/exam/${attemptId}/submit`);

  return (
    <div className="grid grid-cols-[1fr_260px] gap-4 p-4">
      <main>
        <div className="flex justify-between">
          <h2>Question {idx + 1} / {questions.length}</h2>
          <span>⏱ {Math.floor(left/60)}:{String(left%60).padStart(2,"0")}</span>
        </div>
        <p className="my-3">{q.text}</p>
        {q.options.map(o => (
          <label key={o.key} className="block p-2 border rounded my-1 cursor-pointer">
            <input type={q.type==="MSQ"?"checkbox":"radio"}
                   checked={(answers[q.id]||[]).includes(o.key)}
                   onChange={() => select(o.key)} /> {o.text}
          </label>
        ))}
        <div className="mt-4 flex gap-2">
          <button onClick={() => setIdx(i => Math.max(0, i-1))}>Previous</button>
          <button onClick={() => setMarked(m => new Set(m).add(q.id))}>Mark for review</button>
          <button onClick={() => setIdx(i => Math.min(questions.length-1, i+1))}>Next</button>
          <button onClick={submit}>Submit</button>
        </div>
      </main>
      <aside className="grid grid-cols-5 gap-1 content-start">
        {questions.map((x, i) => (
          <button key={x.id} onClick={() => setIdx(i)}
            className={marked.has(x.id) ? "bg-purple-500" :
                       answers[x.id] ? "bg-green-500" : "bg-gray-200"}>{i+1}</button>
        ))}
      </aside>
    </div>
  );
}
```

---

## 9. Seed Data — Questions from Your Files

| File | Topics | Notes |
|------|--------|-------|
| `Ml_Assignment2.pdf` (Week 2) | Linear regression, design matrix, Lasso/Ridge, subset selection, PCR, kNN | Screenshot PDF → needs OCR + image extraction |
| `ML_assignment_3.docx` | (parse with python-docx) | |
| `ML_Assignment4.docx` | (parse with python-docx) | |
| `Assignment_5.pdf` | Neural nets, parameter count, MLE, backprop, ANN vs SVM | Numeric + MSQ |
| `Assignment_6.pdf` | Recall, k-fold CV, bagging, stacking, ROC | Numeric + MSQ |
| `Assignment_7.pdf` | Decision trees, Gini, bias–variance, missing values | Numeric + MSQ |
| `Assignment_8_ML.pdf` | Naive Bayes, AdaBoost, random forest | |
| `OOSD_2026_..._Quiz.html` | OOSD MCQ/MSQ | Parse HTML → JSON directly (BeautifulSoup) |

Run:
```bash
python scripts/seed_from_assignments.py --dir ./assignments
```

---

## 10. Setup & Run

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
sudo apt install tesseract-ocr                       # Windows: install Tesseract
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev                                          # http://localhost:5173
```

---

## 11. ⚠️ Important Notes on Answer Quality

While reviewing your uploaded solutions, a few answers look **questionable** — exactly the cases the Answer Finder's `CONFLICT` flag is designed to catch. Examples worth re-checking:

1. **Assignment 7, Q5** — the written solution talks itself in circles ("Wait—there is an important detail…") and the final split (17.35) is not clearly justified. Recompute information gain for every candidate threshold.
2. **Assignment 5, Q8** — the gradient calculation: ∂E/∂w₂ = 2(f−y)·∂f/∂w₂ = 2(0.8176−5)(0.0746) ≈ −0.624, so w₂_new = 1 − 0.5(−0.624) = **1.312**, but the file says "1.3119" — rounding only, fine for numeric tolerance.
3. **Assignment 6, Q5** — the checked options include "Accuracy = 2(TP+TN)/(TP+TN+FP+FN)", which is **not** the correct formula (accuracy has no factor 2). Verify.
4. **Assignment 5, Q1** — the explanation says "exponential model" but picks `y = x^w` (a power model). Inconsistent wording.
5. **Assignment 8, Q6** — "Option 2 and 3" for random forest `m`: check against the original option text.

The system's **Answer-key audit report** will list these automatically so you never train on wrong keys.

---

## 12. Roadmap

| Phase | Deliverable | Time |
|-------|-------------|------|
| 1 | Seed JSON + exam UI (timer, palette, grading) | 3–4 days |
| 2 | PDF/DOCX ingestion + OCR + LLM extraction | 3 days |
| 3 | Answer Finder (web search + LLM + consensus) | 3 days |
| 4 | Analytics, spaced repetition, wrong-answer retry | 3 days |
| 5 | Variant generator, adaptive difficulty, PWA | 4 days |
| 6 | Auth, deploy (Docker + Render/Railway/Vercel) | 2 days |

---

## 13. Docker (optional)

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y tesseract-ocr
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```

---

## 14. Future Ideas
- Voice-based viva mode
- Collaborative study rooms
- Auto-generate full mock paper from syllabus topics
- Browser extension: right-click any question on a web page → add to bank
- Plagiarism-safe question paraphrasing for new variants
