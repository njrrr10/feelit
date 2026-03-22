from __future__ import annotations

from dotenv import load_dotenv
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth


TARGET_PREFIX = "LICENTA_"


def main() -> None:
    load_dotenv()

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-read-private playlist-read-collaborative",
            cache_path=".cache"
        )
    )

    playlists = sp.current_user_playlists(limit=50)

    rows = []
    seen = set()

    for pl in playlists["items"]:
        name = pl["name"]
        if not name.upper().startswith(TARGET_PREFIX):
            continue

        mood = name.upper().replace(TARGET_PREFIX, "").strip().lower()
        pl_id = pl["id"]
        print(f"Extracting {name} -> mood={mood}")

        results = sp.playlist_tracks(pl_id)
        while results:
            for item in results["items"]:
                track = item.get("track")
                if not track or not track.get("id"):
                    continue

                tid = track["id"]
                key = (tid, mood)
                if key in seen:
                    continue
                seen.add(key)

                rows.append({
                    "spotify_id": tid,
                    "artist": track["artists"][0]["name"],
                    "name": track["name"],
                    "popularity": track.get("popularity", 0),
                    "duration_ms": track.get("duration_ms", 0),
                    "explicit": track.get("explicit", False),
                    "source_playlist": name,
                    "mood": mood,
                })

            if results.get("next"):
                results = sp.next(results)
            else:
                break

    extra = pd.DataFrame(rows)
    extra.to_csv("extra_mood_tracks.csv", index=False, encoding="utf-8")
    print(f"✅ Saved extra_mood_tracks.csv with {len(extra)} rows")

    # merge cu mood_tracks.csv existent
    base = pd.read_csv("mood_tracks.csv")
    combined = pd.concat([base, extra], ignore_index=True)

    # scăpăm de duplicate (aceeași piesă + același mood)
    combined = combined.drop_duplicates(subset=["spotify_id", "mood"])

    combined.to_csv("mood_tracks_v2.csv", index=False, encoding="utf-8")
    print(f"✅ Saved mood_tracks_v2.csv with {len(combined)} rows")


if __name__ == "__main__":
    main()