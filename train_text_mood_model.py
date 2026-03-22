from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def build_dataset() -> Tuple[List[str], List[str]]:
    """
    Dataset bilingv (RO + EN) pentru clasificarea stării (mood) din text.
    Clase: relax, focus, happy, sad, angry

    Extins cu multe exemple, în special pentru RELAX & HAPPY (care tind să fie ambigue).
    """
    data: list[tuple[str, str]] = [
        # =========================
        # RELAX (RO)
        # =========================
        ("sunt stresat si vreau sa ma linistesc", "relax"),
        ("am anxietate si vreau ceva calm", "relax"),
        ("vreau muzica chill ca sa ma relaxez", "relax"),
        ("sunt obosit si vreau sa ma relaxez", "relax"),
        ("vreau sa scap de stres", "relax"),
        ("vreau ceva linistitor pentru seara", "relax"),
        ("nu pot dormi, vreau muzica pentru somn", "relax"),
        ("am avut o zi grea, vreau ceva calm", "relax"),
        ("vreau muzica de relaxare", "relax"),
        ("vreau sa imi scada anxietatea", "relax"),
        ("sunt tensionat si vreau sa ma calmez", "relax"),
        ("simt ca imi bate inima tare, vreau sa ma linistesc", "relax"),
        ("am un atac de panica, vreau ceva calm", "relax"),
        ("ma simt agitat, vreau sa ma relaxez", "relax"),
        ("vreau muzica pentru meditat", "relax"),
        ("vreau muzica pentru respiratie si calm", "relax"),
        ("vreau ceva foarte calm, fara energie", "relax"),
        ("vreau sa adorm, pune-mi ceva linistitor", "relax"),
        ("am insomnie si vreau muzica de somn", "relax"),
        ("vreau sa imi reduc stresul", "relax"),
        ("sunt coplesit si vreau sa ma linistesc", "relax"),
        ("vreau sa imi scada tensiunea", "relax"),
        ("am emotii si vreau sa ma calmez", "relax"),
        ("vreau muzica chill pentru relaxare", "relax"),
        ("vreau ceva ambient pentru calm", "relax"),
        ("sunt anxios si vreau liniste", "relax"),
        ("ma simt nelinistit, vreau sa ma calmez", "relax"),
        ("vreau muzica de noapte, calm", "relax"),
        ("vreau sa ma destind", "relax"),
        ("vreau un vibe calm si linistit", "relax"),

        # RELAX (EN)
        ("i am stressed and i want to calm down", "relax"),
        ("i feel anxious and need something calm", "relax"),
        ("i want chill music to relax", "relax"),
        ("i am tired and i want to unwind", "relax"),
        ("i need stress relief music", "relax"),
        ("i want something soothing", "relax"),
        ("i can't sleep, i want sleep music", "relax"),
        ("i had a long day, i want to relax", "relax"),
        ("calm vibes please", "relax"),
        ("i want peaceful music", "relax"),
        ("i feel tense and i need to relax", "relax"),
        ("my anxiety is high, i need calm music", "relax"),
        ("panic attack, i need something calming", "relax"),
        ("i feel overwhelmed, i want to calm down", "relax"),
        ("i want meditation music", "relax"),
        ("i want music for breathing and relaxing", "relax"),
        ("i want very calm music", "relax"),
        ("help me fall asleep", "relax"),
        ("i have insomnia, i need sleep music", "relax"),
        ("i want to reduce stress", "relax"),
        ("i feel restless, i need to calm down", "relax"),
        ("i want ambient music for relaxing", "relax"),
        ("i want chill ambient vibes", "relax"),
        ("i feel nervous and need to calm down", "relax"),
        ("i need to unwind", "relax"),
        ("relaxing music please", "relax"),

        # =========================
        # FOCUS (RO)
        # =========================
        ("vreau sa invat", "focus"),
        ("am de scris la licenta si trebuie sa ma concentrez", "focus"),
        ("vreau muzica pentru munca", "focus"),
        ("trebuie sa ma focusez", "focus"),
        ("vreau ceva de studiu", "focus"),
        ("am nevoie de concentrare", "focus"),
        ("vreau muzica de background pentru invatat", "focus"),
        ("lucrez la proiect si vreau sa ma concentrez", "focus"),
        ("am examen si vreau muzica pentru focus", "focus"),
        ("vreau sa fiu productiv", "focus"),
        ("vreau sa invat fara distrageri", "focus"),
        ("vreau ceva pentru deep work", "focus"),
        ("am de citit si vreau sa ma concentrez", "focus"),
        ("am laborator si vreau focus", "focus"),
        ("trebuie sa rezolv probleme, vreau concentrare", "focus"),
        ("vreau muzica pentru programare", "focus"),

        # FOCUS (EN)
        ("i want to study", "focus"),
        ("i need to focus", "focus"),
        ("i need music for concentration", "focus"),
        ("i have to work and concentrate", "focus"),
        ("i'm writing my thesis, i need focus music", "focus"),
        ("i want background music for studying", "focus"),
        ("i want deep work music", "focus"),
        ("i need to be productive", "focus"),
        ("i have an exam tomorrow, i need to focus", "focus"),
        ("help me concentrate", "focus"),
        ("i want music for coding", "focus"),
        ("i need to study without distractions", "focus"),
        ("i need to focus on my project", "focus"),
        ("i want something for work", "focus"),
        ("i need to lock in and study", "focus"),

        # =========================
        # HAPPY (RO)
        # =========================
        ("sunt fericit", "happy"),
        ("am chef de party", "happy"),
        ("vreau muzica buna, vibe pozitiv", "happy"),
        ("azi e o zi super, vreau ceva upbeat", "happy"),
        ("sunt entuziasmat si plin de energie", "happy"),
        ("vreau sa dansez", "happy"),
        ("sunt in mood bun", "happy"),
        ("vreau muzica de distractie", "happy"),
        ("vreau ceva energic si pozitiv", "happy"),
        ("am chef sa ma simt bine", "happy"),
        ("vreau muzica pentru chef", "happy"),
        ("vreau vibe de vara", "happy"),
        ("vreau ceva upbeat si vesel", "happy"),
        ("am energie, vreau muzica tare", "happy"),
        ("vreau muzica pentru petrecere", "happy"),
        ("vreau sa ma distrez", "happy"),
        ("sunt super bine, vreau muzica de party", "happy"),
        ("vreau good vibes", "happy"),
        ("azi ma simt bine rau", "happy"),
        ("vreau ceva care sa ma binedispuna", "happy"),

        # HAPPY (EN)
        ("i feel happy", "happy"),
        ("i want party music", "happy"),
        ("good vibes only", "happy"),
        ("i feel excited and energetic", "happy"),
        ("i want upbeat music", "happy"),
        ("i want to dance", "happy"),
        ("i'm in a great mood", "happy"),
        ("i want fun music", "happy"),
        ("make me feel good", "happy"),
        ("i want positive vibes", "happy"),
        ("summer vibes", "happy"),
        ("i feel amazing today", "happy"),
        ("i want something cheerful", "happy"),
        ("i want feel-good music", "happy"),
        ("let's party", "happy"),
        ("i want music to celebrate", "happy"),
        ("i want a good mood playlist", "happy"),
        ("i feel great and energetic", "happy"),
        ("give me upbeat party songs", "happy"),
        ("i want happy songs", "happy"),

        # =========================
        # SAD (RO)
        # =========================
        ("sunt trist", "sad"),
        ("ma simt down", "sad"),
        ("am avut o zi proasta si vreau ceva melancolic", "sad"),
        ("sunt deprimat", "sad"),
        ("imi vine sa plang", "sad"),
        ("sunt singur si trist", "sad"),
        ("nu am chef de nimic", "sad"),
        ("ma simt gol pe dinauntru", "sad"),
        ("sunt abatut", "sad"),
        ("vreau muzica trista", "sad"),
        ("ma simt heartbroken", "sad"),
        ("m-a parasit si sunt trist", "sad"),
        ("am inima franta", "sad"),
        ("vreau melodii de plans", "sad"),
        ("vreau ceva nostalgic si trist", "sad"),
        ("ma apasa tot, sunt trist", "sad"),
        ("nu ma simt bine emotional", "sad"),
        ("vreau muzica pentru o stare proasta", "sad"),
        ("am chef de ceva melancolic", "sad"),
        ("sunt low azi", "sad"),

        # SAD (EN)
        ("i feel sad", "sad"),
        ("i feel down", "sad"),
        ("i had a bad day and want something melancholic", "sad"),
        ("i'm depressed", "sad"),
        ("i feel like crying", "sad"),
        ("i feel lonely", "sad"),
        ("i don't feel like doing anything", "sad"),
        ("i feel empty", "sad"),
        ("i feel heartbroken", "sad"),
        ("i want sad music", "sad"),
        ("i want to cry", "sad"),
        ("my heart is broken", "sad"),
        ("i feel nostalgic and sad", "sad"),
        ("i feel low today", "sad"),
        ("i want melancholic songs", "sad"),
        ("i feel emotionally drained", "sad"),
        ("i want breakup songs", "sad"),
        ("i feel miserable", "sad"),
        ("i feel really down today", "sad"),
        ("sad vibes", "sad"),

        # =========================
        # ANGRY (RO)
        # =========================
        ("sunt nervos", "angry"),
        ("sunt furios si vreau sa ma descarc", "angry"),
        ("m-a enervat rau ceva", "angry"),
        ("sunt frustrat", "angry"),
        ("vreau ceva agresiv", "angry"),
        ("vreau muzica de workout", "angry"),
        ("am chef de ceva tare", "angry"),
        ("vreau sa ma descarc pe muzica", "angry"),
        ("sunt plin de nervi", "angry"),
        ("vreau muzica intensa", "angry"),
        ("vreau muzica de sala", "angry"),
        ("sunt rage", "angry"),
        ("ma scoate din sarite", "angry"),
        ("vreau ceva hard", "angry"),
        ("vreau muzica pentru nervi", "angry"),
        ("vreau sa dau tot la sala", "angry"),
        ("sunt nervos rau", "angry"),
        ("vreau melodii agresive", "angry"),
        ("vreau sa urlu", "angry"),
        ("vreau muzica de descarcare", "angry"),

        # ANGRY (EN)
        ("i am angry", "angry"),
        ("i am furious and i need to blow off steam", "angry"),
        ("something really annoyed me", "angry"),
        ("i'm frustrated", "angry"),
        ("i want aggressive music", "angry"),
        ("i want gym music", "angry"),
        ("i want something hard and intense", "angry"),
        ("i need music to vent", "angry"),
        ("i'm full of rage", "angry"),
        ("i want intense music", "angry"),
        ("i want workout music", "angry"),
        ("i need rage music", "angry"),
        ("i feel pissed off", "angry"),
        ("i want hard music", "angry"),
        ("i want to release anger", "angry"),
        ("i want heavy music", "angry"),
        ("i feel mad", "angry"),
        ("i want aggressive songs", "angry"),
        ("i want to go hard in the gym", "angry"),
        ("angry vibes", "angry"),
    ]

    texts = [t for t, _ in data]
    labels = [y for _, y in data]
    return texts, labels


def main() -> None:
    texts, labels = build_dataset()

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    model: Pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=5000)),
        ]
    )

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    print("\n=== TEXT MOOD MODEL EVAL (RO+EN, extended) ===")
    print(classification_report(y_test, y_pred, zero_division=0))

    out_path = Path("text_mood_model.pkl")
    with out_path.open("wb") as f:
        pickle.dump(model, f)

    print(f"✅ Saved to {out_path.resolve()}")

    while True:
        s = input("\nText (ENTER exit): ").strip()
        if not s:
            break

        pred = model.predict([s])[0]
        proba = model.predict_proba([s])[0]
        classes = list(model.classes_)
        conf = float(proba[classes.index(pred)])

        print(f"➡️ {pred} (conf ~ {conf:.2f})")


if __name__ == "__main__":
    main()