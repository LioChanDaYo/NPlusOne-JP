from .db import SessionLocal, Base, engine
from .models import User, Lexeme


Base.metadata.create_all(bind=engine)


db = SessionLocal()
if not db.query(User).get(1):
    db.add(User(id=1, name="you"))


# quelques mots connus pour que N+1 filtre marche
for w in ["今日","いい","天気","昨日","新しい","靴","買う","この","店","コーヒー","本当に","美味しい"]:
    db.add(Lexeme(user_id=1, lemma=w, known=True))


db.commit(); db.close()
print("Seed done.")