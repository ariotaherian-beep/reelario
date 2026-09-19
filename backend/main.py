from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import shutil
import uuid
import json

ROOT = Path(__file__).resolve().parent.parent
STORAGE = ROOT / "storage"
UPLOADS = STORAGE / "uploads"
PROJECTS = STORAGE / "projects"
PREVIEWS = STORAGE / "previews"

UPLOADS.mkdir(parents=True, exist_ok=True)
PREVIEWS.mkdir(parents=True, exist_ok=True)
PROJECTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Reelario", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Track(BaseModel):
    id: str
    artist: str = ""
    title: str = ""
    source: str = "upload"
    audio_path: Optional[str] = None
    artwork_path: Optional[str] = None
    clip_duration: float = 6.0
    start_point: float = 0.0
    status: str = "empty"

class Project(BaseModel):
    id: str
    name: str = "New Reel"
    format: str = "9:16"
    width: int = 1080
    height: int = 1920
    tracks: list[Track] = []

@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "Reelario",
        "version": "0.1.0"
    }

@app.post("/api/projects")
def create_project(track_count: int = 3):
    if track_count < 1 or track_count > 50:
        raise HTTPException(400, "Track count must be between 1 and 50")

    project_id = uuid.uuid4().hex[:12]

    project = Project(
        id=project_id,
        tracks=[
            Track(
                id=uuid.uuid4().hex[:10],
                clip_duration=6.0
            )
            for _ in range(track_count)
        ]
    )

    path = PROJECTS / f"{project_id}.json"
    path.write_text(project.model_dump_json(indent=2))

    return project

@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    path = PROJECTS / f"{project_id}.json"

    if not path.exists():
        raise HTTPException(404, "Project not found")

    return json.loads(path.read_text())

@app.put("/api/projects/{project_id}")
def save_project(project_id: str, project: Project):
    path = PROJECTS / f"{project_id}.json"

    if project.id != project_id:
        raise HTTPException(400, "Project ID mismatch")

    path.write_text(project.model_dump_json(indent=2))
    return project

@app.post("/api/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()

    if ext not in [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"]:
        raise HTTPException(400, "Unsupported audio format")

    file_id = uuid.uuid4().hex
    destination = UPLOADS / f"{file_id}{ext}"

    with destination.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    return {
        "id": file_id,
        "filename": file.filename,
        "path": str(destination),
        "type": "audio"
    }

@app.post("/api/upload/artwork")
async def upload_artwork(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()

    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(400, "Unsupported image format")

    file_id = uuid.uuid4().hex
    destination = UPLOADS / f"{file_id}{ext}"

    with destination.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    return {
        "id": file_id,
        "filename": file.filename,
        "path": str(destination),
        "url": f"/api/media/{destination.name}",
        "type": "artwork"
    }

@app.get("/api/media/{filename}")
def media(filename: str):
    path = UPLOADS / filename

    if not path.exists():
        raise HTTPException(404, "Media not found")

    return FileResponse(path)

@app.get("/api/mixario/status")
def mixario_status():
    # V1 placeholder. Reelario stays independent.
    return {
        "connected": False,
        "mode": "future_api",
        "message": "Mixario connector reserved for next stage"
    }

@app.post("/api/preview/audio")
async def create_audio_preview(file: UploadFile = File(...)):
    import subprocess

    ext = Path(file.filename or "").suffix.lower()
    if ext not in [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"]:
        raise HTTPException(400, "Unsupported audio format")

    file_id = uuid.uuid4().hex
    source = UPLOADS / f"{file_id}{ext}"
    preview = PREVIEWS / f"{file_id}_preview.mp3"

    with source.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", "0",
            "-i", str(source),
            "-t", "6",
            "-vn",
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            str(preview)
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise HTTPException(500, f"FFmpeg failed: {result.stderr[-1000:]}")

    return {
        "status": "ok",
        "duration": 6,
        "preview_url": f"/api/preview/{preview.name}"
    }

@app.get("/api/preview/{filename}")
def get_audio_preview(filename: str):
    from fastapi.responses import FileResponse

    path = PREVIEWS / filename
    if not path.exists():
        raise HTTPException(404, "Preview not found")

    return FileResponse(path, media_type="audio/mpeg")

@app.post("/api/preview/reel/{project_id}")
def create_reel_preview(project_id: str):
    import subprocess

    project_path = PROJECTS / f"{project_id}.json"
    if not project_path.exists():
        raise HTTPException(404, "Project not found")

    data = json.loads(project_path.read_text())
    tracks = data.get("tracks", [])

    if len(tracks) < 2:
        raise HTTPException(400, "At least 2 tracks are required")

    tracks = tracks[:2]
    clips = []

    for i, track in enumerate(tracks):
        audio = track.get("audio_path")
        artwork = track.get("artwork_path")

        if not audio or not Path(audio).exists():
            raise HTTPException(400, f"Track {i + 1}: audio missing")

        if not artwork or not Path(artwork).exists():
            raise HTTPException(400, f"Track {i + 1}: artwork missing")

        clip = PREVIEWS / f"{project_id}_clip_{i + 1}.mp4"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", artwork,
            "-ss", str(track.get("start_point", 0)),
            "-i", audio,
            "-t", str(track.get("clip_duration", 6)),
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "format=yuv420p",
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(clip)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(
                500,
                f"Track {i + 1} FFmpeg failed: {result.stderr[-1500:]}"
            )

        clips.append(clip)

    concat_file = PREVIEWS / f"{project_id}_concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{clip}'" for clip in clips)
    )

    output = PREVIEWS / f"{project_id}_reel_preview.mp4"

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output)
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise HTTPException(
            500,
            f"Concat failed: {result.stderr[-1500:]}"
        )

    return {
        "status": "ok",
        "tracks": 2,
        "preview_url": f"/api/preview/video/{output.name}"
    }


@app.get("/api/preview/video/{filename}")
def get_reel_preview(filename: str):
    path = PREVIEWS / filename

    if not path.exists():
        raise HTTPException(404, "Video preview not found")

    return FileResponse(path, media_type="video/mp4")
