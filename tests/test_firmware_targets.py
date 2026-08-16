import unittest


class FirmwareTargetSkeletonTests(unittest.TestCase):
    def test_target_files_exist(self):
        import os

        self.assertTrue(os.path.exists('firmware/controller/main.c'))
        self.assertTrue(os.path.exists('firmware/display/main.c'))
        self.assertTrue(os.path.exists('firmware/buzzer/main.c'))


if __name__ == "__main__":
    unittest.main()
