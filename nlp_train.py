from __future__ import annotations

import pickle
from pathlib import Path
from typing import List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def build_toy_dataset() -> tuple[List[str], List[str]]:
    """
    Creează un dataset mic de pornire.
    Clase: relax, focus, happy, sad, angry
    """
    texts = [
        # RELAX
        "sunt stresat si vreau sa ma linistesc",
        "ma simt obosit, vreau ceva calm",
        "am anxietate, vreau muzica linistitoare",

        # FOCUS
        "vreau sa invat si sa ma concentrez",
        "am de scris la licenta, vreau ceva de focus",
        "vreau muzica pentru munca, fara distractii",

        # HAPPY
        "sunt fericit, am energie, vreau ceva upbeat",
        "azi e o zi buna, vreau muzica de party",
        "sunt entuziasmat, vreau ceva energic",

        # SAD
        "sunt trist si vreau ceva melancholic",
        "m-a lasat cineva, sunt down",
        "nu am chef de nimic, sunt deprimat",

        # ANGRY
        "sunt nervos, vreau sa ma descarc",
        "m-a enervat rau ceva, vreau muzica agresiva",
        "sunt frustrat si tensionat",
    ]

    labels = [
        "relax", "relax", "relax",
        "focus", "focus", "focus",
        "happy", "happy", "happy",
        "sad", "sad", "sad",
        "angry", "angry", "angry",
    ]

    return texts, labels


def train_model(texts: List[str], labels: List[str]) -> Pipeline:
    """
    Antrenează model NLP: TF-IDF + Logistic Regression
    """

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.4,      # 🔥 modificat la 0.4 ca sa nu mai dea eroare
        random_state=42,
        stratify=labels
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=2000)),
    ])

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    print("\n=== EVALUATION ===")
    print(classification_report(y_test, y_pred))

    return model


def save_model(model: Pipeline, path: Path) -> None:
    with path.open("wb") as f:
        pickle.dump(model, f)


def main() -> None:
    texts, labels = build_toy_dataset()

    model = train_model(texts, labels)

    model_path = Path("mood_model.pkl")
    save_model(model, model_path)

    print(f"\n✅ Model saved to: {model_path.resolve()}")

    # Demo interactiva
    while True:
        user_input = input("\nScrie cum te simti (ENTER pentru exit): ").strip()
        if user_input == "":
            break

        prediction = model.predict([user_input])[0]
        probabilities = model.predict_proba([user_input])[0]
        classes = list(model.classes_)
        confidence = probabilities[classes.index(prediction)]

        print(f"➡️ Mood: {prediction} (confidence ~ {confidence:.2f})")


if __name__ == "__main__":
    main()