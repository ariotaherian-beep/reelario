import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from slots import make_slots, assign, swap_assignments

class SlotsTests(unittest.TestCase):
    def test_reference_boundaries_unchanged(self):
        slots = make_slots([0, 1450, 3100, 3800])
        self.assertEqual([(s["reference_start_ms"], s["reference_end_ms"]) for s in slots], [(0,1450),(1450,3100),(3100,3800)])
        assign(slots, "slot-0001", "video-a", 3000)
        assign(slots, "slot-0002", "video-b", 500)
        swap_assignments(slots, "slot-0001", "slot-0002")
        self.assertEqual(slots[0]["source_id"], "video-b")
        self.assertEqual(slots[0]["reference_end_ms"], 1450)
        self.assertEqual(slots[1]["source_in_ms"], 3000)

    def test_invalid_boundaries(self):
        with self.assertRaises(ValueError):
            make_slots([0,100,100])

if __name__ == "__main__":
    unittest.main()
