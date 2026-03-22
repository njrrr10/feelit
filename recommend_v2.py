from __future__ import annotations

from pathlib import Path
import pandas as pd

from mood_from_text import detect_mood


def main() -> None:
    data_path = Path("mood_tracks_v2.csv")
    if not data_path.exists():
        raise FileNotFoundError("Nu găsesc mood_tracks_v2.csv.")

    df = pd.read_csv(data_path)
    df["mood"] = df["mood"].astype(str).str.lower()
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)

    while True:
        text = input("\nScrie cum te simti / ce vrei (ENTER ca sa iesi): ").strip()
        if not text:
            break

        mood = detect_mood(text)
        print(f"\n➡️ Detected mood: {mood}")

        subset = df[df["mood"] == mood].copy()
        if subset.empty:
            print("⚠️ Nu am piese pentru mood-ul ăsta.")
            continue

        # luăm top 100 ca “pool”, apoi alegem 10 random ca să varieze
        pool = subset.sort_values("popularity", ascending=False).head(100)
        recs = pool.sample(n=min(10, len(pool)), random_state=None)

        print("\n🎵 Recomandari (random din top 100):")
        for i, row in enumerate(recs.itertuples(index=False), start=1):
            print(f"{i}. {row.artist} – {row.name} | popularity={row.popularity}")


if __name__ == "__main__":
    main()