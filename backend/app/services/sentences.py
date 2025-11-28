from typing import List, Dict
import os
import html
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from ..nlp import is_n_plus_1

# On garde le client YouTube global pour éviter de le recréer à chaque appel
# Assure-toi que YOUTUBE_API_KEY est bien dans ton .env
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

def search_videos(query: str, max_results: int = 3):
    """Cherche des vidéos japonaises contenant le mot-clé."""
    try:
        request = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            relevanceLanguage="ja", # Priorité au contenu japonais
            maxResults=max_results
        )
        response = request.execute()
        return response.get("items", [])
    except Exception as e:
        print(f"Erreur API YouTube: {e}")
        return []

def get_subtitles(video_id: str):
    """Récupère les sous-titres (priorité manuel > auto)."""
    try:
        # On demande du japonais ('ja')
        return YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
    except Exception:
        # Si pas de sous-titres ou erreur, on renvoie une liste vide
        return []

def fetch_candidates(lemma: str, known: set) -> List[Dict]:
    """
    Cherche des phrases N+1 pour 'lemma' via l'API YouTube.
    """
    out = []
    
    # 1. On cherche des vidéos liées au mot (on ajoute "日本語" pour aider le contexte)
    videos = search_videos(f"{lemma} 日本語")
    
    existing_sentences = set() # Pour éviter les doublons exacts

    for video in videos:
        vid_id = video['id']['videoId']
        vid_title = video['snippet']['title']
        
        # 2. On récupère le transcript
        transcript = get_subtitles(vid_id)
        
        # 3. On filtre chaque ligne du transcript
        for line in transcript:
            text = line['text']
            
            # Nettoyage basique (entités HTML & sauts de ligne)
            text = html.unescape(text).replace("\n", " ")
            
            # Optimisation : Si le mot n'est pas dedans, on passe direct
            if lemma not in text:
                continue
                
            # Vérification N+1 : Le mot cible doit être le SEUL inconnu
            if is_n_plus_1(text, target=lemma, known_lemmas=known):
                
                # Évite les doublons
                if text in existing_sentences:
                    continue
                existing_sentences.add(text)
                
                # Ajout aux candidats
                out.append({
                    "id": 0, # Sera géré par la DB lors de l'insertion
                    "text": text,
                    "source": "youtube",
                    "source_id": vid_id,
                    "start_ms": int(line['start'] * 1000),
                    "end_ms": int((line['start'] + line['duration']) * 1000),
                    # On pourrait passer le titre de la vidéo comme metadata si besoin
                })
                
                # Si on a trouvé assez de phrases (ex: 5), on arrête pour gagner du temps
                if len(out) >= 5:
                    return out

    return out