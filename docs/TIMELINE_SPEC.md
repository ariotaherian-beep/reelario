# Reelario V1 — Time-slot contract

Reference boundaries are immutable integer milliseconds. No beat snapping or timeline reordering is allowed.

A slot owns its immutable reference start/end and render frame indices. Drag-and-drop moves **assignments**, not time slots. Assignments contain source_id, source_in_ms and crop_mode (center or blur). Video-only inputs.

At output FPS, exact reference millisecond boundaries may not be representable. Frame indices are rounded from absolute boundaries (never cumulative rounded durations). UI should show discrepancies. Zero-frame slots require an explicit validation error or higher FPS; never silently drop a slot.

Source duration must cover each selected segment; reject too-short sources instead of silently looping. Render normalization, scaling, cropping and concat require re-encoding. Reference audio is copied as a timeline source and encoded as needed to fit output container; no intentional time stretching. Reference audio copyright and usage rights remain the user's responsibility.

Phase 1: metadata + slot model + tests. Scene cut detector, interactive UI and final render are pending.
