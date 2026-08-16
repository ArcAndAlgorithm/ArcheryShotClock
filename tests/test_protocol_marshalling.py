import unittest

from firmware.common.protocol import StateUpdateMessage, SignalEvent


class ProtocolMarshallingTests(unittest.TestCase):
    """
    Tests for the wire protocol message structures used by the C++ transport layer.
    These tests verify that the protocol messages can be serialized and match
    the expected wire format for ESP-NOW transmission.
    """

    def test_state_update_message_to_dict(self):
        msg = StateUpdateMessage(
            session_id="test-session",
            unit_id="controller-01",
            device_role="controller",
            light_state="GREEN",
            phase="SHOOTING",
            active=True,
            paused=False,
            time_remaining_ms=12500,
            arrows_shot=2,
            arrows_per_end=6,
            end_number=1,
            set_number=1,
            protocol_version=1,
        )

        data = msg.to_dict()

        self.assertEqual(data["protocol_version"], 1)
        self.assertEqual(data["session_id"], "test-session")
        self.assertEqual(data["unit_id"], "controller-01")
        self.assertEqual(data["device_role"], "controller")
        self.assertEqual(data["light_state"], "GREEN")
        self.assertEqual(data["phase"], "SHOOTING")
        self.assertTrue(data["active"])
        self.assertFalse(data["paused"])
        self.assertEqual(data["time_remaining_ms"], 12500)
        self.assertEqual(data["arrows_shot"], 2)

    def test_signal_event_to_dict(self):
        event = SignalEvent(
            session_id="test-session",
            unit_id="buzzer-01",
            event_name="SIGNAL_START",
            count=1,
            protocol_version=1,
        )

        data = event.to_dict()

        self.assertEqual(data["protocol_version"], 1)
        self.assertEqual(data["session_id"], "test-session")
        self.assertEqual(data["unit_id"], "buzzer-01")
        self.assertEqual(data["event_name"], "SIGNAL_START")
        self.assertEqual(data["count"], 1)

    def test_state_update_message_role_normalization(self):
        msg = StateUpdateMessage(
            session_id="test",
            device_role="CONTROLLER",  # uppercase
        )
        data = msg.to_dict()
        self.assertEqual(data["device_role"], "controller")  # normalized to lowercase

    def test_state_update_message_all_light_states(self):
        for light_state in ["OFF", "RED", "GREEN", "YELLOW"]:
            msg = StateUpdateMessage(light_state=light_state)
            data = msg.to_dict()
            self.assertEqual(data["light_state"], light_state)

    def test_state_update_message_all_phases(self):
        for phase in ["IDLE", "OCCUPY", "SHOOTING", "STOPPED", "PAUSED", "SCORING"]:
            msg = StateUpdateMessage(phase=phase)
            data = msg.to_dict()
            self.assertEqual(data["phase"], phase)


if __name__ == "__main__":
    unittest.main()
