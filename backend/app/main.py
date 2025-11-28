import os
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import words, srs


Base.metadata.create_all(bind=engine)


app = FastAPI(title="N+1 Japanese API")


origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(words.router)
app.include_router(srs.router)


@app.get("/health")
async def health():
    return {"status": "ok"}