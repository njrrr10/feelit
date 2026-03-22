from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd


def load_model(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def score_track(row: pd.Series, mood: str) -> float:
    """
    Scor simplu pe baza metadata (fără audio_features).
    Îl rafinăm după ce avem mai multe date/feedback.
    """
    popularity = float(row.get("popularity", 0) or 0)
    duration_ms = float(row.get("duration_ms", 0) or 0)
    explicit = bool(row.get("explicit", False))

    # Normalizări simple
    pop = popularity / 100.0                 # 0..1
    dur = max(0.0, min(duration_ms / 300000.0, 1.0))  # 0..1 (cap la 5 min)

    # Heuristici (foarte simple, dar prezentabile)
    if mood == "relax":
        # Preferăm non-explicit + durată medie + popularitate moderată
        return (0.6 * (1.0 - pop)) + (0.3 * (1.0 - dur)) + (0.1 * (0.0 if explicit else 1.0))

    if mood == "focus":
        # Preferăm non-explicit + durată mai mare (ambient/lofi) + popularitate mai mică
        return (0.5 * (1.0 - pop)) + (0.4 * dur) + (0.1 * (0.0 if explicit else 1.0))

    if mood == "happy":
        # Preferăm popularitate mai mare (upbeat mainstream) + durată medie
        return (0.8 * pop) + (0.2 * (1.0 - abs(dur - 0.6)))

    if mood == "sad":
        # Popularitate medie + durată mai mare
        return (0.4 * (1.0 - abs(pop - 0.5))) + (0.6 * dur)

    if mood == "angry":
        # Popularitate mai mare + explicit permis
        return (0.7 * pop) + (0.3 * (1.0 if explicit else 0.6))

    # fallback
    return pop


def main() -> None:
    model_path = Path("mood_model.pkl")
    csv_path = Path("tracks_metadata.csv")

    if not model_path.exists():
        raise FileNotFoundError("Nu găsesc mood_model.pkl. Rulează întâi: python nlp_train.py")
    if not csv_path.exists():
        raise FileNotFoundError("Nu găsesc tracks_metadata.csv. Rulează întâi: python spotify_test.py")

    model = load_model(model_path)
    df = pd.read_csv(csv_path)

    # Curățăm minim
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce").fillna(0)
    df["explicit"] = df["explicit"].astype(bool)

    while True:
        text = input("\nScrie cum te simti / ce vrei (ENTER ca sa iesi): ").strip()
        if not text:
            break

        mood = model.predict([text])[0]
        proba = model.predict_proba([text])[0]
        classes = list(model.classes_)
        confidence = float(proba[classes.index(mood)])

        print(f"\n➡️ Detected mood: {mood} (confidence ~ {confidence:.2f})")

        # Scorăm toate melodiile și luăm top 10
        df["score"] = df.apply(lambda r: score_track(r, mood), axis=1)
        top = df.sort_values("score", ascending=False).head(10)

        print("\n🎵 Recomandari (top 10 din Liked Songs):")
        for i, row in enumerate(top.itertuples(index=False), start=1):
            print(f"{i}. {row.artist} – {row.name} | score={row.score:.3f}")


if __name__ == "__main__":
    main()