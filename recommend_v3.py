from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd

from mood_from_text import detect_mood


def load_model(path: Path):
    with path.open("rb") as f:
        return pickle.load(f)


def predict_mood_with_conf(model, text: str) -> tuple[str, float]:
    pred = model.predict([text])[0]
    proba = model.predict_proba([text])[0]
    classes = list(model.classes_)
    conf = float(proba[classes.index(pred)])
    return pred, conf


def main() -> None:
    model_path = Path("text_mood_model.pkl")
    data_path = Path("mood_tracks_v2.csv")

    if not model_path.exists():
        raise FileNotFoundError("Nu găsesc text_mood_model.pkl. Rulează: python train_text_mood_model.py")
    if not data_path.exists():
        raise FileNotFoundError("Nu găsesc mood_tracks_v2.csv. Rulează extract + build.")

    model = load_model(model_path)
    df = pd.read_csv(data_path)

    df["mood"] = df["mood"].astype(str).str.lower()
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)

    # ca să varieze recomandările: luăm random dintr-un "pool" de top
    POOL_SIZE = 120
    N_RECS = 10

    # dacă modelul e nesigur, mergem pe reguli
    CONF_THRESHOLD = 0.30

    while True:
        text = input("\nScrie cum te simti / ce vrei (ENTER ca sa iesi): ").strip()
        if not text:
            break

        ml_mood, conf = predict_mood_with_conf(model, text)
        rule_mood = detect_mood(text)

        if conf >= CONF_THRESHOLD:
            mood = ml_mood
            mode = f"ML (conf {conf:.2f})"
        else:
            mood = rule_mood
            mode = f"RULES (ML conf {conf:.2f} < {CONF_THRESHOLD})"

        print(f"\n➡️ Mood: {mood} | mode={mode}")

        subset = df[df["mood"] == mood].copy()
        if subset.empty:
            print("⚠️ Nu am piese pentru mood-ul ăsta.")
            continue

        pool = subset.sort_values("popularity", ascending=False).head(POOL_SIZE)
        recs = pool.sample(n=min(N_RECS, len(pool)), random_state=None)

        print("\n🎵 Recomandari:")
        for i, row in enumerate(recs.itertuples(index=False), start=1):
            print(f"{i}. {row.artist} – {row.name} | popularity={row.popularity} | src={row.source_playlist}")


if __name__ == "__main__":
    main()