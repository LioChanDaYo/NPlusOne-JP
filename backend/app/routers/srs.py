from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..models import Card, Review
from ..schemas import DueCard, ReviewIn
from ..srs import schedule


router = APIRouter(prefix="/srs", tags=["srs"])


@router.get("/due", response_model=list[DueCard])
def due(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    cards = db.query(Card).filter(Card.user_id==1, Card.due <= now).order_by(Card.due).limit(20).all()
    out = []
    for c in cards:
        q = "読みを選んでください" if c.kind=="recog" else "日本語で答えてください"
        out.append(DueCard(id=c.id, lemma=c.lemma, kind=c.kind, question=q, sentence_id=c.sentence_id))
    return out


@router.post("/review")
def review(payload: ReviewIn, db: Session = Depends(get_db)):
    c = db.query(Card).get(payload.card_id)
    if not c:
        return {"ok": False}
    r = Review(card_id=c.id, rating=payload.rating, latency_ms=payload.latency_ms)
    db.add(r)
    stab, diff, due = schedule(c.stability, c.difficulty, payload.rating)
    c.stability, c.difficulty, c.due = stab, diff, due
    db.commit()
    return {"ok": True, "due": due.isoformat(), "stability": stab, "difficulty": diff}