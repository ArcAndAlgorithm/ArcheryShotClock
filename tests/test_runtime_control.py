import unittest

from firmware.common.controller_runtime import ControllerRuntime
from firmware.common.display_runtime import DisplayRuntime
from firmware.common.buzzer_runtime import BuzzerRuntime


class ControllerRuntimeTests(unittest.TestCase):
    def test_start_and_tick_updates_state(self):
        runtime = ControllerRuntime()

        runtime.start()
        runtime.tick(1.0)

        payload = runtime.build_state_update()
        self.assertTrue(payload["active"])
        self.assertEqual(payload["phase"], "OCCUPY")
        self.assertEqual(payload["light_state"], "YELLOW")
        self.assertLess(payload["time_remaining_ms"], 30000)

    def test_emergency_stop_halts_clock(self):
        runtime = ControllerRuntime()
        runtime.start()

        runtime.trigger_emergency_stop()
        payload = runtime.build_state_update()

        self.assertFalse(payload["active"])
        self.assertEqual(payload["light_state"], "RED")
        self.assertEqual(payload["phase"], "STOPPED")

    def test_display_runtime_uses_controller_state(self):
        runtime = ControllerRuntime()
        runtime.start()
        display = DisplayRuntime()

        display.consume_state(runtime.build_state_update())

        self.assertEqual(display.state["light"], "GREEN")
        self.assertTrue(display.state["active"])

    def test_buzzer_runtime_emits_expected_signal(self):
        buzzer = BuzzerRuntime()

        message = buzzer.play_signal("SIGNAL_START", 1)

        self.assertEqual(message["event_name"], "SIGNAL_START")
        self.assertEqual(message["count"], 1)


if __name__ == "__main__":
    unittest.main()
