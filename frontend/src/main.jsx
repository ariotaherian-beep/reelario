import React, {useState} from "react";
import {createRoot} from "react-dom/client";
import "./style.css";

const API = "http://127.0.0.1:8010";

function App() {
  const [count, setCount] = useState(3);
  const [project, setProject] = useState(null);
  const [message, setMessage] = useState("");

  async function createProject() {
    setMessage("Creating project...");

    try {
      const res = await fetch(
        `${API}/api/projects?track_count=${count}`,
        {method: "POST"}
      );

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();
      setProject(data);
      setMessage("");
    } catch (e) {
      setMessage("Error: " + e.message);
    }
  }

  function updateTrack(index, field, value) {
    setProject(prev => {
      const tracks = [...prev.tracks];
      tracks[index] = {...tracks[index], [field]: value};
      return {...prev, tracks};
    });
  }

  function addTrack() {
    setProject(prev => ({
      ...prev,
      tracks: [
        ...prev.tracks,
        {
          id: crypto.randomUUID(),
          artist: "",
          title: "",
          source: "upload",
          audio_path: null,
          artwork_path: null,
          clip_duration: 6,
          start_point: 0,
          status: "empty"
        }
      ]
    }));
  }

  function removeTrack(index) {
    setProject(prev => ({
      ...prev,
      tracks: prev.tracks.filter((_, i) => i !== index)
    }));
  }

  async function upload(index, type, file) {
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    setMessage(`Uploading ${file.name}...`);

    try {
      const res = await fetch(`${API}/api/upload/${type}`, {
        method: "POST",
        body: form
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();

      if (type === "audio") {
        updateTrack(index, "audio_path", data.path);
        updateTrack(index, "status", "audio ready");
      } else {
        updateTrack(index, "artwork_path", data.path);
      }

      setMessage("✓ Uploaded");
      setTimeout(() => setMessage(""), 1200);
    } catch (e) {
      setMessage("Error: " + e.message);
    }
  }

  async function saveProject() {
    try {
      setMessage("Saving...");

      const res = await fetch(`${API}/api/projects/${project.id}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(project)
      });

      if (!res.ok) throw new Error(await res.text());

      setMessage("✓ Project saved");
      setTimeout(() => setMessage(""), 1200);
    } catch (e) {
      setMessage("Error: " + e.message);
    }
  }

  const totalDuration =
    project?.tracks.reduce(
      (sum, track) => sum + Number(track.clip_duration || 0),
      0
    ) || 0;

  if (!project) {
    return (
      <main className="welcome">
        <div className="brand">REELARIO</div>
        <h1>Create a New Reel</h1>
        <p>
          Build a reel from any number of tracks.
          Audio can be uploaded now and connected to Mixario later.
        </p>

        <div className="createCard">
          <label>NUMBER OF TRACKS</label>

          <div className="counter">
            <button
              onClick={() => setCount(Math.max(1, count - 1))}
            >
              −
            </button>

            <strong>{count}</strong>

            <button
              onClick={() => setCount(Math.min(50, count + 1))}
            >
              +
            </button>
          </div>

          <button className="primary" onClick={createProject}>
            Create Reel
          </button>
        </div>

        {message && <div className="message">{message}</div>}
      </main>
    );
  }

  return (
    <main>
      <header>
        <div>
          <div className="brand">REELARIO</div>
          <h1>{project.name}</h1>
        </div>

        <div className="headerStats">
          <span>{project.tracks.length} Tracks</span>
          <span>{totalDuration.toFixed(1)} sec</span>
          <span>9:16</span>
        </div>
      </header>

      <section className="toolbar">
        <button onClick={addTrack}>+ Add Track</button>
        <button onClick={saveProject}>Save Project</button>
        <button className="primary" disabled>
          Preview Reel — Next Stage
        </button>
      </section>

      <section className="tracks">
        {project.tracks.map((track, index) => (
          <article className="trackCard" key={track.id}>
            <div className="trackNumber">
              {String(index + 1).padStart(2, "0")}
            </div>

            <div className="trackContent">
              <div className="trackHead">
                <h2>Track {index + 1}</h2>

                {project.tracks.length > 1 && (
                  <button
                    className="danger"
                    onClick={() => removeTrack(index)}
                  >
                    Remove
                  </button>
                )}
              </div>

              <div className="sourceTabs">
                <button
                  className={track.source === "mixario" ? "selected" : ""}
                  onClick={() =>
                    updateTrack(index, "source", "mixario")
                  }
                >
                  Search Mixario
                </button>

                <button
                  className={track.source === "upload" ? "selected" : ""}
                  onClick={() =>
                    updateTrack(index, "source", "upload")
                  }
                >
                  Upload Audio
                </button>
              </div>

              {track.source === "mixario" ? (
                <div className="grid">
                  <label>
                    Artist
                    <input
                      value={track.artist}
                      onChange={e =>
                        updateTrack(index, "artist", e.target.value)
                      }
                      placeholder="Artist name"
                    />
                  </label>

                  <label>
                    Track
                    <input
                      value={track.title}
                      onChange={e =>
                        updateTrack(index, "title", e.target.value)
                      }
                      placeholder="Track title"
                    />
                  </label>

                  <button className="find" disabled>
                    Find Track — Next Stage
                  </button>
                </div>
              ) : (
                <label className="uploadBox">
                  <strong>
                    {track.audio_path
                      ? "✓ Audio Ready"
                      : "Upload MP3 / WAV / FLAC"}
                  </strong>

                  <small>
                    {track.audio_path || "Choose an audio file"}
                  </small>

                  <input
                    type="file"
                    accept="audio/*"
                    onChange={e =>
                      upload(index, "audio", e.target.files?.[0])
                    }
                  />
                </label>
              )}

              <div className="settings">
                <label>
                  Artwork
                  <input
                    type="file"
                    accept="image/*"
                    onChange={e =>
                      upload(index, "artwork", e.target.files?.[0])
                    }
                  />
                </label>

                <label>
                  Clip Duration
                  <div className="numberInput">
                    <input
                      type="number"
                      min="1"
                      max="60"
                      step="0.5"
                      value={track.clip_duration}
                      onChange={e =>
                        updateTrack(
                          index,
                          "clip_duration",
                          Number(e.target.value)
                        )
                      }
                    />
                    <span>sec</span>
                  </div>
                </label>

                <label>
                  Start Point
                  <div className="numberInput">
                    <input
                      type="number"
                      min="0"
                      step="0.5"
                      value={track.start_point}
                      onChange={e =>
                        updateTrack(
                          index,
                          "start_point",
                          Number(e.target.value)
                        )
                      }
                    />
                    <span>sec</span>
                  </div>
                </label>
              </div>

              <div className="status">
                {track.status === "audio ready"
                  ? "✓ AUDIO READY"
                  : "○ WAITING FOR AUDIO"}
              </div>
            </div>
          </article>
        ))}
      </section>

      <footer>
        <div>
          <strong>Total Reel Duration</strong>
          <span>{totalDuration.toFixed(1)} seconds</span>
        </div>

        <button className="primary" onClick={saveProject}>
          Save Project
        </button>
      </footer>

      {message && <div className="floatingMessage">{message}</div>}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
