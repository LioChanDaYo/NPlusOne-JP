from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..models import Card, Review, Sentence
from ..schemas import DueCard, ReviewIn
from ..srs import schedule


router = APIRouter(prefix="/srs", tags=["srs"])


@router.get("/due", response_model=list[DueCard])
def due(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    
    # On fait une jointure pour avoir les infos de la carte ET de la phrase
    # On filtre les cartes dont la date 'due' est passée
    results = db.query(Card, Sentence).join(Sentence, Card.sentence_id == Sentence.id)\
                .filter(Card.user_id == 1, Card.due <= now)\
                .order_by(Card.due)\
                .limit(20)\
                .all()
    
    out = []
    for card, sentence in results:
        # Logique simple pour la question
        if card.kind == "recog":
            # Recognition : On montre la phrase, on cache le mot ? 
            # Pour l'instant on montre tout, l'utilisateur doit deviner la lecture/sens du mot cible
            q = "Comment se lit et que veut dire ce mot ?"
        else:
            # Retrieval : On devrait cacher le mot dans la phrase (Cloze deletion)
            # Pour ce MVP, on simplifie
            q = "Quel est ce mot en japonais ?"

        out.append(DueCard(
            id=card.id, 
            lemma=card.lemma, 
            kind=card.kind, 
            question=q, 
            sentence_id=card.sentence_id,
            sentence_text=sentence.text # <--- On remplit le nouveau champ
        ))
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