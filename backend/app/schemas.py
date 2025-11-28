from pydantic import BaseModel
from typing import Optional, List


class SentenceOut(BaseModel):
    id: int
    text: str
    source: str
    source_id: str
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None


    class Config:
        from_attributes = True


class SuggestResponse(BaseModel):
    lemma: str
    candidates: List[SentenceOut]


class AddWordIn(BaseModel):
    lemma: str


class AcceptIn(BaseModel):
    lemma: str
    sentence_id: int
    accept: bool
    reason: Optional[str] = None


class DueCard(BaseModel):
    id: int
    lemma: str
    kind: str
    question: str
    sentence_id: int
    sentence_text: str


class ReviewIn(BaseModel):
    card_id: int
    rating: int # 1–4
    latency_ms: int = 0