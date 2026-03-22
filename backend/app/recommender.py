from __future__ import annotations

import os
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials


@dataclass
class PredictResult:
    mood: str
    confidence: float
    mode: str  # "ML" sau "RULES"


def _load_pickle(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)


def _predict_mood_with_conf(model: Any, text: str) -> Tuple[str, float]:
    pred = model.predict([text])[0]
    proba = model.predict_proba([text])[0]
    classes = list(model.classes_)
    conf = float(proba[classes.index(pred)])
    return str(pred), conf


def _detect_mood_rules(text: str) -> str:
    t = (text or "").lower().strip()

    if re.search(r"stres|anx|panic|calm|relax|linist|chill|obosit|tired|sleep|insom", t):
        return "relax"
    if re.search(r"trist|sad|deprim|down|plang|heartbreak|singur|melanc|breakup", t):
        return "sad"
    if re.search(r"nervos|furios|angry|rage|frustrat|hate|agresiv|descarc|pissed", t):
        return "angry"
    if re.search(r"invat|study|focus|concentr|munca|work|licenta|proiect|coding|program", t):
        return "focus"
    if re.search(r"fericit|happy|party|chef|energie|upbeat|good vibes|dance|celebr", t):
        return "happy"

    return "happy"


class Recommender:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

        load_dotenv(self.base_dir / ".env")

        self.model_path = self.base_dir / "text_mood_model.pkl"
        self.data_path = self.base_dir / "mood_tracks_v2.csv"

        if not self.model_path.exists():
            raise FileNotFoundError(f"Missing model: {self.model_path}")
        if not self.data_path.exists():
            raise FileNotFoundError(f"Missing data: {self.data_path}")

        self.model = _load_pickle(self.model_path)

        df = pd.read_csv(self.data_path)
        df["mood"] = df["mood"].astype(str).str.lower()
        df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
        self.df = df

        self.conf_threshold = 0.30
        self.pool_size = 150

        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise RuntimeError("Lipsesc SPOTIPY_CLIENT_ID / SPOTIPY_CLIENT_SECRET în .env")

        self.sp_public = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
            )
        )

    def predict(self, text: str) -> PredictResult:
        ml_mood, conf = _predict_mood_with_conf(self.model, text)

        if conf >= self.conf_threshold:
            return PredictResult(mood=ml_mood, confidence=conf, mode="ML")

        return PredictResult(
            mood=_detect_mood_rules(text),
            confidence=conf,
            mode="RULES",
        )

    def recommend(self, text: str, n: int) -> tuple[PredictResult, pd.DataFrame]:
        pred = self.predict(text)

        subset = self.df[self.df["mood"] == pred.mood].copy()
        if subset.empty:
            subset = self.df.copy()

        pool = subset.sort_values("popularity", ascending=False).head(self.pool_size)
        recs = pool.sample(n=min(n, len(pool)), random_state=None).copy()

        try:
            ids = [str(x) for x in recs["spotify_id"].tolist()]
            resp = self.sp_public.tracks(ids)
            tracks = (resp or {}).get("tracks", []) if isinstance(resp, dict) else []

            preview_map: dict[str, str | None] = {}
            url_map: dict[str, str | None] = {}
            image_map: dict[str, str | None] = {}

            for t in tracks:
                if not t:
                    continue

                tid = t.get("id")
                if not tid:
                    continue

                preview_map[tid] = t.get("preview_url")
                url_map[tid] = (t.get("external_urls") or {}).get("spotify")

                images = ((t.get("album") or {}).get("images") or [])
                if images:
                    image_map[tid] = images[0].get("url")
                else:
                    image_map[tid] = None

            recs["preview_url"] = recs["spotify_id"].astype(str).map(preview_map)
            recs["spotify_url"] = recs["spotify_id"].astype(str).map(url_map)
            recs["image_url"] = recs["spotify_id"].astype(str).map(image_map)

        except Exception:
            recs["preview_url"] = None
            recs["spotify_url"] = recs["spotify_id"].astype(str).apply(
                lambda tid: f"https://open.spotify.com/track/{tid}"
            )
            recs["image_url"] = None

        recs["spotify_url"] = recs.apply(
            lambda row: row["spotify_url"]
            if isinstance(row["spotify_url"], str) and row["spotify_url"]
            else f"https://open.spotify.com/track/{row['spotify_id']}",
            axis=1,
        )

        return pred, recs