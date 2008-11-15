"unit tests for testoob.collecting"
import sys
from unittest import TestCase
from testoob import collecting

class frame_code(TestCase):
    def test_frame_filename(self):
        self.assertEqual(__file__, collecting._frame_filename(sys._getframe()))

    def test_first_external_frame(self):
        # we should get our own current frame
        self.assertEqual(sys._getframe(), collecting._first_external_frame())

if __name__ == "__main__":
    import testoob
    testoob.main()