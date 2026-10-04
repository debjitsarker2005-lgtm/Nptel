from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field

class OptionSchema(BaseModel):
    key: str
    text: str

class NumericAnswerSchema(BaseModel):
    value: float
    tolerance: float = 0.0

class AnswerMetaSchema(BaseModel):
    key_source: Optional[str] = "assignment"
    web_verified: Optional[bool] = True
    confidence: Optional[float] = 0.95
    sources: Optional[List[str]] = []
    status: Optional[str] = "MATCH"

class QuestionSchema(BaseModel):
    id: str
    course: str
    week: int
    source: Optional[str] = None
    type: str  # MCQ | MSQ | NUMERIC | TRUE_FALSE
    topic: Optional[str] = "General"
    difficulty: Optional[str] = "medium"
    marks: float = 1.0
    negative_marks: float = 0.0
    text: str
    options: List[OptionSchema] = []
    correct: List[str] = []
    numeric_answer: Optional[NumericAnswerSchema] = None
    explanation: Optional[str] = ""
    image: Optional[str] = None
    answer_meta: Optional[AnswerMetaSchema] = None

class ExamConfigSchema(BaseModel):
    course: Optional[str] = "ALL"
    week: Optional[Union[int, str]] = "ALL"
    mode: Optional[str] = "EXAM"
    count: Optional[int] = 25
    shuffle: Optional[bool] = False

class SubmitResponseSchema(BaseModel):
    qid: str
    selected: Optional[Union[List[str], float, str]] = None

class ExamSubmitSchema(BaseModel):
    responses: List[SubmitResponseSchema]
