from datetime import datetime
from fsrs import Scheduler, Card, Rating


# Instance globale (stateless côté API, état porté par la Card sérialisée en DB)
scheduler = Scheduler()


# Conversion note (1–4) → Rating FSRS
_RATING_MAP = {
    1: Rating.Again,
    2: Rating.Hard,
    3: Rating.Good,
    4: Rating.Easy,
}


def schedule(prev_stab: float | None, prev_diff: float | None, rating: int):
    # On crée une Card éphémère portant l'état actuel (stability/difficulty)
    card = Card()
    if prev_stab is not None:
        card.stability = float(prev_stab)
    if prev_diff is not None:
        card.difficulty = float(prev_diff)


    # Applique la revue
    r = _RATING_MAP.get(rating, Rating.Good)
    card, _log = scheduler.review_card(card, r)


    # La lib peuple due/stability/difficulty directement
    due: datetime = card.due
    return float(card.stability), float(card.difficulty), due