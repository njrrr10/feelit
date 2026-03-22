from __future__ import annotations

from pathlib import Path
import re
import pandas as pd


def guess_mood_from_playlist(name: str) -> str | None:
    n = (name or "").lower()

    # relax / calm (PRIORITATE)
    if re.search(r"stress|relief|calm|relax|chill|sleep|meditat", n):
        return "relax"

    # focus / study
    if re.search(r"\bstudy\b|\bfocus\b|\bconcentr|lofi|deep work", n):
        return "focus"

    # sad
    if re.search(r"sad|saddest|cry|depress|heartbreak|nostalg|melanch|emotional", n):
        return "sad"

    # happy
    if re.search(r"party|happy|feel good|good vibes|hits|summer|dance|upbeat", n):
        return "happy"

    # angry
    if re.search(r"workout|gym|heavy|rage|aggressive|hard|metal|rock|trap|drill", n):
        return "angry"

    return None

def main() -> None:
    in_path = Path("big_dataset.csv")
    if not in_path.exists():
        raise FileNotFoundError("Nu găsesc big_dataset.csv. Rulează extract_playlists.py")

    df = pd.read_csv(in_path)

    # mood din numele playlistului
    df["source_playlist"] = df["source_playlist"].astype(str)
    df["mood"] = df["source_playlist"].apply(guess_mood_from_playlist)

    labeled = df.dropna(subset=["mood"]).copy()

    out_path = Path("mood_tracks.csv")
    labeled.to_csv(out_path, index=False, encoding="utf-8")

    print(f"✅ Total tracks in big_dataset: {len(df)}")
    print(f"✅ Labeled tracks (by keywords): {len(labeled)}")
    print("\nCounts per mood:")
    print(labeled["mood"].value_counts())
    print(f"\n💾 Saved to {out_path.resolve()}")


if __name__ == "__main__":
    main()