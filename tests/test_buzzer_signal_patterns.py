import unittest

from firmware.common.protocol import SignalEvent
from firmware.common.buzzer_runtime import BuzzerRuntime


class BuzzerSignalPatternsTests(unittest.TestCase):
    """
    Tests for buzzer signal pattern generation per Article 11.3.
    Validates that each signal event maps to the correct beep sequence.
    """

    def setUp(self):
        self.buzzer = BuzzerRuntime()

    def test_signal_occupy_line_emits_two_beeps(self):
        """Article 11.3.1: Occupy line signal is 2 beeps."""
        result = self.buzzer.play_signal("SIGNAL_OCCUPY_LINE")
        self.assertEqual(result["event_name"], "SIGNAL_OCCUPY_LINE")
        self.assertEqual(result["count"], 2)

    def test_signal_start_emits_one_beep(self):
        """Article 11.3.1: Start shooting signal is 1 beep."""
        result = self.buzzer.play_signal("SIGNAL_START")
        self.assertEqual(result["event_name"], "SIGNAL_START")
        self.assertEqual(result["count"], 1)

    def test_signal_warning_emits_one_beep(self):
        """30s warning: 1 beep."""
        result = self.buzzer.play_signal("SIGNAL_WARNING")
        self.assertEqual(result["event_name"], "SIGNAL_WARNING")
        self.assertEqual(result["count"], 1)

    def test_signal_stop_emits_two_beeps(self):
        """Article 11.3.1: Stop signal is 2 beeps."""
        result = self.buzzer.play_signal("SIGNAL_STOP")
        self.assertEqual(result["event_name"], "SIGNAL_STOP")
        self.assertEqual(result["count"], 2)

    def test_signal_scoring_emits_three_beeps(self):
        """Article 11.3.1: Scoring may begin signal is 3 beeps."""
        result = self.buzzer.play_signal("SIGNAL_SCORING")
        self.assertEqual(result["event_name"], "SIGNAL_SCORING")
        self.assertEqual(result["count"], 3)

    def test_signal_emergency_emits_five_beeps(self):
        """Article 11.3.3: Emergency stop signal is 5+ beeps."""
        result = self.buzzer.play_signal("SIGNAL_EMERGENCY")
        self.assertEqual(result["event_name"], "SIGNAL_EMERGENCY")
        self.assertGreaterEqual(result["count"], 5)

    def test_signal_resume_emits_one_beep(self):
        """Resume after suspension: 1 beep."""
        result = self.buzzer.play_signal("SIGNAL_RESUME")
        self.assertEqual(result["event_name"], "SIGNAL_RESUME")
        self.assertEqual(result["count"], 1)

    def test_signal_event_serialization(self):
        """Signal events can be serialized for ESP-NOW transmission."""
        event = SignalEvent(
            session_id="test-session",
            unit_id="buzzer-01",
            event_name="SIGNAL_START",
            count=1,
            protocol_version=1,
        )

        data = event.to_dict()

        self.assertEqual(data["session_id"], "test-session")
        self.assertEqual(data["unit_id"], "buzzer-01")
        self.assertEqual(data["event_name"], "SIGNAL_START")
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["protocol_version"], 1)

    def test_all_defined_signals(self):
        """Test that all defined signals in BuzzerRuntime have a count."""
        for signal_name in BuzzerRuntime.SIGNALS.keys():
            result = self.buzzer.play_signal(signal_name)
            self.assertIn("count", result)
            self.assertGreater(result["count"], 0)


if __name__ == "__main__":
    unittest.main()
