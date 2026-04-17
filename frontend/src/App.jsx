import { useEffect, useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi, I’m Feelit. Tell me how you feel and I’ll recommend music for you.",
      mood: null,
      tracks: [],
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    const generatedSessionId =
      "session_" + Math.random().toString(36).slice(2, 11);
    setSessionId(generatedSessionId);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;

    const userMessage = {
      role: "user",
      text: input,
      mood: null,
      tracks: [],
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          n: 6,
          session_id: sessionId,
        }),
      });

      const data = await res.json().catch(() => null);

      if (!res.ok || !data) {
        setError(`Backend error (${res.status})`);
        setLoading(false);
        return;
      }

      const botMessage = {
        role: "assistant",
        text: data.reply,
        mood: data.mood,
        tracks: data.tracks || [],
      };

      setMessages((prev) => [...prev, botMessage]);
      setInput("");
    } catch (e) {
      setError("Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <header style={styles.header}>
          <div style={styles.brand}>
            <span style={styles.brandIcon}>🎧</span>
            <span style={styles.brandText}>Feelit</span>
          </div>
          <div style={styles.subtitle}>
            AI chat for mood-based music recommendations
          </div>
        </header>

        <div style={styles.chatWrapper}>
          <div style={styles.chatArea}>
            {messages.map((msg, index) => (
              <div
                key={index}
                style={
                  msg.role === "user"
                    ? styles.userMessageWrapper
                    : styles.botMessageWrapper
                }
              >
                <div
                  style={
                    msg.role === "user" ? styles.userBubble : styles.botBubble
                  }
                >
                  <div style={styles.messageText}>{msg.text}</div>

                  {msg.mood && (
                    <div style={styles.moodLine}>
                      Recommended mood:{" "}
                      <span style={styles.moodChip}>
                        {msg.mood.charAt(0).toUpperCase() + msg.mood.slice(1)}
                      </span>
                    </div>
                  )}

                  {msg.tracks && msg.tracks.length > 0 && (
                    <div style={styles.trackGrid}>
                      {msg.tracks.map((track, i) => (
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
                                  if (audio._stopTimer) {
                                    clearTimeout(audio._stopTimer);
                                  }
                                  audio._stopTimer = setTimeout(() => {
                                    audio.pause();
                                    audio.currentTime = 0;
                                  }, 10000);
                                }}
                                onPause={(e) => {
                                  const audio = e.currentTarget;
                                  if (audio._stopTimer) {
                                    clearTimeout(audio._stopTimer);
                                  }
                                }}
                              />
                            ) : (
                              <div style={styles.noPreview}>
                                Preview unavailable
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div style={styles.botMessageWrapper}>
                <div style={styles.botBubble}>Thinking...</div>
              </div>
            )}

            {error && <div style={styles.error}>{error}</div>}
          </div>

          <div style={styles.inputBar}>
            <input
              style={styles.input}
              placeholder="Tell me how you feel..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend();
              }}
            />

            <button
              type="button"
              style={{
                ...styles.button,
                opacity: loading ? 0.85 : 1,
                cursor: loading ? "not-allowed" : "pointer",
              }}
              onClick={handleSend}
              disabled={loading}
            >
              Send
            </button>
          </div>
        </div>
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
    padding: "28px 28px 40px",
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

  chatWrapper: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },

  chatArea: {
    minHeight: "65vh",
    background: "rgba(17,24,39,0.45)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 20,
    padding: 18,
    boxShadow: "0 10px 30px rgba(0,0,0,0.35)",
    backdropFilter: "blur(6px)",
    overflow: "hidden",
  },

  userMessageWrapper: {
    display: "flex",
    justifyContent: "flex-end",
    marginBottom: 14,
  },

  botMessageWrapper: {
    display: "flex",
    justifyContent: "flex-start",
    marginBottom: 14,
  },

  userBubble: {
    maxWidth: "75%",
    background: "#1DB954",
    color: "white",
    borderRadius: 18,
    padding: "14px 16px",
    boxShadow: "0 8px 18px rgba(0,0,0,0.25)",
  },

  botBubble: {
    width: "100%",
    background: "rgba(2,6,23,0.65)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 18,
    padding: "16px 16px",
    boxShadow: "0 8px 18px rgba(0,0,0,0.25)",
  },

  messageText: {
    fontSize: 15,
    lineHeight: 1.5,
  },

  moodLine: {
    marginTop: 14,
    fontSize: 14,
    opacity: 0.9,
  },

  moodChip: {
    display: "inline-block",
    marginLeft: 8,
    padding: "4px 10px",
    borderRadius: 999,
    background: "rgba(29,185,84,0.18)",
    border: "1px solid rgba(29,185,84,0.35)",
    color: "#86efac",
    fontWeight: 800,
    fontSize: 13,
  },

  trackGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: 16,
    width: "100%",
    marginTop: 18,
  },

  card: {
    background: "rgba(17,24,39,0.72)",
    border: "1px solid rgba(255,255,255,0.10)",
    borderRadius: 18,
    overflow: "hidden",
    boxShadow: "0 10px 30px rgba(0,0,0,0.35)",
    transition: "all 0.2s ease",
  },

  imageWrapper: {
    width: "100%",
    height: 190,
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
    padding: 16,
  },

  trackName: {
    fontWeight: 900,
    fontSize: 17,
    lineHeight: 1.25,
    marginBottom: 6,
  },

  artistName: {
    opacity: 0.78,
    fontSize: 14,
    marginBottom: 12,
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
    textDecoration: "none",
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

  inputBar: {
    display: "flex",
    gap: 12,
    alignItems: "center",
  },

  input: {
    flex: 1,
    padding: "15px 16px",
    borderRadius: 14,
    border: "1px solid rgba(255,255,255,0.12)",
    background: "rgba(2,6,23,0.55)",
    color: "white",
    fontSize: 16,
    outline: "none",
  },

  button: {
    padding: "15px 22px",
    minWidth: 120,
    borderRadius: 14,
    border: "1px solid rgba(255,255,255,0.18)",
    background: "#1DB954",
    color: "white",
    fontWeight: 800,
  },

  error: {
    marginTop: 12,
    padding: "12px 14px",
    borderRadius: 12,
    background: "rgba(239,68,68,0.12)",
    border: "1px solid rgba(239,68,68,0.25)",
    color: "#fecaca",
  },
};

export default App;