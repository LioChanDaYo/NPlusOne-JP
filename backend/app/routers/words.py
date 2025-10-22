from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User, Lexeme, Sentence, Card
from ..schemas import AddWordIn, SuggestResponse, AcceptIn, SentenceOut
from ..services.sentences import fetch_candidates


router = APIRouter(prefix="/words", tags=["words"])


# Pour demo: user=1 auto


def _known_lemmas(db: Session, user_id: int = 1):
    rows = db.query(Lexeme).filter(Lexeme.user_id==user_id, Lexeme.known==True).all()
    return {r.lemma for r in rows}


@router.post("/add-word", response_model=SuggestResponse)
def add_word(payload: AddWordIn, db: Session = Depends(get_db)):
    lemma = payload.lemma
    if not db.query(User).get(1):
        db.add(User(id=1, name="you"))
        db.commit()
    known = _known_lemmas(db)
    # on marque le mot comme inconnu
    db.add(Lexeme(user_id=1, lemma=lemma, known=False))
    db.commit()
    cands = fetch_candidates(lemma, known)
    # on insère les phrases candidates en base si pas déjà
    sent_out = []
    for c in cands:
        s = Sentence(text=c["text"], source=c["source"], source_id=c["source_id"], start_ms=c["start_ms"], end_ms=c["end_ms"])
        db.add(s)
        db.commit()
        db.refresh(s)
        sent_out.append(SentenceOut.model_validate(s))
    return SuggestResponse(lemma=lemma, candidates=sent_out)


@router.post("/accept")
def accept_sentence(payload: AcceptIn, db: Session = Depends(get_db)):
    s = db.query(Sentence).get(payload.sentence_id)
    if not s:
        raise HTTPException(404, "sentence not found")
    # créer deux cartes par défaut
    for kind in ("recog","retrieval"):
        c = Card(user_id=1, lemma=payload.lemma, kind=kind, sentence_id=s.id)
        db.add(c)
    db.commit()
    return {"ok": True}