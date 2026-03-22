from __future__ import annotations

from dotenv import load_dotenv
import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException


def main() -> None:
    load_dotenv()

    sp: spotipy.Spotify = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="user-library-read",
            cache_path=".cache",
        )
    )

    results: dict = sp.current_user_saved_tracks(limit=50)  # pune 50 ca să ai date mai multe

    rows: list[dict] = []

    print("=== SAVED TRACKS ===")
    for idx, item in enumerate(results["items"], start=1):
        track: dict = item["track"]
        spotify_id: str = track["id"]
        artist: str = track["artists"][0]["name"]
        name: str = track["name"]

        # metadata extra (merge, nu cere audio_features)
        t: dict = sp.track(spotify_id)

        row = {
            "spotify_id": spotify_id,
            "artist": artist,
            "name": name,
            "popularity": t.get("popularity"),
            "duration_ms": t.get("duration_ms"),
            "explicit": t.get("explicit"),
        }
        rows.append(row)

        print(f"{idx}. {artist} – {name}")

    # scriem CSV
    out_path = "tracks_metadata.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["spotify_id", "artist", "name", "popularity", "duration_ms", "explicit"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Saved {len(rows)} rows to {out_path}")

    # (optional) arătăm că audio_features e blocat, dar nu ne mai interesează
    print("\n=== AUDIO FEATURES (optional) ===")
    try:
        ids = [r["spotify_id"] for r in rows[:5]]
        _ = sp.audio_features(ids)
        print("Audio features worked (unexpected).")
    except SpotifyException:
        print("Audio features blocked (HTTP 403). Using metadata-only pipeline.")


if __name__ == "__main__":
    main()