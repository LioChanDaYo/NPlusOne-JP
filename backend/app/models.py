from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="you")


class Lexeme(Base):
    __tablename__ = "lexicon"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lemma = Column(String, index=True)
    known = Column(Boolean, default=True)
    stability = Column(Float, default=0.0)
    difficulty = Column(Float, default=0.0)


class Sentence(Base):
    __tablename__ = "sentences"
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    lang = Column(String, default="ja")
    source = Column(String) # youtube|tatoeba|mock
    source_id = Column(String, index=True)
    start_ms = Column(Integer, nullable=True)
    end_ms = Column(Integer, nullable=True)
    license = Column(String, nullable=True)
    author = Column(String, nullable=True)


class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lemma = Column(String, index=True)
    kind = Column(String) # recog|retrieval
    sentence_id = Column(Integer, ForeignKey("sentences.id"))
    hint = Column(Text, nullable=True)
    furigana = Column(Text, nullable=True)
    due = Column(DateTime, default=datetime.utcnow)
    stability = Column(Float, default=0.0)
    difficulty = Column(Float, default=0.0)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.id"))
    ts = Column(DateTime, default=datetime.utcnow)
    rating = Column(Integer) # 1–4
    latency_ms = Column(Integer, default=0)