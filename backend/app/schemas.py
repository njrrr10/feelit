from __future__ import annotations

from pydantic import BaseModel, Field


class MoodRequest(BaseModel):
    text: str = Field(..., min_length=1, description="User input text (RO/EN).")


class MoodResponse(BaseModel):
    mood: str
    mode: str
    confidence: float


class RecommendRequest(BaseModel):
    text: str = Field(..., min_length=1)
    n: int = Field(10, ge=1, le=50)


class TrackItem(BaseModel):
    spotify_id: str
    artist: str
    name: str
    popularity: float
    source_playlist: str
    spotify_url: str | None = None
    preview_url: str | None = None
    image_url: str | None = None


class RecommendResponse(BaseModel):
    mood: str
    mode: str
    confidence: float
    tracks: list[TrackItem]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    n: int = Field(5, ge=1, le=20)
    session_id: str = Field(..., min_length=1, max_length=100)


class ChatResponse(BaseModel):
    reply: str
    mood: str
    tracks: list[TrackItem]