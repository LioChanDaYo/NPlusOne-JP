import sys
import os
import bz2  # <--- 1. On importe la lib de compression

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, engine, Base
from app.models import Sentence

def import_tsv(filepath: str):
    db = SessionLocal()
    print(f"Début de l'import depuis {filepath}...")
    
    count = 0
    # 2. On utilise bz2.open avec le mode 'rt' (read text)
    with bz2.open(filepath, 'rt', encoding='utf-8') as f:
        for line in f:
            try:
                parts = line.strip().split('\t')
                # Tatoeba: id \t lang \t text
                if len(parts) < 3: continue
                
                if parts[1] != 'jpn': continue
                
                text = parts[2]
                
                # Filtre : phrases courtes (entre 5 et 60 caractères)
                if 5 < len(text) < 60:
                    s = Sentence(
                        text=text, 
                        lang='jpn', 
                        source='tatoeba', 
                        source_id=parts[0]
                    )
                    db.add(s)
                    count += 1
                    
                    if count % 1000 == 0:
                        print(f"{count} phrases importées...")
                        db.commit()
                        
                    # Limite pour le dev (retirer ou augmenter plus tard)
                    if count >= 10000: 
                        break
            except Exception as e:
                print(f"Erreur sur une ligne : {e}")
                continue

    db.commit()
    db.close()
    print(f"Terminé : {count} phrases ajoutées.")

if __name__ == "__main__":
    # Assurez-vous que le fichier s'appelle bien ainsi dans le dossier backend
    import_tsv("jpn_sentences.tsv.bz2")