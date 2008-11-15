"unit tests for testoob.collecting"
import sys
from unittest import TestCase
from testoob import collecting
import testoob

class frame_code(TestCase):
    def test_frame_filename(self):
        if not testoob.capabilities.c.getframe:
            testoob.testing.skip("requires 'sys._getframe'")
        self.assertEqual(__file__, collecting._frame_filename(sys._getframe()))

    def test_first_external_frame(self):
        if not testoob.capabilities.c.f_back:
            testoob.testing.skip("requires 'f_back' support")
        # we should get our own current frame
        self.assertEqual(sys._getframe(), collecting._first_external_frame())

if __name__ == "__main__":
    import testoob
    testoob.main()
