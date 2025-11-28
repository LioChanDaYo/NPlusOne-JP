# NPlusOne-JP
Apprentissage du vocabulaire japonais à l'aide de phrases d'exemples N+1

Notes d'installation : FSRS a besoin de l'installation Rust et Cargo 
Windows :
https://rustup.rs
Télécharge et exécute rustup-init.exe
Accepte les options par défaut (cela installe rustc, cargo et les outils nécessaires)

Certaines libs exigent Python 3.11
Windows :
# 1) Installer Python 3.11 si besoin
winget install -e --id Python.Python.3.11

# 2) (Re)créer un venv 3.11 dans le dossier backend
cd backend
py -3.11 -m venv .venv
. .\.venv\Scripts\Activate.ps1

# 3) Mettre pip/outils à jour
python -m pip install -U pip wheel setuptools

# 4) Installer les deps (inclut fsrs==2.4.0)
pip install -r requirements.txt

# 5) Lancer l’API
(optionnel le mock avec : python -c "from app.seed_mock import *")
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# 6) Peupler la base de phrases
pour l'instant à l'aide du script import_tatoeba.py, à lancer depuis /backend à partir du moment où jpn_sentences.tsv.bz2, téléchargé depuis le site tatoeba, se trouve également dans /backend
py .\scripts\import_tatoeba.py

Pour le Frontend :
cd ../frontend
npm i
setx NEXT_PUBLIC_API http://localhost:8000
npm run dev

Visite : http://localhost:3000