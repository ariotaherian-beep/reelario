import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from engine import inspect_video

class TestEngine(unittest.TestCase):
    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            inspect_video("/nonexistent/reelario.mp4")

    @patch("engine.run_json")
    def test_metadata(self, probe):
        probe.return_value = {"format": {"duration": "2.5"}, "streams": [{"codec_type": "video", "width": 1920, "height": 1080}, {"codec_type": "audio", "channels": 2}]}
        with TemporaryDirectory() as folder:
            file = Path(folder) / "clip.mp4"
            file.write_bytes(b"dummy")
            info = inspect_video(file)
        self.assertEqual(info["duration_seconds"], 2.5)
        self.assertEqual(info["video"][0]["width"], 1920)
        self.assertEqual(info["audio"][0]["channels"], 2)

if __name__ == "__main__":
    unittest.main()
