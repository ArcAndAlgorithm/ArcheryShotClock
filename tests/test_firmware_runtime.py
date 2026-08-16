import unittest

from firmware.common.firmware_runtime import FirmwareRuntime


class FirmwareRuntimeTests(unittest.TestCase):
    def test_controller_tick_publishes_state_to_display(self):
        runtime = FirmwareRuntime()
        runtime.start_match()
        runtime.tick(1.0)

        self.assertTrue(runtime.controller.active)
        self.assertEqual(runtime.display.phase, "OCCUPY")
        self.assertLess(runtime.display.time_remaining_ms, 30000)

    def test_emergency_stop_publishes_red_state(self):
        runtime = FirmwareRuntime()
        runtime.start_match()
        runtime.trigger_emergency()

        self.assertFalse(runtime.controller.active)
        self.assertEqual(runtime.display.light, "RED")


if __name__ == "__main__":
    unittest.main()
