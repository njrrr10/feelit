from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


def main() -> None:
    data_path = Path("mood_tracks_v2.csv")
    if not data_path.exists():
        raise FileNotFoundError("Nu găsesc mood_tracks_v2.csv. Rulează extract_licenta_playlists.py")

    df = pd.read_csv(data_path)

    # Text pentru NLP: combinăm artist + titlu (poți extinde mai târziu cu genuri)
    df["text"] = (df["artist"].astype(str) + " " + df["name"].astype(str)).str.lower()
    df["label"] = df["mood"].astype(str).str.lower()

    # Split stratificat
    x_train, x_test, y_train, y_test = train_test_split(
        df["text"].tolist(),
        df["label"].tolist(),
        test_size=0.2,
        random_state=42,
        stratify=df["label"].tolist(),
    )

    model: Pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=4000)),
        ]
    )

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    print("\n=== EVALUATION (v2) ===")
    print(classification_report(y_test, y_pred))

    out_path = Path("mood_model_v2.pkl")
    with out_path.open("wb") as f:
        pickle.dump(model, f)

    print(f"✅ Saved model to {out_path.resolve()}")


if __name__ == "__main__":
    main()