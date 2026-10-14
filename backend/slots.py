"""Immutable reference time slots with editable source assignments."""
from fractions import Fraction

def make_slots(boundaries_ms, fps_num=30, fps_den=1):
    if len(boundaries_ms) < 2 or boundaries_ms[0] != 0 or any(b <= a for a,b in zip(boundaries_ms,boundaries_ms[1:])):
        raise ValueError("Boundaries must start at zero and be strictly increasing")
    fps = Fraction(fps_num, fps_den)
    def frame(ms):
        value = Fraction(ms, 1000) * fps
        return (value.numerator * 2 + value.denominator) // (2 * value.denominator)
    return [
        {"id": f"slot-{i+1:04d}", "reference_start_ms": a,
         "reference_end_ms": b, "duration_ms": b-a,
         "render_start_frame": frame(a), "render_end_frame": frame(b),
         "source_id": None, "source_in_ms": 0, "crop_mode": "center"}
        for i,(a,b) in enumerate(zip(boundaries_ms,boundaries_ms[1:]))
    ]

def assign(slots, slot_id, source_id, source_in_ms=0, crop_mode="center"):
    if source_in_ms < 0 or crop_mode not in ("center", "blur"):
        raise ValueError("Invalid source in-point or crop mode")
    for slot in slots:
        if slot["id"] == slot_id:
            slot.update(source_id=source_id, source_in_ms=source_in_ms, crop_mode=crop_mode)
            return
    raise KeyError(slot_id)

def swap_assignments(slots, first_id, second_id):
    by_id = {s["id"]: s for s in slots}
    a,b = by_id[first_id],by_id[second_id]
    fields = ("source_id", "source_in_ms", "crop_mode")
    previous = {field:a[field] for field in fields}
    for field in fields:
        a[field] = b[field]
        b[field] = previous[field]
