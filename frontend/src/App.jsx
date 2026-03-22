import { useState } from "react";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRecommend = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, n: 12 }),
      });

      const data = await res.json().catch(() => null);

      if (!res.ok || !data) {
        setError(`Backend error (${res.status})`);
        return;
      }

      setResult(data);
    } catch (e) {
      setError("Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const moodTitle = result?.mood
    ? result.mood.charAt(0).toUpperCase() + result.mood.slice(1)
    : "";

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <header style={styles.header}>
          <div style={styles.brand}>
            <span style={styles.brandIcon}>🎧</span>
            <span style={styles.brandText}>Feelit</span>
          </div>
          <div style={styles.subtitle}>
            Mood-based music recommendations powered by AI
          </div>
        </header>

        <div style={styles.searchRow}>
          <input
            style={styles.input}
            placeholder="Type how you feel..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleRecommend();
            }}
          />

          <button
            type="button"
            style={{
              ...styles.button,
              opacity: loading ? 0.9 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
            onClick={handleRecommend}
            disabled={loading}
          >
            {loading ? "Loading..." : "Recommend"}
          </button>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        {result && (
          <section style={styles.results}>
            <div style={styles.resultsHeader}>
              <div style={styles.resultsTitle}>
                Recommended for: <span style={styles.moodChip}>{moodTitle}</span>
              </div>
              <div style={styles.resultsMeta}>
                {result.tracks?.length || 0} tracks
              </div>
            </div>

            <div style={styles.grid}>
              {result.tracks?.map((track, i) => (
                <div
                  key={i}
                  style={styles.card}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "translateY(-4px)";
                    e.currentTarget.style.boxShadow =
                      "0 18px 40px rgba(0,0,0,0.45)";
                    e.currentTarget.style.border =
                      "1px solid rgba(29,185,84,0.35)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow =
                      "0 10px 30px rgba(0,0,0,0.35)";
                    e.currentTarget.style.border =
                      "1px solid rgba(255,255,255,0.10)";
                  }}
                >
                  <div style={styles.imageWrapper}>
                    {track.image_url ? (
                      <img
                        src={track.image_url}
                        alt={`${track.name} cover`}
                        style={styles.coverImage}
                      />
                    ) : (
                      <div style={styles.imageFallback}>♪</div>
                    )}
                  </div>

                  <div style={styles.cardBody}>
                    <div style={styles.trackName}>{track.name}</div>
                    <div style={styles.artistName}>{track.artist}</div>

                    <div style={styles.metaRow}>
                      <span style={styles.metaText}>
                        Popularity: {track.popularity}
                      </span>
                    </div>

                    <div style={styles.actionsRow}>
                      {track.spotify_url && (
                        <a
                          href={track.spotify_url}
                          target="_blank"
                          rel="noreferrer"
                          style={styles.spotifyLink}
                        >
                          Open in Spotify
                        </a>
                      )}
                    </div>

                    {track.preview_url ? (
                      <audio
                        style={styles.audio}
                        controls
                        preload="none"
                        src={track.preview_url}
                        onPlay={(e) => {
                          const audio = e.currentTarget;
                          if (audio._stopTimer) clearTimeout(audio._stopTimer);
                          audio._stopTimer = setTimeout(() => {
                            audio.pause();
                            audio.currentTime = 0;
                          }, 10000);
                        }}
                        onPause={(e) => {
                          const audio = e.currentTarget;
                          if (audio._stopTimer) clearTimeout(audio._stopTimer);
                        }}
                      />
                    ) : (
                      <div style={styles.noPreview}>Preview unavailable</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    width: "100%",
    background:
      "radial-gradient(1400px 700px at 12% 8%, #172554 0%, #020617 60%)",
    color: "white",
  },

  container: {
    width: "100%",
    maxWidth: "1400px",
    margin: "0 auto",
    padding: "36px 28px 70px",
  },

  header: {
    marginBottom: 20,
  },

  brand: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },

  brandIcon: {
    fontSize: 28,
  },

  brandText: {
    fontSize: 46,
    fontWeight: 800,
    letterSpacing: 0.5,
  },

  subtitle: {
    marginTop: 10,
    opacity: 0.75,
    fontSize: 16,
  },

  searchRow: {
    display: "flex",
    gap: 12,
    alignItems: "center",
    flexWrap: "wrap",
    marginBottom: 24,
  },

  input: {
    flex: "1 1 520px",
    minWidth: 260,
    padding: "15px 16px",
    borderRadius: 12,
    border: "1px solid rgba(255,255,255,0.12)",
    background: "rgba(2,6,23,0.55)",
    color: "white",
    fontSize: 16,
    outline: "none",
  },

  button: {
    padding: "15px 20px",
    minWidth: 150,
    borderRadius: 12,
    border: "1px solid rgba(255,255,255,0.18)",
    background: "#1DB954",
    color: "white",
    fontWeight: 800,
  },

  error: {
    marginBottom: 18,
    padding: "12px 14px",
    borderRadius: 12,
    background: "rgba(239,68,68,0.12)",
    border: "1px solid rgba(239,68,68,0.25)",
    color: "#fecaca",
  },

  results: {
    marginTop: 20,
  },

  resultsHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "baseline",
    gap: 12,
    flexWrap: "wrap",
    marginBottom: 16,
  },

  resultsTitle: {
    fontSize: 22,
    fontWeight: 800,
  },

  moodChip: {
    display: "inline-block",
    marginLeft: 10,
    padding: "5px 12px",
    borderRadius: 999,
    background: "rgba(29,185,84,0.16)",
    border: "1px solid rgba(29,185,84,0.35)",
    color: "#86efac",
    fontSize: 14,
    fontWeight: 800,
  },

  resultsMeta: {
    opacity: 0.65,
    fontSize: 14,
  },

  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: 18,
    width: "100%",
  },

  card: {
    background: "rgba(17,24,39,0.72)",
    border: "1px solid rgba(255,255,255,0.10)",
    borderRadius: 18,
    overflow: "hidden",
    boxShadow: "0 10px 30px rgba(0,0,0,0.35)",
    backdropFilter: "blur(6px)",
    transition: "all 0.2s ease",
  },

  imageWrapper: {
    width: "100%",
    height: 220,
    background: "rgba(255,255,255,0.04)",
  },

  coverImage: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    display: "block",
  },

  imageFallback: {
    width: "100%",
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 48,
    opacity: 0.45,
  },

  cardBody: {
    padding: 18,
  },

  trackName: {
    fontWeight: 900,
    fontSize: 18,
    lineHeight: 1.25,
    marginBottom: 6,
  },

  artistName: {
    opacity: 0.78,
    fontSize: 15,
    marginBottom: 14,
  },

  metaRow: {
    marginBottom: 10,
  },

  metaText: {
    opacity: 0.65,
    fontSize: 13,
  },

  actionsRow: {
    marginBottom: 10,
  },

  spotifyLink: {
    color: "#1DB954",
    fontWeight: 800,
    fontSize: 14,
  },

  audio: {
    width: "100%",
    marginTop: 6,
  },

  noPreview: {
    opacity: 0.6,
    fontSize: 13,
    marginTop: 6,
  },
};

export default App;