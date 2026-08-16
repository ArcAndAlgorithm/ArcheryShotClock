import unittest

from firmware.common.buzzer_state import BuzzerState
from firmware.common.display_state import DisplayState


class DisplayBuzzerStateTests(unittest.TestCase):
    def test_display_state_applies_controller_update(self):
        display = DisplayState()
        display.apply_update({
            "session_id": "match-01",
            "active": True,
            "paused": False,
            "light_state": "GREEN",
            "phase": "SHOOTING",
            "time_remaining_ms": 20000,
            "arrows_shot": 3,
            "arrows_per_end": 6,
            "score_display": False,
        })

        self.assertEqual(display.session_id, "match-01")
        self.assertTrue(display.active)
        self.assertEqual(display.light, "GREEN")
        self.assertIn("SHOOTING", display.render_summary())

    def test_buzzer_state_applies_signal_event(self):
        buzzer = BuzzerState()
        buzzer.apply_event({
            "session_id": "match-01",
            "unit_id": "buzzer-01",
            "event_name": "SIGNAL_STOP",
            "count": 2,
            "active": True,
        })

        self.assertEqual(buzzer.event_name, "SIGNAL_STOP")
        self.assertEqual(buzzer.count, 2)
        self.assertTrue(buzzer.active)
        self.assertEqual(buzzer.pattern()["event_name"], "SIGNAL_STOP")


if __name__ == "__main__":
    unittest.main()
