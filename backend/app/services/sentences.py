from typing import List, Dict
import os
import html
from sqlalchemy import func
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from ..db import SessionLocal
from ..models import Sentence
from ..nlp import is_n_plus_1

# --- SECTION 1 : LOGIQUE YOUTUBE (Conservée) ---

# On garde le client YouTube global
# Si la clé n'est pas là, on évite de faire planter l'app au démarrage, 
# l'erreur surviendra seulement si on appelle la fonction.
YOUTUBE_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY) if YOUTUBE_KEY else None

def search_videos(query: str, max_results: int = 3):
    """Cherche des vidéos japonaises contenant le mot-clé."""
    if not youtube:
        print("⚠️ Pas de clé API YouTube configurée.")
        return []
    try:
        request = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            relevanceLanguage="ja",
            maxResults=max_results
        )
        response = request.execute()
        return response.get("items", [])
    except Exception as e:
        print(f"Erreur API YouTube: {e}")
        return []

def get_subtitles(video_id: str):
    """Récupère les sous-titres."""
    try:
        return YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
    except Exception:
        return []

def fetch_from_youtube(lemma: str, known: set, limit: int = 5) -> List[Dict]:
    """Logique d'extraction depuis YouTube (lente mais riche en contexte audio)."""
    out = []
    print(f"🔎 Fallback sur YouTube pour : {lemma}")
    
    videos = search_videos(f"{lemma} 日本語")
    existing_sentences = set()

    for video in videos:
        if len(out) >= limit: break
        
        vid_id = video['id']['videoId']
        transcript = get_subtitles(vid_id)
        
        for line in transcript:
            text = line['text']
            text = html.unescape(text).replace("\n", " ")
            
            if lemma not in text: continue
            if text in existing_sentences: continue
            
            # Filtre N+1 (peut être assoupli ici si besoin)
            if is_n_plus_1(text, target=lemma, known_lemmas=known):
                existing_sentences.add(text)
                out.append({
                    "id": 0, # Pas d'ID DB pour l'instant
                    "text": text,
                    "source": "youtube",
                    "source_id": vid_id,
                    "start_ms": int(line['start'] * 1000),
                    "end_ms": int((line['start'] + line['duration']) * 1000),
                })
                if len(out) >= limit: break
    return out


# --- SECTION 2 : LOGIQUE TATOEBA / DB (Prioritaire) ---

def fetch_from_db(lemma: str, known: set, limit: int = 5) -> List[Dict]:
    """Logique d'extraction depuis la DB locale (rapide)."""
    db = SessionLocal()
    out = []
    try:
        # 1. On récupère un large pool de phrases contenant le mot
        raw_candidates = db.query(Sentence)\
            .filter(Sentence.text.contains(lemma))\
            .filter(func.length(Sentence.text) < 60)\
            .limit(100)\
            .all()

        n_plus_one_matches = []
        fallback_matches = []

        for s in raw_candidates:
            if lemma not in s.text: continue

            # Priorité 1 : N+1 Strict
            if is_n_plus_1(s.text, lemma, known):
                n_plus_one_matches.append(s)
            else:
                # Priorité 2 : Phrases simples (courtes)
                fallback_matches.append(s)

        # On prend d'abord les N+1
        results = n_plus_one_matches[:limit]
        
        # Si pas assez, on complète avec les plus courtes des autres (Fallback Simplicité)
        if len(results) < limit:
            missing = limit - len(results)
            fallback_matches.sort(key=lambda x: len(x.text))
            results.extend(fallback_matches[:missing])

        # Conversion en format dict
        for s in results:
            out.append({
                "id": s.id,
                "text": s.text,
                "source": s.source,
                "source_id": s.source_id,
                "start_ms": s.start_ms,
                "end_ms": s.end_ms,
            })
            
        return out
    finally:
        db.close()


# --- SECTION 3 : ORCHESTRATEUR ---

def fetch_candidates(lemma: str, known: set) -> List[Dict]:
    """
    Stratégie Hybride :
    1. Regarde en DB (Tatoeba).
    2. Si < 5 phrases, complète avec YouTube.
    """
    candidates = fetch_from_db(lemma, known, limit=5)
    
    # Si on n'a pas assez de phrases (ex: mot rare ou argot absent de Tatoeba)
    if len(candidates) < 5:
        missing = 5 - len(candidates)
        youtube_candidates = fetch_from_youtube(lemma, known, limit=missing)
        candidates.extend(youtube_candidates)
        
    return candidates