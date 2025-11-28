from datetime import datetime, timezone
from fsrs import Scheduler, Card, Rating, State

# Instance du planificateur
scheduler = Scheduler()

# --- AUTO-DETECTION DES ENUMS ---
# Pour éviter les erreurs "AttributeError: New" ou "AGAIN",
# on construit le mapping dynamiquement quelle que soit la version de la lib.
try:
    # On essaie de mapper {1: Rating.Again, ...} ou {1: Rating.AGAIN, ...}
    _RATING_MAP = {r.value: r for r in Rating}
    _STATE_MAP = {s.value: s for s in State}
except Exception as e:
    print(f"⚠️ Erreur d'initialisation FSRS: {e}")
    # Fallback critique (si l'auto-détection échoue)
    _RATING_MAP = {}
    _STATE_MAP = {}

def to_utc(dt):
    """Force une date en UTC timezone-aware."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def review_card_object(db_card, rating: int):
    # 1. Instancier la carte FSRS (Structure v6 épurée)
    f_card = Card()
    
    # On ne remplit QUE les champs mémoire (D/S/R) + State
    if db_card.due:
        f_card.due = to_utc(db_card.due)
        
    f_card.stability = float(db_card.stability)
    f_card.difficulty = float(db_card.difficulty)
    
    if db_card.last_review:
        f_card.last_review = to_utc(db_card.last_review)
    
    # Conversion Entier DB -> Enum State
    # On utilise le mapping auto-généré. Si inconnu (0), on espère que c'est le défaut.
    # Si la carte est nouvelle (0), on ne touche pas f_card.state (qui est New par défaut)
    if db_card.state in _STATE_MAP:
        f_card.state = _STATE_MAP[db_card.state]

    # 2. Appliquer la révision
    now = datetime.now(timezone.utc)
    
    # Récupération de l'objet Rating correct (ex: Rating.Good)
    fsrs_rating = _RATING_MAP.get(rating)
    if not fsrs_rating:
        raise ValueError(f"Note invalide : {rating}. Attendue : {list(_RATING_MAP.keys())}")

    # Calcul (review_card renvoie un tuple : card, log)
    f_card, _log = scheduler.review_card(f_card, fsrs_rating, now)

    # 3. Mise à jour de l'objet DB
    db_card.due = f_card.due
    db_card.stability = f_card.stability
    db_card.difficulty = f_card.difficulty
    db_card.last_review = f_card.last_review
    
    # Récupération de l'état (compatible Enum ou Int)
    if hasattr(f_card.state, 'value'):
        db_card.state = int(f_card.state.value)
    else:
        db_card.state = int(f_card.state)

    # 4. Mise à jour manuelle des statistiques (plus gérées par Card)
    db_card.reps = (db_card.reps or 0) + 1
    # Si la note correspond à "Again" (valeur 1 généralement)
    if rating == 1:
        db_card.lapses = (db_card.lapses or 0) + 1
        
    return db_card