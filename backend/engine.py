import json
import subprocess
from pathlib import Path

def run_json(args):
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)

def inspect_video(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    data = run_json(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    streams = data.get("streams", [])
    return {
        "filename": path.name,
        "duration_seconds": float(data.get("format", {}).get("duration", 0)),
        "size_bytes": path.stat().st_size,
        "video": [{k: s.get(k) for k in ("codec_name", "width", "height", "r_frame_rate", "avg_frame_rate", "pix_fmt", "rotation") if k in s} for s in streams if s.get("codec_type") == "video"],
        "audio": [{k: s.get(k) for k in ("codec_name", "sample_rate", "channels", "channel_layout") if k in s} for s in streams if s.get("codec_type") == "audio"],
    }

def make_thumbnail(source, destination, at_seconds=1):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(at_seconds), "-i", str(source), "-frames:v", "1", "-vf", "scale=480:-2", str(destination)], check=True)

def ingest(source, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = inspect_video(source)
    if manifest["video"]:
        thumb = output_dir / "thumbnail.jpg"
        make_thumbnail(source, thumb, min(1.0, max(0, manifest["duration_seconds"] / 2)))
        manifest["thumbnail"] = thumb.name
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
