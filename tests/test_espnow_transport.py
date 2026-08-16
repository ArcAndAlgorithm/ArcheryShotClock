import unittest

from firmware.common.espnow_transport import EspNowTransport


class EspNowTransportTests(unittest.TestCase):
    def test_send_state_packet_includes_protocol_version(self):
        transport = EspNowTransport()

        packet = transport.send_state("match-01", "controller-01", {"phase": "SHOOTING", "light_state": "GREEN"})

        self.assertEqual(packet["message_type"], "STATE_UPDATE")
        self.assertEqual(packet["session_id"], "match-01")
        self.assertEqual(packet["protocol_version"], 1)

    def test_send_signal_packet_records_last_packet(self):
        transport = EspNowTransport()

        packet = transport.send_signal("match-01", "buzzer-01", {"event_name": "SIGNAL_STOP", "count": 2})

        self.assertEqual(packet["event_name"], "SIGNAL_STOP")
        self.assertEqual(transport.receive_last()["unit_id"], "buzzer-01")


if __name__ == "__main__":
    unittest.main()
