from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .recommender import Recommender
from .schemas import MoodRequest, MoodResponse, RecommendRequest, RecommendResponse, TrackItem

app = FastAPI(title="FeelIt API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

rec = Recommender(base_dir=BASE_DIR)


@app.get("/")
def root() -> dict:
    return {"message": "FeelIt API is running. Go to /docs"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=MoodResponse)
def predict(req: MoodRequest) -> MoodResponse:
    pred = rec.predict(req.text)
    return MoodResponse(mood=pred.mood, mode=pred.mode, confidence=pred.confidence)


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest) -> RecommendResponse:
    pred, df = rec.recommend(req.text, req.n)

    tracks = [
        TrackItem(
            spotify_id=str(r.spotify_id),
            artist=str(r.artist),
            name=str(r.name),
            popularity=float(r.popularity),
            source_playlist=str(r.source_playlist),
            spotify_url=getattr(r, "spotify_url", None),
            preview_url=getattr(r, "preview_url", None),
            image_url=getattr(r, "image_url", None),
        )
        for r in df.itertuples(index=False)
    ]

    return RecommendResponse(
        mood=pred.mood,
        mode=pred.mode,
        confidence=pred.confidence,
        tracks=tracks,
    )