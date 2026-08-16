import unittest

from firmware.common.protocol import SignalEvent, StateUpdateMessage


class ProtocolSerializationTests(unittest.TestCase):
    def test_state_update_serializes_expected_fields(self):
        message = StateUpdateMessage(
            session_id="match-01",
            unit_id="controller-01",
            device_role="controller",
            light_state="GREEN",
            phase="SHOOTING",
            active=True,
            paused=False,
            time_remaining_ms=120000,
            arrows_shot=2,
            arrows_per_end=6,
            end_number=1,
            set_number=1,
        )

        payload = message.to_dict()

        self.assertEqual(payload["protocol_version"], 1)
        self.assertEqual(payload["session_id"], "match-01")
        self.assertEqual(payload["light_state"], "GREEN")
        self.assertEqual(payload["phase"], "SHOOTING")
        self.assertTrue(payload["active"])
        self.assertEqual(payload["time_remaining_ms"], 120000)

    def test_signal_event_serializes_expected_fields(self):
        event = SignalEvent(
            session_id="match-01",
            unit_id="buzzer-01",
            event_name="SIGNAL_START",
            count=1,
        )

        payload = event.to_dict()

        self.assertEqual(payload["event_name"], "SIGNAL_START")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["unit_id"], "buzzer-01")


if __name__ == "__main__":
    unittest.main()
