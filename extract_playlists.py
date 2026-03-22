from __future__ import annotations

from dotenv import load_dotenv
import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def main() -> None:
    load_dotenv()

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-read-private playlist-read-collaborative",
            cache_path=".cache"
        )
    )

    print("=== YOUR PLAYLISTS ===")
    playlists = sp.current_user_playlists(limit=50)

    all_tracks = []
    seen_ids = set()

    for playlist in playlists["items"]:
        playlist_name = playlist["name"]
        playlist_id = playlist["id"]

        print(f"\n📂 Extracting from: {playlist_name}")

        results = sp.playlist_tracks(playlist_id)

        while results:
            for item in results["items"]:
                track = item.get("track")
                if not track:
                    continue

                track_id = track["id"]
                if track_id in seen_ids:
                    continue

                seen_ids.add(track_id)

                row = {
                    "spotify_id": track_id,
                    "artist": track["artists"][0]["name"],
                    "name": track["name"],
                    "popularity": track.get("popularity", 0),
                    "duration_ms": track.get("duration_ms", 0),
                    "explicit": track.get("explicit", False),
                    "source_playlist": playlist_name
                }

                all_tracks.append(row)

            if results["next"]:
                results = sp.next(results)
            else:
                break

    # Save CSV
    out_file = "big_dataset.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "spotify_id",
                "artist",
                "name",
                "popularity",
                "duration_ms",
                "explicit",
                "source_playlist"
            ],
        )
        writer.writeheader()
        writer.writerows(all_tracks)

    print(f"\n✅ Extracted {len(all_tracks)} unique tracks")
    print(f"💾 Saved to {out_file}")


if __name__ == "__main__":
    main()