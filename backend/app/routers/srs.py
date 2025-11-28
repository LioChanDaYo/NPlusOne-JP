from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..models import Card, Review, Sentence
from ..schemas import DueCard, ReviewIn
from ..srs import review_card_object # On importe la nouvelle fonction

router = APIRouter(prefix="/srs", tags=["srs"])

@router.get("/due", response_model=list[DueCard])
def due(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    # On récupère les cartes dues (jointure pour avoir le texte)
    results = db.query(Card, Sentence).join(Sentence, Card.sentence_id == Sentence.id)\
                .filter(Card.user_id == 1, Card.due <= now)\
                .order_by(Card.due)\
                .limit(20)\
                .all()
    
    out = []
    for card, sentence in results:
        q = "Comment se lit et que veut dire ce mot ?" if card.kind=="recog" else "Quel est ce mot en japonais ?"
        out.append(DueCard(
            id=card.id, 
            lemma=card.lemma, 
            kind=card.kind, 
            question=q, 
            sentence_id=card.sentence_id,
            sentence_text=sentence.text
        ))
    return out

@router.post("/review")
def review(payload: ReviewIn, db: Session = Depends(get_db)):
    c = db.query(Card).get(payload.card_id)
    if not c:
        return {"ok": False}
    
    # Enregistrer l'historique
    r = Review(card_id=c.id, rating=payload.rating, latency_ms=payload.latency_ms)
    db.add(r)
    
    # Calculer le prochain intervalle (modifie l'objet c directement)
    review_card_object(c, payload.rating)
    
    db.commit()
    return {
        "ok": True, 
        "due": c.due.isoformat(), 
        "stability": c.stability, 
        "difficulty": c.difficulty
    }