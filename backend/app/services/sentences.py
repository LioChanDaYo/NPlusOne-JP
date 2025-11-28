from typing import List, Dict
from ..nlp import is_n_plus_1
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import os

# Mock corpus minimal (remplace plus tard par YouTube/Tatoeba)
MOCK = [
    {"id":"m1","text":"今日はいい天気ですね。","source":"mock","source_id":"mock1"},
    {"id":"m2","text":"昨日、新しい靴を買いました。","source":"mock","source_id":"mock2"},
    {"id":"m3","text":"この店のコーヒーは本当に美味しい。","source":"mock","source_id":"mock3"},
]


def fetch_candidates(lemma: str, known: set) -> List[Dict]:
    out = []
    for i, s in enumerate(MOCK, start=1):
        if is_n_plus_1(s["text"], target=lemma, known_lemmas=known):
            out.append({
                "id": i,
                "text": s["text"],
                "source": s["source"],
                "source_id": s["source_id"],
                "start_ms": None,
                "end_ms": None,
            })
    return out[:5]

# 1. Configuration du client YouTube (consomme le quota Google)
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

def search_videos(query_japanese):
    # Coût: 100 unités
    request = youtube.search().list(
        q=query_japanese,
        part="id,snippet",
        type="video",
        relevanceLanguage="ja",
        maxResults=5
    )
    return request.execute()

def get_subtitles(video_id):
    # Coût: 0 unité (via youtube-transcript-api)
    try:
        # Récupère les sous-titres (priorité au japonais manuel, puis généré auto)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
        return transcript
    except Exception as e:
        print(f"Pas de sous-titres pour {video_id}: {e}")
        return []