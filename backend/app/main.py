from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .recommender import Recommender
from .schemas import (
    MoodRequest,
    MoodResponse,
    RecommendRequest,
    RecommendResponse,
    TrackItem,
    ChatRequest,
    ChatResponse,
)

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

# memorie simplă pe sesiune
chat_memory: dict[str, dict] = {}


def build_track_items(df) -> list[TrackItem]:
    return [
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


def is_followup_request(message: str) -> bool:
    msg = message.lower().strip()

    followup_phrases = [
        "mai da-mi",
        "mai dă-mi",
        "alte piese",
        "altceva",
        "again",
        "more songs",
        "other songs",
        "give me more",
        "another ones",
        "different songs",
        "give me other songs",
        "mai vreau",
        "inca una",
        "încă una",
        "try again",
    ]

    return any(phrase in msg for phrase in followup_phrases)


def build_chat_reply(message: str, mood: str, used_memory: bool) -> str:
    msg = message.lower()

    if used_memory:
        return (
            f"Sigur — am păstrat aceeași direcție și ți-am pregătit alte recomandări pe mood-ul de {mood}."
        )

    if mood == "relax":
        return (
            "Am înțeles. Pari într-o stare mai tensionată și ți-am pregătit ceva mai calm, "
            "care să te ajute să te liniștești."
        )

    if mood == "focus":
        return (
            "Am înțeles. Pari orientat spre concentrare, așa că ți-am ales piese mai potrivite "
            "pentru studiu sau lucru."
        )

    if mood == "happy":
        return (
            "Nice — pari într-un vibe bun. Ți-am pregătit ceva mai energic și pozitiv."
        )

    if mood == "sad":
        if "imbune" in msg or "cheer" in msg or "better" in msg or "uplift" in msg:
            return (
                "Am înțeles. Te simți mai jos, dar vrei ceva care să te ridice puțin, "
                "așa că ți-am ales melodii mai accesibile și plăcute."
            )
        return (
            "Înțeleg. Pari într-o stare mai tristă și ți-am ales piese care se potrivesc "
            "mai bine cu mood-ul tău actual."
        )

    if mood == "angry":
        return (
            "Am înțeles. Pari tensionat sau nervos, așa că ți-am ales ceva mai intens."
        )

    return "Ți-am pregătit câteva recomandări pe baza mesajului tău."


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
    tracks = build_track_items(df)

    return RecommendResponse(
        mood=pred.mood,
        mode=pred.mode,
        confidence=pred.confidence,
        tracks=tracks,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    used_memory = False

    if req.session_id not in chat_memory:
        chat_memory[req.session_id] = {
            "last_mood": None,
            "last_message": None,
        }

    session = chat_memory[req.session_id]

    if is_followup_request(req.message) and session["last_mood"] is not None:
        mood = session["last_mood"]
        pred, df = rec.recommend(mood, req.n)
        used_memory = True
    else:
        pred, df = rec.recommend(req.message, req.n)
        mood = pred.mood
        session["last_mood"] = mood
        session["last_message"] = req.message

    tracks = build_track_items(df)
    reply = build_chat_reply(req.message, mood, used_memory)

    return ChatResponse(
        reply=reply,
        mood=mood,
        tracks=tracks,
    )