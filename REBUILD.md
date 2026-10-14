# Reelario Cloud Video Engine — rebuild

Free-tier-first MVP. The existing main branch is preserved until review.

## Phase 1
Run `python backend/main.py input.mp4 --output output` to create a JSON metadata manifest and a thumbnail. Requires Python and FFmpeg/ffprobe.

Cloud test: Actions → Video Ingestion → Run workflow, supply a **public non-sensitive** direct HTTPS MP4 under 50 MiB, then download the artifact.

Do not upload private footage to this public repository or pass private signed URLs as workflow inputs.

## Planned
Shot detection, rhythm analysis, camera motion estimation, timeline JSON, and rendering. GitHub Actions free minutes and artifact storage are limited.
